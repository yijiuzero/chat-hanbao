# -*- coding: utf-8 -*-
"""ReMe-backed memory manager for agents.

The public class and registry key keep the historical ``ReMeLight`` naming so
existing agent configs continue to work, but the implementation delegates to
ReMe's application/job framework.
"""

import asyncio
import base64
import datetime
import hashlib
import logging
import os
import re
from typing import Any, TYPE_CHECKING

from agentscope.message import Msg, TextBlock
from agentscope.message import ToolResultState
from agentscope.tool import ToolChunk

from .base_memory_manager import BaseMemoryManager, memory_registry
from .memory_audit import MemoryAuditor  # [hanbao modification] req ⑤/②
from .prompts import build_memory_guidance_prompt
from .reme_config import get_reme_app_config
from ..model_factory import create_model_and_formatter
from ...app.inbox_store import append_event as append_inbox_event
from ...config import load_config
from ...config.config import load_agent_config, AgentProfileConfig

if TYPE_CHECKING:
    from reme import ReMe
    from reme.application import Response

logger = logging.getLogger(__name__)

os.environ.setdefault("REME_DISABLE_LOGURU", "true")

NO_MEMORY_RESULTS = "(no memory results)"
INBOX_RESULT_JOB_NAMES = {"auto_memory", "auto_dream", "auto_resource"}
INBOX_RESULT_HOOK_KEY = "hanbao_memory_result_hook"
INBOX_EMITTED_METADATA_KEY = "_hanbao_inbox_emitted"
MAX_INBOX_BODY_CHARS = 4000
_REME_SESSION_ID_PREFIX = "qpsid_"
_REME_SESSION_ID_B64_PREFIX = f"{_REME_SESSION_ID_PREFIX}b64_"
_REME_SESSION_ID_HASH_PREFIX = f"{_REME_SESSION_ID_PREFIX}sha256_"
_MAX_REME_SESSION_ID_CHARS = 240
_WINDOWS_INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WINDOWS_RESERVED_FILENAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

# [hanbao modification] Time-awareness: stamp retrieved memory with its
# source date so the model can distinguish historical facts from the
# user's current state (e.g. "user had a cold last week" vs "user is
# sick now"). Daily notes are stored as YYYY-MM-DD.md, so dates appear
# in search result file paths.
_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

# P1 write-side guidance injected into ReMe consolidation jobs via their
# hint/memory_hint parameters. Whether ReMe honors it depends on its
# internal prompt; the retrieval-side annotation below already provides
# the robust fix for stale "current state" claims.
_MEMORY_TIME_HINT = (
    "时间感知要求：提炼事实时给每条事实标注采集日期(as-of)。"
    "用户临时身体状态(如感冒/发烧/疲劳)默认短期，标注采集日期并"
    "默认有效期不超过7天；超期事实不应当作当前状态。仅长期偏好/"
    "身份事实才持久保留。"
)

# [hanbao modification] Source-tag + fiction-isolation + compression governance
# (req ①③④). Injected into auto_memory / auto_dream hints, mirroring the
# time-awareness hint above. Advisory: ReMe may honor it partially, but it
# steers extraction toward provenance tags and away from persisting fiction.
_MEMORY_SOURCE_HINT = (
    "来源与可信度标注要求：提炼/整合每条事实时，在条目开头标注来源标签"
    "——用户明确陈述的事实标 [user_stated]，由对话推断(未确认)的事实标 "
    "[AI_inferred]，角色扮演/创作/虚构内容标 [AI_creative]。规则："
    "① [AI_creative] 内容(含虚构情节、想象设定、角色扮演)严禁写入长期记忆"
    "与每日笔记，只存在于当轮对话，不得沉淀为记忆；"
    "② 压缩/做梦(dream)整合时保留原始来源标签不抹除，不得将 [AI_inferred] "
    "提升为 [user_stated]；③ 当 [user_stated] 与 [AI_inferred] 冲突时，"
    "保留 [user_stated]、丢弃 [AI_inferred]；④ 同一事实出现多个相互矛盾的"
    "[user_stated] 版本时(如用户先说住北京后改说住上海)，以采集日期最新的"
    "版本为准，旧版本标记 [user_stated][已废弃] 并不再引用，不得新旧并存。"
)


# [hanbao modification] Transient-state / time-bound-plan keyword set (req ②③④).
# When a retrieved memory has no dated daily-note anchor yet clearly refers to
# a short-lived condition or a one-off plan, we hard-prompt the model to treat
# it as stale unless the user recently re-confirmed it. No machine [valid_until]
# tag — relies on the model's own time reasoning plus a correct "today".
_TRANSIENT_KEYWORDS = (
    "感冒|发烧|发热|生病|住院|咳嗽|头痛|难受|累|疲劳|疲惫|"
    "心情|情绪|焦虑|抑郁|低落|生气|难过|"
    "计划|打算|准备去|要去|出差|旅行|旅游|搬家|换工作|离职|"
    "cold|fever|sick|hospital|tired|exhausted|anxious|depressed|"
    "plan|trip|travel|move|quit|resign"
)


def _today_in_tz(tz_name: "str | None") -> datetime.date:
    """Resolve "today" in the user's IANA timezone, falling back to local.

    Containers often run in UTC while the user is in GMT+8; using the local
    (naive) date shifts every overnight memory by a day, so the model would
    call yesterday's cold "today" (req ②). Resolve against user_timezone and
    degrade gracefully if the tz db is missing.
    """
    if tz_name:
        try:
            from zoneinfo import ZoneInfo

            return datetime.datetime.now(ZoneInfo(tz_name)).date()
        except Exception:  # pragma: no cover - missing tzdata / bad name
            logger.debug("user_timezone %r unresolved, fallback local", tz_name)
    return datetime.date.today()


def _annotate_memory_dates(
    text: str,
    user_timezone: "str | None" = None,
) -> str:
    """Prepend a time-awareness note to memory search results.

    Scans for YYYY-MM-DD date tokens (typically from daily-note file
    paths like daily/2026-08-12.md) and tells the model how old the
    retrieved memory is, so it won't treat stale facts as the user's
    current state. The reference "today" is resolved in the user's IANA
    timezone so a GMT+8 user is never told a UTC container's "yesterday".
    """
    if not text:
        return text
    today = _today_in_tz(user_timezone)
    found: set[datetime.date] = set()
    for y, m, d in _DATE_RE.findall(text):
        try:
            found.add(datetime.date(int(y), int(m), int(d)))
        except ValueError:
            continue
    if not found:
        # No date anchor: cannot assess age. If it reads like a transient
        # state or a time-bound plan, hard-prompt staleness + no follow-up.
        if re.search(_TRANSIENT_KEYWORDS, text, flags=re.IGNORECASE):
            return (
                "\n[记忆时间提示] 以下为检索到的历史记忆，且未带日期。"
                "若涉及临时身体状态(如感冒/发烧，通常 3-5 天自愈)或"
                "一次性计划(如出差/旅行/搬家，超过约一周未再提及即视为已过期)，"
                "默认按'已恢复/已过期'处理，不要主动追问用户"
                "'好了没/去了没'。引用为当前状态前请先确认。\n" + text
            )
        return (
            "\n[记忆时间提示] 以下为检索到的历史记忆。引用用户当前状态"
            "(健康/情绪/位置等)前，请先确认该记忆是否仍为近期。\n" + text
        )
    newest = max(found)
    days_ago = (today - newest).days
    if days_ago <= 0:
        age = "今天"
    elif days_ago == 1:
        age = "昨天"
    else:
        age = f"约 {days_ago} 天前"
    dates_str = "、".join(sorted(d.strftime("%Y-%m-%d") for d in found))
    # Reinforce the no-follow-up rule for explicit transient keywords that are
    # already several days old.
    extra = ""
    if re.search(_TRANSIENT_KEYWORDS, text, flags=re.IGNORECASE) and days_ago >= 3:
        extra = (
            "该内容涉及临时状态/计划且已隔多日，"
            "默认视为已恢复/已过期，勿主动追问。"
        )
    return (
        f"\n[记忆时间提示] 以下记忆关联日期：{dates_str}"
        f"（最新为{age}，属历史记忆，不代表用户此刻状态）。"
        "引用用户当前状态前请先确认是否仍为近期。" + extra + "\n" + text
    )


def _merge_memory_hint(existing: str, extra: str) -> str:
    """Append time-awareness guidance to an existing ReMe hint once."""
    existing = (existing or "").strip()
    if not extra or extra in existing:
        return existing
    return f"{existing} {extra}".strip()


def _to_reme_session_id(session_id: str) -> str:
    """Return a stable Windows-safe session ID for ReMe file storage.

    ReMe 0.4 uses ``session_id`` as a filename component. Hanbao channel
    IDs deliberately contain separators such as ``telegram:123``, which are
    valid logical identifiers but invalid Windows filenames. Keep ordinary
    IDs unchanged for compatibility and encode only unsafe IDs. IDs beginning
    with our encoding namespace are encoded as well, making the mapping
    unambiguous for existing user-provided IDs.
    """
    filename_stem = session_id.split(".", 1)[0].upper()
    is_safe = (
        bool(session_id)
        and session_id == session_id.strip()
        and session_id not in {".", ".."}
        and not session_id.endswith(".")
        and not _WINDOWS_INVALID_FILENAME_CHARS.search(session_id)
        and filename_stem not in _WINDOWS_RESERVED_FILENAMES
        and not session_id.startswith(_REME_SESSION_ID_PREFIX)
        and len(session_id) <= _MAX_REME_SESSION_ID_CHARS
    )
    if is_safe:
        return session_id

    encoded = (
        base64.urlsafe_b64encode(session_id.encode("utf-8"))
        .decode(
            "ascii",
        )
        .rstrip("=")
    )
    encoded_session_id = f"{_REME_SESSION_ID_B64_PREFIX}{encoded}"
    if len(encoded_session_id) <= _MAX_REME_SESSION_ID_CHARS:
        return encoded_session_id

    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return f"{_REME_SESSION_ID_HASH_PREFIX}{digest}"


def _tool_chunk(text: str, *, ok: bool = True) -> ToolChunk:
    return ToolChunk(
        is_last=True,
        state=ToolResultState.SUCCESS if ok else ToolResultState.ERROR,
        content=[TextBlock(type="text", text=text)],
    )


@memory_registry.register("remelight")
class ReMeLightMemoryManager(BaseMemoryManager):
    """Memory manager backed by ReMe.

    ReMe uses the Hanbao workspace root as its vault.  Daily memory,
    digest memory, search, auto-memory, and auto-dream are executed through
    ReMe jobs.
    """

    def __init__(self, working_dir: str, agent_id: str):
        super().__init__(working_dir=working_dir, agent_id=agent_id)
        self._reme: "ReMe | None" = None
        self._reindex_lock = asyncio.Lock()
        # [hanbao modification] req ② — cache the user's IANA timezone so the
        # retrieval-side date annotation resolves "today" correctly even when
        # the container itself runs in UTC.
        try:
            self._user_timezone = getattr(load_config(), "user_timezone", None)
        except Exception:
            self._user_timezone = None
        self._auditor = self._build_auditor()  # [hanbao modification] req ⑤/②
        logger.info(
            "ReMeLightMemoryManager init: agent_id=%s working_dir=%s",
            agent_id,
            working_dir,
        )

        try:
            from reme import ReMe as ReMeApp  # type: ignore

            agent_config: AgentProfileConfig = load_agent_config(self.agent_id)
            global_config = load_config()
            self._reme = ReMeApp(
                **get_reme_app_config(
                    working_dir=self.working_dir,
                    agent_config=agent_config,
                    user_timezone=getattr(
                        global_config,
                        "user_timezone",
                        None,
                    ),
                ),
            )
            self._install_reme_result_hook()
        except Exception as exc:
            logger.warning("ReMe import failed; memory disabled: %s", exc)

    # [hanbao modification] req ⑤/② — memory audit wiring ---------------
    def _build_auditor(self) -> "MemoryAuditor | None":
        """Build the append-only memory auditor, or None if unavailable."""
        try:
            agent_config = load_agent_config(self.agent_id)
            rcfg = agent_config.running.reme_light_memory_config
            return MemoryAuditor(
                self.working_dir,
                self.agent_id,
                rcfg.daily_dir,
                rcfg.digest_dir,
            )
        except Exception:
            logger.warning("memory auditor disabled", exc_info=True)
            return None

    async def start(self) -> None:
        """Start the embedded ReMe application."""
        if self._reme is None:
            return

        await self._update_hanbao_model()
        try:
            await self._reme.start()
            logger.info(
                "ReMe memory manager started for agent '%s'",
                self.agent_id,
            )
        except Exception:
            logger.exception("ReMe start failed")
            return

    async def close(self) -> bool:
        """Close ReMe and cleanup background summary worker state."""
        logger.info(
            "ReMeLightMemoryManager closing: agent_id=%s",
            self.agent_id,
        )

        worker_stopped = await self._shutdown_summarize_worker()

        if self._reme is not None:
            try:
                await self._reme.close()
            except Exception:
                logger.exception("ReMe close failed")
                return False

        self._reme = None
        return worker_stopped

    def get_memory_prompt(self) -> str:
        """Return memory guidance for system prompt injection."""
        agent_config = load_agent_config(self.agent_id)
        cfg = agent_config.running.reme_light_memory_config
        return build_memory_guidance_prompt(
            agent_config.language,
            daily_dir=cfg.daily_dir,
        )

    def get_memory_config(self) -> Any:
        """Return ReMe Light memory configuration."""
        agent_config = load_agent_config(self.agent_id)
        return agent_config.running.reme_light_memory_config

    def list_memory_tools(self):
        """Return memory tool functions to register with the agent toolkit."""
        return [self.memory_search]

    def get_auto_memory_interval(self) -> int:
        """Return ReMe light auto-memory cadence from agent config."""
        agent_config = load_agent_config(self.agent_id)
        interval = (
            agent_config.running.reme_light_memory_config.auto_memory_interval
        )
        if interval is None:
            return 0
        return int(interval)

    async def _update_hanbao_model(self) -> None:
        """Reuse Hanbao's active model in ReMe's default LLM component."""
        if self._reme is None:
            return

        model, _formatter = create_model_and_formatter(self.agent_id)
        await self._reme.update_component(
            "as_llm",
            "default",
            model=model,
        )

    async def _run_reme_job(
        self,
        name: str,
        *,
        needs_llm: bool = False,
        **kwargs: Any,
    ) -> "Response | None":
        if self._reme is None or not getattr(self._reme, "is_started", False):
            logger.debug("ReMe job skipped; app not started: %s", name)
            return None
        try:
            if needs_llm:
                await self._update_hanbao_model()
            response = await self._reme.run_job(name, **kwargs)
            await self._append_reme_job_result_to_inbox(
                name,
                response=response,
                kwargs=kwargs,
            )
            return response
        except Exception:
            logger.exception("ReMe job failed: %s", name)
            return None

    def _install_reme_result_hook(self) -> None:
        """Expose Hanbao inbox delivery to ReMe background steps."""
        if self._reme is None:
            return
        context = getattr(self._reme, "context", None)
        metadata = getattr(context, "metadata", None)
        if not isinstance(metadata, dict):
            logger.debug("ReMe result hook skipped; metadata unavailable")
            return
        metadata[INBOX_RESULT_HOOK_KEY] = self._handle_reme_result_hook

    async def _handle_reme_result_hook(
        self,
        *,
        job_name: str,
        response: "Response",
        kwargs: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Handle result notifications emitted from ReMe background steps."""
        del metadata
        await self._append_reme_job_result_to_inbox(
            job_name,
            response=response,
            kwargs=kwargs or {},
        )

    async def _append_reme_job_result_to_inbox(
        self,
        name: str,
        *,
        response: "Response",
        kwargs: dict[str, Any],
    ) -> bool:
        if name not in INBOX_RESULT_JOB_NAMES:
            return False
        # [hanbao modification] req ⑤/② — audit after any memory-changing job,
        # independent of whether inbox push is enabled (audit must not depend
        # on the inbox feature being on).
        if self._auditor is not None:
            try:
                await asyncio.to_thread(
                    self._auditor.scan_and_record,
                    name,
                    summary=str(getattr(response, "answer", "") or ""),
                    session_id=str(kwargs.get("session_id") or ""),
                    date=str(kwargs.get("date") or ""),
                )
            except Exception:
                logger.warning(
                    "memory audit failed: %s", name, exc_info=True,
                )
        memory_config = self.get_memory_config()
        if not memory_config.inbox_push_enabled:
            logger.info(
                "ReMe job result inbox push disabled: "
                "agent_id=%s job_name=%s",
                self.agent_id,
                name,
            )
            return False
        response_metadata = getattr(response, "metadata", None)
        if isinstance(response_metadata, dict) and response_metadata.get(
            INBOX_EMITTED_METADATA_KEY,
        ):
            return False
        if (
            name in {"auto_memory", "auto_resource"}
            and isinstance(response_metadata, dict)
            and response_metadata.get("modified") is False
        ):
            logger.info(
                "ReMe job result inbox push skipped; no memory change: "
                "agent_id=%s job_name=%s modified=False",
                self.agent_id,
                name,
            )
            return False

        answer = str(getattr(response, "answer", "") or "").strip()
        if len(answer) > MAX_INBOX_BODY_CHARS:
            answer = f"{answer[:MAX_INBOX_BODY_CHARS].rstrip()}\n..."
        success = bool(getattr(response, "success", False))
        title = self._inbox_result_title(name)
        body = answer or self._empty_inbox_result_body(name)
        payload: dict[str, Any] = {
            "job_name": name,
            "session_id": str(kwargs.get("session_id") or ""),
            "date": str(kwargs.get("date") or ""),
            "hint": str(
                kwargs.get("memory_hint") or kwargs.get("hint") or "",
            ),
        }
        if name == "auto_resource":
            changes = kwargs.get("changes") or []
            if isinstance(changes, list):
                payload["change_count"] = len(changes)
            if isinstance(response_metadata, dict):
                payload["processed"] = response_metadata.get("processed")

        try:
            event = await append_inbox_event(
                agent_id=self.agent_id,
                source_type="memory",
                source_id=name,
                event_type=f"{name}_result",
                status="success" if success else "error",
                severity="info" if success else "error",
                title=title,
                body=body,
                payload=payload,
            )
            if isinstance(response_metadata, dict):
                response_metadata[INBOX_EMITTED_METADATA_KEY] = True
            logger.info(
                "ReMe job result pushed to inbox: "
                "agent_id=%s job_name=%s event_id=%s status=%s modified=%s",
                self.agent_id,
                name,
                event.get("id"),
                event.get("status"),
                response_metadata.get("modified")
                if isinstance(response_metadata, dict)
                else None,
            )
            return True
        except Exception:  # pylint: disable=broad-except
            logger.exception(
                "failed to push ReMe job result to inbox: "
                "agent_id=%s job_name=%s success=%s",
                self.agent_id,
                name,
                success,
            )
            return False

    @staticmethod
    def _inbox_result_title(name: str) -> str:
        return {
            "auto_memory": "Auto-memory result",
            "auto_dream": "Auto-dream result",
            "auto_resource": "Auto-resource result",
        }.get(name, "Memory job result")

    @staticmethod
    def _empty_inbox_result_body(name: str) -> str:
        return {
            "auto_memory": "Auto-memory completed with no returned content.",
            "auto_dream": "Auto-dream completed with no returned content.",
            "auto_resource": (
                "Auto-resource completed with no returned content."
            ),
        }.get(name, "Memory job completed with no returned content.")

    async def memory_search(
        self,
        query: str,
        max_results: int = 5,
        min_score: float = 0,
    ) -> ToolChunk:
        """Search memory files semantically.

        Use this tool before answering questions about prior work,
        decisions, dates, people, preferences, or todos. Returns top
        relevant snippets with file paths and line numbers.

        Args:
            query (`str`):
                The semantic search query to find relevant memory snippets.
            max_results (`int`, optional):
                Maximum number of search results to return. Defaults to 5.
            min_score (`float`, optional):
                Minimum relevance score for results. Defaults to 0; keep this
                at 0 in normal use because ReMe search may mix BM25 and fused
                scores with different scales, and raising it can hide valid
                keyword matches.

        Returns:
            `ToolResponse`:
                Search results formatted with paths, line numbers, and
                content.
        """
        query = query.strip()
        if not query:
            return _tool_chunk("Error: query cannot be empty", ok=False)

        response = await self._run_reme_job(
            "search",
            query=query,
            limit=max(1, max_results),
            min_score=max(0.0, min_score),
        )
        if response is None:
            return _tool_chunk("ReMe is not started.", ok=False)

        answer = str(response.answer or "").strip()
        if not answer:
            answer = NO_MEMORY_RESULTS
        answer = _annotate_memory_dates(  # [hanbao modification]
            answer,
            self._user_timezone,
        )
        return _tool_chunk(answer, ok=response.success)

    async def summarize(
        self,
        messages: list[Msg],
        **kwargs: Any,
    ) -> str:
        """Persist conversation messages through ReMe auto-memory."""
        if not messages:
            return ""

        session_id = str(kwargs.get("session_id") or "")
        if not session_id:
            logger.warning(
                "ReMe summarize skipped; session_id is empty: "
                "agent_id=%s messages=%s",
                self.agent_id,
                len(messages),
            )
            return ""

        response = await self._run_reme_job(
            "auto_memory",
            needs_llm=True,
            messages=[msg.model_dump(mode="json") for msg in messages],
            session_id=_to_reme_session_id(session_id),
            memory_hint=_merge_memory_hint(
                _merge_memory_hint(
                    str(kwargs.get("memory_hint") or ""),
                    _MEMORY_TIME_HINT,  # [hanbao modification] P1 time-aware write
                ),
                _MEMORY_SOURCE_HINT,  # [hanbao modification] req ①③④ source tags
            ),
        )
        if response is None:
            return ""
        return str(response.answer or "")

    async def auto_memory_search(
        self,
        messages: list[Msg] | Msg,
        agent_name: str = "",
        **kwargs: Any,
    ) -> dict | None:
        """Auto-search memory and expose it as a completed tool interaction."""
        del agent_name
        del kwargs
        agent_config = load_agent_config(self.agent_id)
        memory_cfg = agent_config.running.reme_light_memory_config
        if not memory_cfg.auto_memory_search_config.enabled:
            return None

        msgs = [messages] if isinstance(messages, Msg) else list(messages)
        query = self._build_query(msgs)
        if not query:
            return None

        search_cfg = memory_cfg.auto_memory_search_config

        max_results = max(1, search_cfg.max_results)
        response = await self._run_reme_job(
            "search",
            query=query,
            limit=max_results,
            min_score=0,
        )
        if response is None or not response.success:
            return None

        text = str(response.answer or "").strip()
        if not text:
            return None

        text = _annotate_memory_dates(  # [hanbao modification]
            text,
            self._user_timezone,
        )

        assistant_msg = self._build_auto_memory_search_msg(
            query=query,
            max_results=max_results,
            text=text,
        )
        return {
            "query": query,
            "text": text,
            "msg": msgs + [assistant_msg],
        }

    async def auto_memory(
        self,
        all_messages: list[Msg],
        **kwargs: Any,
    ) -> None:
        """Auto-extract memory for a prepared reply batch."""
        if not all_messages:
            return
        all_messages = self._messages_without_auto_memory_search(all_messages)
        if not all_messages:
            return
        session_id = str(kwargs.get("session_id") or "")
        if not session_id:
            logger.warning(
                "ReMe auto_memory skipped; session_id is empty: "
                "agent_id=%s messages=%s",
                self.agent_id,
                len(all_messages),
            )
            return

        self.add_summarize_task(
            messages=all_messages,
            session_id=session_id,
        )

    async def dream(self, **kwargs: Any) -> None:
        """Run one ReMe auto-dream pass."""
        hint = _merge_memory_hint(
            _merge_memory_hint(
                str(kwargs.get("hint") or ""),
                _MEMORY_TIME_HINT,  # [hanbao modification] P1 time-aware write
            ),
            _MEMORY_SOURCE_HINT,  # [hanbao modification] req ①③④ source tags
        )
        response = await self._run_reme_job(
            "auto_dream",
            needs_llm=True,
            date=str(kwargs.get("date") or ""),
            hint=hint,
        )
        if response is not None and not response.success:
            raise RuntimeError(str(response.answer))

    async def reme_status(self) -> "Response | None":
        """Return embedded ReMe component memory estimates and process RSS."""
        return await self._run_reme_job("status")

    async def rebuild_index(self) -> "Response | None":
        """Clear and rebuild the ReMe search index on explicit request."""
        if self._reindex_lock.locked():
            raise RuntimeError("Memory index rebuild is already running")
        async with self._reindex_lock:
            return await self._run_reme_job("reindex")
