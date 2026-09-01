# -*- coding: utf-8 -*-
"""Memory & profile entry browser for the hanbao console.

[hanbao modification] This module is new hanbao code (no upstream
counterpart).  It exposes the ReMe-backed memory vault as **individual
entries** so the user can see what the agent remembers, and correct or
delete a single fact without hand-editing Markdown.

Design constraints (see docs/CHANGES-FROM-UPSTREAM.md stage 6.am):

* **Never bypasses the vault layout** — only the same Markdown files ReMe
  itself owns are touched (``<working_dir>/<daily_dir>/**/*.md``,
  ``<working_dir>/<digest_dir>/**/*.md``, ``MEMORY.md``, ``PROFILE.md``).
  ReMe's ``index_update_loop`` watches those files, so a line edit is
  picked up by the next reindex exactly like a ReMe write.
* **Never weakens existing guards** — every resolved path is contained to
  the allowed roots *after* ``resolve()`` (symlink-safe), and any path
  inside the secret directory is rejected outright.  This is the same
  containment contract ``security/tool_guard/guardians/file_guardian.py``
  enforces for tool calls.
* **Append-only audit** — every user-driven delete/correct is recorded
  through ``MemoryAuditor`` so the trail survives (stage 6.ak).

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import datetime
import hashlib
import logging
import os
import re
import tempfile
import threading
from pathlib import Path
from typing import Any, Iterable

from ...constant import SECRET_DIR

logger = logging.getLogger(__name__)

# Reuse the transient-state keyword set introduced in stage 6.al so the
# console surfaces the same "this is probably stale" judgement the model
# gets during retrieval.  Imported lazily to avoid a hard import cycle.
_TRANSIENT_KEYWORDS: re.Pattern[str] | None = None


def _transient_pattern() -> re.Pattern[str]:
    """Return the compiled transient-state keyword pattern (6.al)."""
    global _TRANSIENT_KEYWORDS  # noqa: PLW0603
    if _TRANSIENT_KEYWORDS is None:
        try:
            from .reme_light_memory_manager import _TRANSIENT_KEYWORDS as raw

            _TRANSIENT_KEYWORDS = re.compile(raw, re.IGNORECASE)
        except Exception:  # pragma: no cover - defensive
            logger.debug(
                "transient keyword set unavailable; staleness hints disabled",
            )
            _TRANSIENT_KEYWORDS = re.compile(r"(?!x)x")
    return _TRANSIENT_KEYWORDS


# ── Source tags (kept in sync with _MEMORY_SOURCE_HINT, stage 6.ak) ─────────

SOURCE_USER_STATED = "user_stated"
SOURCE_AI_INFERRED = "AI_inferred"
SOURCE_AI_CREATIVE = "AI_creative"
SOURCE_UNKNOWN = "unknown"

SOURCE_TAGS = (
    SOURCE_USER_STATED,
    SOURCE_AI_INFERRED,
    SOURCE_AI_CREATIVE,
)

_TAG_RE = re.compile(
    r"\[(?P<tag>user_stated|AI_inferred|AI_creative)"
    r"(?P<scope>::[^\]]*)?\]",
    re.IGNORECASE,
)
_DEPRECATED_RE = re.compile(r"\[已废弃\]|\[deprecated\]", re.IGNORECASE)
_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_ASOF_RE = re.compile(r"\[as-of:\s*(\d{4}-\d{2}-\d{2})\s*\]", re.IGNORECASE)

_MEMORY_MD_NAMES = ("MEMORY.md", "PROFILE.md")

# Lines that are structural (headings / separators / fences) are shown but
# not editable — deleting them would corrupt the document skeleton.
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
_FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")

MAX_ENTRIES = 500
MAX_FILE_BYTES = 2 * 1024 * 1024

_write_locks: dict[str, threading.Lock] = {}
_write_locks_guard = threading.Lock()


def _lock_for(path: str) -> threading.Lock:
    with _write_locks_guard:
        lock = _write_locks.get(path)
        if lock is None:
            lock = threading.Lock()
            _write_locks[path] = lock
        return lock


class MemoryBrowserError(ValueError):
    """Raised when a memory edit request is invalid or unsafe."""


class MemoryBrowser:
    """Read/entry-level edit view over an agent's memory vault."""

    def __init__(
        self,
        working_dir: str | Path,
        agent_id: str | None = None,
        *,
        daily_dir: str = "memory",
        digest_dir: str = "digest",
    ):
        self.working_dir = Path(working_dir)
        self.agent_id = agent_id
        self.daily_dir = daily_dir
        self.digest_dir = digest_dir
        self.memory_dir = self.working_dir / daily_dir
        self.digest_dir_path = self.working_dir / digest_dir
        self._secret_root = Path(SECRET_DIR)

    # ------------------------------------------------------------------
    # Path safety
    # ------------------------------------------------------------------

    def _allowed_roots(self) -> list[Path]:
        return [
            self.memory_dir,
            self.digest_dir_path,
            self.working_dir,
        ]

    def _is_forbidden(self, resolved: Path) -> bool:
        """Reject anything living under the secret directory."""
        try:
            resolved.relative_to(self._secret_root.resolve())
            return True
        except ValueError:
            return False
        except OSError:  # pragma: no cover - odd filesystems
            return False

    def resolve_file(self, rel_path: str) -> Path:
        """Resolve a vault-relative path, enforcing containment.

        Args:
            rel_path: Path relative to the workspace root, as returned by
                :meth:`list_entries` in the ``file`` field.

        Returns:
            The resolved absolute :class:`Path`.

        Raises:
            MemoryBrowserError: If the path escapes the vault or points at
                the secret directory.
        """
        raw = (rel_path or "").strip().replace("\\", "/").lstrip("/")
        if not raw:
            raise MemoryBrowserError("file is required")
        parts = [p for p in raw.split("/") if p not in ("", ".")]
        if not parts or any(p == ".." for p in parts):
            raise MemoryBrowserError(f"Invalid memory path: {rel_path!r}")
        if not parts[-1].endswith(".md"):
            raise MemoryBrowserError(
                f"Only .md files can be edited: {rel_path!r}",
            )

        candidate = (self.working_dir / "/".join(parts)).resolve(
            strict=False,
        )
        # Skip symlinked entries: resolve() already followed them, so a
        # symlink pointing outside the vault lands outside the roots.
        allowed = False
        for root in self._allowed_roots():
            try:
                candidate.relative_to(root.resolve(strict=False))
                allowed = True
                break
            except (ValueError, OSError):
                continue
        if not allowed:
            raise MemoryBrowserError(
                f"Path escapes the memory vault: {rel_path!r}",
            )
        if self._is_forbidden(candidate):
            raise MemoryBrowserError(
                "Refusing to touch the secret directory",
            )
        # Root-level vault files are limited to the well-known pair, so a
        # stray .md anywhere in the workspace is not editable by accident.
        if candidate.parent == self.working_dir.resolve(strict=False):
            if candidate.name not in _MEMORY_MD_NAMES:
                raise MemoryBrowserError(
                    f"Not a memory file: {rel_path!r}",
                )
        elif not str(candidate).startswith(
            str(self.memory_dir.resolve(strict=False)),
        ) and not str(candidate).startswith(
            str(self.digest_dir_path.resolve(strict=False)),
        ):
            raise MemoryBrowserError(
                f"Not inside the memory vault: {rel_path!r}",
            )
        return candidate

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def vault_files(self) -> list[Path]:
        files: list[Path] = []
        seen: set[Path] = set()
        for root in (self.memory_dir, self.digest_dir_path):
            if not root.is_dir():
                continue
            for path in root.rglob("*.md"):
                if not path.is_file():
                    continue
                resolved = path.resolve(strict=False)
                if resolved in seen or self._is_forbidden(resolved):
                    continue
                seen.add(resolved)
                files.append(path)
        for name in _MEMORY_MD_NAMES:
            path = self.working_dir / name
            if path.is_file():
                resolved = path.resolve(strict=False)
                if resolved not in seen and not self._is_forbidden(resolved):
                    seen.add(resolved)
                    files.append(path)
        return sorted(files, key=lambda p: str(p))

    @staticmethod
    def rel_path(path: Path, working_dir: Path) -> str:
        try:
            return path.resolve(strict=False).relative_to(
                working_dir.resolve(strict=False),
            ).as_posix()
        except (ValueError, OSError):
            return path.name

    @staticmethod
    def _read(path: Path) -> str:
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                return ""
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    # ------------------------------------------------------------------
    # Entry parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _entry_id(rel_path: str, line_no: int, text: str) -> str:
        digest = hashlib.sha1(
            f"{rel_path}:{line_no}:{text}".encode("utf-8"),
        ).hexdigest()
        return digest[:12]

    def _date_for(
        self,
        rel_path: str,
        text: str,
        mtime: float,
        tz_name: str | None,
    ) -> str | None:
        as_of = _ASOF_RE.search(text)
        if as_of:
            return as_of.group(1)
        # NB: group(0) is the full YYYY-MM-DD match; group(1) is only the
        # year — using group(1) here silently truncated every date.
        inline = _DATE_RE.search(text)
        if inline:
            return inline.group(0)
        path_date = _DATE_RE.search(rel_path)
        if path_date:
            return path_date.group(0)
        if mtime:
            try:
                stamp = datetime.datetime.fromtimestamp(mtime)
            except (OSError, ValueError, OverflowError):
                return None
            return stamp.date().isoformat()
        return None

    def _parse_line(
        self,
        rel_path: str,
        line_no: int,
        raw_line: str,
        fallback_date: str | None,
        today: datetime.date,
    ) -> dict[str, Any] | None:
        stripped = raw_line.strip()
        if not stripped:
            return None

        tag_match = _TAG_RE.search(stripped)
        if tag_match:
            matched = tag_match.group("tag")
            source = next(
                t for t in SOURCE_TAGS if t.lower() == matched.lower()
            )
        else:
            source = SOURCE_UNKNOWN

        deprecated = bool(_DEPRECATED_RE.search(stripped))
        entry_date = _ASOF_RE.search(stripped)
        date = (
            entry_date.group(1)
            if entry_date
            else fallback_date
        )

        # Structural lines (headings, code fences) are document skeleton,
        # not memories — they are excluded from the entry list but still
        # occupy their line number, so edits stay correctly addressed.
        if _HEADING_RE.match(raw_line) or _FENCE_RE.match(raw_line):
            return None

        transient = bool(_transient_pattern().search(stripped))

        hint: str | None = None
        if deprecated:
            hint = "deprecated"
        elif transient:
            if date:
                try:
                    age = (
                        today - datetime.date.fromisoformat(date)
                    ).days
                except ValueError:
                    age = 0
                if age >= 3:
                    hint = "likely-stale"
            else:
                hint = "likely-stale"

        return {
            "id": self._entry_id(rel_path, line_no, raw_line),
            "file": rel_path,
            "line": line_no,
            "text": stripped,
            "source": source,
            "deprecated": deprecated,
            "date": date,
            "transient": transient,
            "hint": hint,
            "editable": True,
        }

    # ------------------------------------------------------------------
    # Public API — read
    # ------------------------------------------------------------------

    def list_entries(
        self,
        *,
        query: str = "",
        source: str = "",
        file: str = "",
        include_deprecated: bool = True,
        limit: int = 200,
        user_timezone: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return memory entries across the whole vault.

        Args:
            query: Case-insensitive substring filter on the entry text.
            source: Optional source-tag filter
                (``user_stated`` / ``AI_inferred`` / ``AI_creative`` /
                ``unknown``).
            file: Optional vault-relative file filter.
            include_deprecated: Whether to include ``[已废弃]`` entries.
            limit: Maximum number of entries to return.
            user_timezone: IANA timezone used to resolve "today" for the
                staleness hint (stage 6.al parity).

        Returns:
            Entries sorted newest-first by date, then by file and line.
        """
        today = _today(user_timezone)
        needle = (query or "").strip().lower()
        wanted_source = (source or "").strip().lower()
        wanted_file = (file or "").strip()
        limit = max(1, min(int(limit or 200), MAX_ENTRIES))

        entries: list[dict[str, Any]] = []
        for path in self.vault_files():
            rel_path = self.rel_path(path, self.working_dir)
            if wanted_file and rel_path != wanted_file:
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                mtime = 0.0
            fallback_date = self._date_for(rel_path, "", mtime, user_timezone)
            content = self._read(path)
            for line_no, raw_line in enumerate(content.splitlines(), 1):
                entry = self._parse_line(
                    rel_path,
                    line_no,
                    raw_line,
                    fallback_date,
                    today,
                )
                if entry is None:
                    continue
                if not include_deprecated and entry["deprecated"]:
                    continue
                if (
                    wanted_source
                    and entry["source"].lower() != wanted_source
                ):
                    continue
                if needle and needle not in entry["text"].lower():
                    continue
                entries.append(entry)

        # Newest first, then file/line ascending for a stable reading order
        # (Python's sort is stable, so sort the tie-breakers first).
        entries.sort(key=lambda e: (e["file"], e["line"]))
        entries.sort(key=lambda e: e["date"] or "", reverse=True)
        return entries[:limit]

    def stats(self, *, user_timezone: str | None = None) -> dict[str, Any]:
        """Return aggregate counts for the memory panel header."""
        entries = self.list_entries(
            limit=MAX_ENTRIES,
            user_timezone=user_timezone,
        )
        by_source: dict[str, int] = {tag: 0 for tag in SOURCE_TAGS}
        by_source[SOURCE_UNKNOWN] = 0
        files: set[str] = set()
        deprecated = 0
        stale = 0
        for entry in entries:
            by_source[entry["source"]] = (
                by_source.get(entry["source"], 0) + 1
            )
            files.add(entry["file"])
            if entry["deprecated"]:
                deprecated += 1
            if entry["hint"] == "likely-stale":
                stale += 1
        return {
            "total": len(entries),
            "by_source": by_source,
            "files": len(files),
            "deprecated": deprecated,
            "stale": stale,
            "truncated": len(entries) >= MAX_ENTRIES,
        }

    # ------------------------------------------------------------------
    # Public API — write
    # ------------------------------------------------------------------

    def delete_entry(
        self,
        rel_path: str,
        line: int,
        expected_text: str = "",
    ) -> dict[str, Any]:
        """Delete a single memory line.

        Args:
            rel_path: Vault-relative file path.
            line: 1-based line number.
            expected_text: Optional guard — the operation is aborted when
                the line no longer matches (someone else edited it first).

        Returns:
            Dict describing what was removed.
        """
        return self._mutate(
            rel_path,
            line,
            expected_text,
            new_text=None,
            new_source=None,
        )

    def update_entry(
        self,
        rel_path: str,
        line: int,
        new_text: str,
        expected_text: str = "",
        new_source: str | None = None,
    ) -> dict[str, Any]:
        """Correct a single memory line in place.

        Args:
            rel_path: Vault-relative file path.
            line: 1-based line number.
            new_text: Replacement text for that line.
            expected_text: Optional optimistic-concurrency guard.
            new_source: Optional source tag to (re)apply.  When omitted the
                existing tag is preserved.

        Returns:
            Dict describing the change.
        """
        cleaned = (new_text or "").strip()
        if not cleaned:
            raise MemoryBrowserError("new_text must not be empty")
        return self._mutate(
            rel_path,
            line,
            expected_text,
            new_text=cleaned,
            new_source=new_source,
        )

    def _mutate(
        self,
        rel_path: str,
        line: int,
        expected_text: str,
        *,
        new_text: str | None,
        new_source: str | None,
    ) -> dict[str, Any]:
        if not isinstance(line, int) or line < 1:
            raise MemoryBrowserError("line must be a 1-based line number")

        path = self.resolve_file(rel_path)
        if not path.is_file():
            raise MemoryBrowserError(f"Memory file not found: {rel_path!r}")

        if new_source is not None and new_source not in SOURCE_TAGS:
            raise MemoryBrowserError(
                f"Unsupported source tag: {new_source!r}",
            )

        key = str(path)
        with _lock_for(key):
            original = self._read(path)
            lines = original.splitlines(keepends=True)
            if line > len(lines):
                raise MemoryBrowserError(
                    f"Line {line} is out of range for {rel_path!r}",
                )
            current = lines[line - 1].rstrip("\r\n")
            if expected_text and current.strip() != expected_text.strip():
                raise MemoryBrowserError(
                    "Memory changed since it was loaded; refresh and"
                    " try again",
                )
            if _HEADING_RE.match(current) or _FENCE_RE.match(current):
                raise MemoryBrowserError(
                    "Structural lines cannot be edited from the memory"
                    " panel",
                )

            if new_text is None:
                del lines[line - 1]
                action = "delete"
            else:
                replacement = new_text
                if new_source:
                    stripped_tag = _TAG_RE.sub("", new_text).strip()
                    stripped_tag = _DEPRECATED_RE.sub("", stripped_tag)
                    replacement = (
                        f"[{new_source}] {stripped_tag.strip()}"
                    ).strip()
                lines[line - 1] = replacement + "\n"
                action = "update"

            new_content = "".join(lines)
            if original.endswith(("\n", "\r")) and not new_content.endswith(
                "\n",
            ):
                new_content += "\n"
            self._atomic_write(path, new_content)

        self._record_audit(action, rel_path, line, current, new_text)
        logger.info(
            "memory entry %s: agent=%s file=%s line=%s",
            action,
            self.agent_id,
            rel_path,
            line,
        )
        return {
            "ok": True,
            "action": action,
            "file": rel_path,
            "line": line,
            "previous": current.strip(),
            "current": (new_text or "").strip(),
        }

    @staticmethod
    def _atomic_write(path: Path, content: str) -> None:
        """Write *content* atomically so ReMe never sees a partial file."""
        directory = path.parent
        fd, tmp_name = tempfile.mkstemp(
            dir=str(directory),
            prefix=".hanbao-mem-",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
                fh.write(content)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_name, path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

    def _record_audit(
        self,
        action: str,
        rel_path: str,
        line: int,
        previous: str,
        new_text: str | None,
    ) -> None:
        """Append the user-driven change to the append-only audit log."""
        try:
            from .memory_audit import MemoryAuditor

            auditor = MemoryAuditor(
                self.working_dir,
                self.agent_id or "",
                self.daily_dir,
                self.digest_dir,
            )
            auditor.record_job(
                f"console_{action}",
                summary=(
                    f"console {action}: {rel_path}:{line}"
                    f" — {previous.strip()[:200]}"
                ),
                removed_user_stated=[
                    {
                        "path": rel_path,
                        "line": previous.strip()[:200],
                        "by": "console_user",
                    },
                ]
                if action == "delete"
                else [],
            )
        except Exception:  # pragma: no cover - audit must never block
            logger.debug("memory audit record failed", exc_info=True)


def _today(tz_name: str | None) -> datetime.date:
    """Resolve "today" in *tz_name*, falling back to the local date."""
    if tz_name:
        try:
            from zoneinfo import ZoneInfo

            return datetime.datetime.now(ZoneInfo(tz_name)).date()
        except Exception:  # pragma: no cover - missing tzdata / bad name
            logger.debug("timezone %r unresolved in memory browser", tz_name)
    return datetime.date.today()


def iter_source_tags() -> Iterable[str]:
    """Return every known source tag (used by the API schema)."""
    return SOURCE_TAGS + (SOURCE_UNKNOWN,)
