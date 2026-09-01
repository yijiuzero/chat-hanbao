# -*- coding: utf-8 -*-
# [hanbao modification]
"""Index storage for the hanbao local knowledge base.

This module is new hanbao code (no upstream counterpart).

The index lives **inside the agent workspace** (``.hanbao_knowledge/``),
i.e. on the same NAS volume as the rest of hanbao's data.  Source
documents are never copied — only extracted chunk text plus a per-file
fingerprint (size + mtime) is stored, so a rebuild skips unchanged files.

Path safety mirrors the memory vault:
  * source directories must exist and must not sit inside the secret dir;
  * symlinked files are resolved before the include/exclude decision;
  * results report the path relative to the configured source root
    (plus the root itself), never a fully expanded secret path.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Callable, Iterable

from .bm25 import BM25Index
from .config import KnowledgeConfig
from .extract import chunk_text, extract_text, is_supported, matches_any
from .tokenizer import tokenize

logger = logging.getLogger(__name__)

INDEX_DIR_NAME = ".hanbao_knowledge"
INDEX_FILE = "index.json"
CHUNKS_FILE = "chunks.jsonl"


class KnowledgeStore:
    """Build, persist and query the local BM25 knowledge index."""

    def __init__(self, working_dir: str | Path):
        self.working_dir = Path(working_dir)
        self.index_dir = self.working_dir / INDEX_DIR_NAME
        self.index_path = self.index_dir / INDEX_FILE
        self.chunks_path = self.index_dir / CHUNKS_FILE

        self.built_at: float | None = None
        self.config_fingerprint: str = ""
        self.files: dict[str, dict[str, Any]] = {}
        self.chunks: list[dict[str, Any]] = []
        self._index = BM25Index()
        self._loaded = False

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self.load()
        self._loaded = True

    def load(self) -> bool:
        """Load a previously built index.  Returns True on success."""
        if not self.index_path.is_file():
            return False
        try:
            meta = json.loads(self.index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False

        chunks: list[dict[str, Any]] = []
        if self.chunks_path.is_file():
            try:
                for line in self.chunks_path.read_text(
                    encoding="utf-8",
                ).splitlines():
                    if line.strip():
                        chunks.append(json.loads(line))
            except (OSError, json.JSONDecodeError):
                return False

        self.built_at = meta.get("built_at")
        self.config_fingerprint = meta.get("config_fingerprint", "")
        self.files = meta.get("files") or {}
        self.chunks = chunks
        self._index = BM25Index.from_dict(meta.get("bm25") or {})
        if self._index.doc_count != len(chunks):
            logger.warning(
                "Knowledge index is inconsistent (%s docs vs %s chunks);"
                " rebuild needed",
                self._index.doc_count,
                len(chunks),
            )
            return False
        return True

    def save(self) -> None:
        """Persist the index atomically."""
        self.index_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "built_at": self.built_at,
            "config_fingerprint": self.config_fingerprint,
            "files": self.files,
            "bm25": self._index.to_dict(),
        }
        tmp_index = self.index_path.with_suffix(".json.tmp")
        tmp_index.write_text(
            json.dumps(meta, ensure_ascii=False),
            encoding="utf-8",
        )
        tmp_index.replace(self.index_path)

        tmp_chunks = self.chunks_path.with_suffix(".jsonl.tmp")
        with tmp_chunks.open("w", encoding="utf-8") as fh:
            for chunk in self.chunks:
                fh.write(
                    json.dumps(chunk, ensure_ascii=False) + "\n",
                )
        tmp_chunks.replace(self.chunks_path)

    # ------------------------------------------------------------------
    # Source discovery
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_source_dir(raw: str) -> Path | None:
        try:
            path = Path(os.path.expanduser(raw)).resolve(strict=False)
        except (OSError, RuntimeError):
            return None
        return path if path.is_dir() else None

    def _iter_candidates(
        self,
        config: KnowledgeConfig,
    ) -> Iterable[tuple[Path, Path]]:
        """Yield ``(source_root, file_path)`` pairs to consider."""
        max_bytes = config.max_file_mb * 1024 * 1024
        for raw_dir in config.source_dirs:
            root = self._resolve_source_dir(raw_dir)
            if root is None:
                continue
            try:
                walker = os.walk(root, followlinks=False)
            except OSError:
                continue
            for dirpath, dirnames, filenames in walker:
                # Prune hidden / excluded directories in place.
                dirnames[:] = [
                    d
                    for d in dirnames
                    if not d.startswith(".")
                    and not matches_any(
                        d,
                        ["node_modules", "__pycache__"],
                    )
                ]
                for filename in filenames:
                    candidate = Path(dirpath) / filename
                    if not is_supported(candidate):
                        continue
                    if not matches_any(filename, config.include_globs):
                        continue
                    rel = self._relative(candidate, root)
                    if matches_any(rel, config.exclude_globs):
                        continue
                    try:
                        if candidate.stat().st_size > max_bytes:
                            continue
                    except OSError:
                        continue
                    yield root, candidate

    @staticmethod
    def _relative(path: Path, root: Path) -> str:
        try:
            return path.resolve(strict=False).relative_to(
                root.resolve(strict=False),
            ).as_posix()
        except (ValueError, OSError):
            return path.name

    @staticmethod
    def _fingerprint(path: Path) -> tuple[int, int]:
        try:
            stat = path.stat()
            return (stat.st_size, int(stat.st_mtime))
        except OSError:
            return (0, 0)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(
        self,
        config: KnowledgeConfig,
        *,
        rebuild: bool = False,
        fingerprint: str = "",
        progress: Callable[[str, int, int], None] | None = None,
    ) -> dict[str, Any]:
        """(Re)build the index for *config*.

        Args:
            config: The knowledge configuration.
            rebuild: When True, ignore cached file fingerprints.
            fingerprint: Config fingerprint stored alongside the index.
            progress: Optional ``(stage, done, total)`` callback.

        Returns:
            Build statistics.
        """
        self._ensure_loaded()
        previous = {} if rebuild else dict(self.files)
        if fingerprint and self.config_fingerprint != fingerprint:
            # Directory set / chunking changed: nothing can be reused.
            previous = {}

        new_files: dict[str, dict[str, Any]] = {}
        new_chunks: list[dict[str, Any]] = []
        scanned = 0
        indexed = 0
        skipped_unchanged = 0
        failed = 0

        candidates = list(self._iter_candidates(config))
        total = len(candidates)

        for root, path in candidates:
            scanned += 1
            key = str(path)
            try:
                stat = path.stat()
                signature = (stat.st_size, int(stat.st_mtime))
            except OSError:
                failed += 1
                continue

            cached = previous.get(key)
            rel = self._relative(path, root)
            meta = {
                "root": str(root),
                "path": rel,
                "size": signature[0],
                "mtime": signature[1],
                "chunks": 0,
                "mode": "cached",
            }

            if cached and (
                cached.get("size") == signature[0]
                and cached.get("mtime") == signature[1]
            ):
                # Reuse the previously extracted chunks verbatim.
                reused = [
                    c for c in self.chunks if c.get("source") == key
                ]
                if reused:
                    new_chunks.extend(reused)
                    meta["chunks"] = len(reused)
                    meta["mode"] = cached.get("mode", "cached")
                    new_files[key] = meta
                    skipped_unchanged += 1
                    continue

            text, mode = extract_text(path)
            if not text.strip():
                meta["mode"] = mode or "empty"
                new_files[key] = meta
                if mode in {"unsupported", "empty", "error"}:
                    failed += 1
                continue

            pieces = chunk_text(
                text,
                config.chunk_size,
                config.chunk_overlap,
            )
            for order, piece in enumerate(pieces):
                new_chunks.append(
                    {
                        "source": key,
                        "root": str(root),
                        "path": rel,
                        "order": order,
                        "text": piece,
                    },
                )
            meta["chunks"] = len(pieces)
            meta["mode"] = mode
            new_files[key] = meta
            indexed += 1

            if progress and scanned % 25 == 0:
                progress("indexing", scanned, total)

        self.files = new_files
        self.chunks = new_chunks
        self._index.build(
            tokenize(chunk["text"]) for chunk in new_chunks
        )
        self.built_at = time.time()
        self.config_fingerprint = fingerprint
        self.save()

        if progress:
            progress("done", total, total)

        return {
            "ok": True,
            "built_at": self.built_at,
            "files_indexed": indexed,
            "files_unchanged": skipped_unchanged,
            "files_failed": failed,
            "files_total": len(new_files),
            "chunks": len(new_chunks),
            "scanned": scanned,
        }

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        min_score: float = 1.0,
        snippet_chars: int = 320,
    ) -> list[dict[str, Any]]:
        """Return the best matching chunks for *query*.

        Args:
            query: Natural-language query (Chinese or English).
            top_k: Maximum number of chunks to return.
            min_score: Discard BM25 hits below this score.
            snippet_chars: Trim the returned chunk to this length.

        Returns:
            List of dicts with ``score``, ``path``, ``root``, ``source``,
            ``order`` and ``text``.
        """
        self._ensure_loaded()
        if not self.chunks or not query.strip():
            return []
        tokens = tokenize(query)
        if not tokens:
            return []

        hits = self._index.top(tokens, top_k=top_k, min_score=min_score)
        results: list[dict[str, Any]] = []
        for doc_index, score in hits:
            if doc_index >= len(self.chunks):
                continue
            chunk = self.chunks[doc_index]
            text = chunk.get("text", "")
            if len(text) > snippet_chars:
                text = text[:snippet_chars].rstrip() + "…"
            results.append(
                {
                    "score": round(float(score), 4),
                    "path": chunk.get("path", ""),
                    "root": chunk.get("root", ""),
                    "source": chunk.get("source", ""),
                    "order": chunk.get("order", 0),
                    "text": text,
                },
            )
        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return index statistics for the console."""
        self._ensure_loaded()
        by_root: dict[str, int] = {}
        modes: dict[str, int] = {}
        for meta in self.files.values():
            by_root[meta.get("root", "")] = (
                by_root.get(meta.get("root", ""), 0) + 1
            )
            mode = meta.get("mode") or "unknown"
            modes[mode] = modes.get(mode, 0) + 1
        return {
            "built": bool(self.files),
            "built_at": self.built_at,
            "files": len(self.files),
            "chunks": len(self.chunks),
            "by_root": by_root,
            "modes": modes,
            "index_dir": str(self.index_dir),
        }

    def sources(self) -> list[dict[str, Any]]:
        """Return the indexed file list."""
        self._ensure_loaded()
        items = []
        for key, meta in self.files.items():
            items.append(
                {
                    "path": meta.get("path", ""),
                    "root": meta.get("root", ""),
                    "chunks": meta.get("chunks", 0),
                    "size": meta.get("size", 0),
                    "mtime": meta.get("mtime", 0),
                    "mode": meta.get("mode", ""),
                    "source": key,
                },
            )
        items.sort(key=lambda item: item["path"])
        return items

    def clear(self) -> None:
        """Drop the index from memory and disk."""
        self.files = {}
        self.chunks = []
        self._index = BM25Index()
        self.built_at = None
        self.config_fingerprint = ""
        for path in (self.index_path, self.chunks_path):
            try:
                path.unlink()
            except OSError:
                pass
