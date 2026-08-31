# -*- coding: utf-8 -*-
"""Append-only memory audit + soft governance for the ReMe vault.

[hanbao modification] Source-tag governance (req ①③④) is steered via the
hint injected in ``reme_light_memory_manager``. This module provides the
persistent, queryable audit trail (req ⑤) and post-write deletion detection
(req ②) **without** relying on git — the slim production image removes the
git binary, so a pure-Python append-only log is the safer, dependency-free
equivalent of "git blame the vault".

Design notes:
  * All state lives under a hidden ``.hanbao_memory_audit/`` directory inside
    the agent working dir (application data, never personal user files).
  * Every operation is wrapped in try/except so a failure here can NEVER
    break the memory write path.
  * The audit log is append-only JSONL; a small snapshot JSON captures the
    last-seen memory-file text so we can diff deletions between jobs.
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_AUDIT_DIR_NAME = ".hanbao_memory_audit"
_AUDIT_LOG_NAME = "memory_audit.jsonl"
_SNAPSHOT_NAME = "memory_snapshot.json"

# Source-tag patterns — kept in sync with ``_MEMORY_SOURCE_HINT``.
_USER_STATED_RE = re.compile(r"\[user_stated(?:::[^\]]+)?\]", re.IGNORECASE)
_AI_CREATIVE_RE = re.compile(r"\[AI_creative\]", re.IGNORECASE)

_MEMORY_MD_NAMES = ("PROFILE.md", "MEMORY.md")


class MemoryAuditor:
    """Records memory-job outcomes and flags governance violations.

    Persistence format (all under ``<working_dir>/.hanbao_memory_audit/``):
      * ``memory_audit.jsonl`` — one JSON object per job, append-only.
      * ``memory_snapshot.json`` — last-seen full text of each tracked file,
        used to diff deletions between jobs.
    """

    def __init__(
        self,
        working_dir: str | Path,
        agent_id: str,
        daily_dir: str = "memory",
        digest_dir: str = "digest",
        *,
        enabled: bool = True,
    ):
        self.working_dir = Path(working_dir)
        self.agent_id = agent_id
        self.daily_dir = daily_dir
        self.digest_dir = digest_dir
        # Escape hatch: set HANBAO_MEMORY_AUDIT_DISABLE=1 to turn it off.
        if os.environ.get("HANBAO_MEMORY_AUDIT_DISABLE") == "1":
            enabled = False
        self.enabled = enabled
        self.audit_dir = self.working_dir / _AUDIT_DIR_NAME
        self.log_path = self.audit_dir / _AUDIT_LOG_NAME
        self.snapshot_path = self.audit_dir / _SNAPSHOT_NAME
        self._lock = threading.Lock()
        if self.enabled:
            try:
                self.audit_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.warning(
                    "memory audit dir init failed; audit disabled: %s",
                    self.audit_dir,
                    exc_info=True,
                )
                self.enabled = False

    # ------------------------------------------------------------------
    # File discovery + reading
    # ------------------------------------------------------------------
    def _memory_files(self) -> list[Path]:
        files: list[Path] = []
        for sub in (self.daily_dir, self.digest_dir):
            p = self.working_dir / sub
            if p.is_dir():
                files.extend(p.rglob("*.md"))
        for name in _MEMORY_MD_NAMES:
            f = self.working_dir / name
            if f.is_file():
                files.append(f)
        return files

    @staticmethod
    def _read(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def record_job(
        self,
        job_name: str,
        *,
        summary: str = "",
        session_id: str = "",
        date: str = "",
        flagged_creative: list[str] | None = None,
        removed_user_stated: list[dict] | None = None,
    ) -> None:
        """Append one audit entry (JSONL)."""
        if not self.enabled:
            return
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.agent_id,
            "job": job_name,
            "session_id": session_id or "",
            "date": date or "",
            "summary": (summary or "")[:4000],
            "flagged_creative": flagged_creative or [],
            "removed_user_stated": removed_user_stated or [],
        }
        try:
            with self._lock, self.log_path.open(
                "a",
                encoding="utf-8",
            ) as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            logger.warning("memory audit log write failed", exc_info=True)

    def scan_and_record(
        self,
        job_name: str,
        *,
        summary: str = "",
        session_id: str = "",
        date: str = "",
    ) -> None:
        """Scan the vault after a memory job and record an audit entry.

        Detects:
          * ``[AI_creative]`` content that leaked into persisted memory
            (req ① soft enforcement / req ③ fiction isolation).
          * ``[user_stated]`` lines present before but gone now
            (req ② soft deletion detection — who/what was removed).
        """
        if not self.enabled:
            return
        try:
            flagged_creative = self._detect_creative_leaks()
            removed_user_stated = self._detect_user_stated_deletions()
            self.record_job(
                job_name,
                summary=summary,
                session_id=session_id,
                date=date,
                flagged_creative=flagged_creative,
                removed_user_stated=removed_user_stated,
            )
        except Exception:
            logger.warning("memory audit scan failed", exc_info=True)

    def query(self, term: str) -> list[dict]:
        """Return audit entries whose serialized form contains ``term``.

        Lets an operator answer "when was the neck-tattoo line written / who
        removed it?" by grepping the persistent log.
        """
        if not self.enabled or not self.log_path.is_file():
            return []
        out: list[dict] = []
        try:
            text = self.log_path.read_text(encoding="utf-8")
        except Exception:
            return []
        needle = term.lower()
        for line in text.splitlines():
            if not line.strip():
                continue
            if needle in line.lower():
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
        return out

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _detect_creative_leaks(self) -> list[str]:
        hits: list[str] = []
        for f in self._memory_files():
            for i, line in enumerate(self._read(f).splitlines(), 1):
                if _AI_CREATIVE_RE.search(line):
                    hits.append(f"{f.name}:{i}")
        return hits

    def _detect_user_stated_deletions(self) -> list[dict]:
        current = {str(f): self._read(f) for f in self._memory_files()}
        prev = self._load_snapshot()
        removed: list[dict] = []
        for path, prev_text in prev.items():
            cur_text = current.get(path, "")
            if cur_text == prev_text:
                continue
            prev_lines = {
                ln for ln in prev_text.splitlines()
                if _USER_STATED_RE.search(ln)
            }
            cur_lines = {
                ln for ln in cur_text.splitlines()
                if _USER_STATED_RE.search(ln)
            }
            for gone in (prev_lines - cur_lines):
                removed.append({"path": Path(path).name, "line": gone[:200]})
        self._save_snapshot(current)
        return removed

    def _load_snapshot(self) -> dict[str, str]:
        try:
            with self.snapshot_path.open(encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {}

    def _save_snapshot(self, snap: dict[str, str]) -> None:
        try:
            with self._lock, self.snapshot_path.open(
                "w",
                encoding="utf-8",
            ) as fh:
                json.dump(snap, fh, ensure_ascii=False)
        except Exception:
            logger.warning("memory snapshot save failed", exc_info=True)
