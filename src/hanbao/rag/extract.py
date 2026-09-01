# -*- coding: utf-8 -*-
# [hanbao modification]
"""Text extraction for the hanbao local knowledge base.

This module is new hanbao code (no upstream counterpart).

Plain-text formats are read directly with the standard library.  Office /
PDF documents go through ``markitdown`` (MIT), which hanbao already
depends on for the document tools (I-019) — **no new dependency** and no
network access.  Images are indexed by filename and folder only (hanbao
ships no OCR engine); that is a deliberate, documented limitation.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import fnmatch
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Read directly as UTF-8 (with a latin-1 fallback for stray encodings).
_PLAIN_SUFFIXES = frozenset(
    {
        ".md",
        ".txt",
        ".csv",
        ".json",
        ".log",
        ".yaml",
        ".yml",
        ".ini",
        ".conf",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".html",
        ".htm",
        ".xml",
        ".rst",
        ".tex",
    },
)

# Converted through markitdown.
_RICH_SUFFIXES = frozenset(
    {
        ".pdf",
        ".docx",
        ".doc",
        ".pptx",
        ".ppt",
        ".xlsx",
        ".xls",
        ".epub",
        ".zip",
    },
)

# Indexed as metadata only (path + size); no OCR in the slim image.
_METADATA_ONLY_SUFFIXES = frozenset(
    {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".heic",
        ".bmp",
        ".tiff",
        ".mp4",
        ".mov",
        ".mkv",
        ".mp3",
        ".wav",
        ".flac",
    },
)

_MAX_CONVERT_BYTES = 50 * 1024 * 1024


def is_supported(path: Path) -> bool:
    """Return True when *path* can be indexed at all."""
    suffix = path.suffix.lower()
    return suffix in (
        _PLAIN_SUFFIXES | _RICH_SUFFIXES | _METADATA_ONLY_SUFFIXES
    )


def matches_any(name: str, patterns: list[str]) -> bool:
    """Return True when *name* matches one of the glob *patterns*."""
    lowered = name.lower()
    for pattern in patterns or []:
        if fnmatch.fnmatch(lowered, pattern.lower()):
            return True
    return False


def _read_plain(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")
    except OSError:
        return ""


def _convert(path: Path) -> str:
    """Convert an Office/PDF document to Markdown via markitdown."""
    try:
        from markitdown import MarkItDown  # type: ignore
    except Exception:  # noqa: BLE001 - optional at runtime
        logger.debug("markitdown unavailable; skipping %s", path)
        return ""
    try:
        converter = MarkItDown()
        result = converter.convert(str(path))
        return getattr(result, "text_content", "") or ""
    except Exception as exc:  # noqa: BLE001 - never fail a whole build
        logger.warning("Failed to convert %s: %s", path, exc)
        return ""


def extract_text(path: Path) -> tuple[str, str]:
    """Extract indexable text from *path*.

    Args:
        path: File to read.

    Returns:
        ``(text, mode)`` where *mode* is ``text``, ``converted`` or
        ``metadata``.  ``text`` is empty when extraction failed.
    """
    suffix = path.suffix.lower()
    try:
        if path.stat().st_size == 0:
            return "", "empty"
    except OSError:
        return "", "error"

    if suffix in _PLAIN_SUFFIXES:
        return _read_plain(path), "text"

    if suffix in _RICH_SUFFIXES:
        try:
            if path.stat().st_size > _MAX_CONVERT_BYTES:
                return "", "too_large"
        except OSError:
            return "", "error"
        return _convert(path), "converted"

    if suffix in _METADATA_ONLY_SUFFIXES:
        # No OCR: the filename/folder is the only searchable signal.
        return f"{path.parent.name} {path.stem}", "metadata"

    return "", "unsupported"


def chunk_text(
    text: str,
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[str]:
    """Split *text* into overlapping chunks on paragraph boundaries.

    Paragraphs longer than *chunk_size* are split on sentence boundaries
    first and only then hard-cut, so chunks stay readable when quoted
    back to the user.

    Args:
        text: Source text.
        chunk_size: Target characters per chunk.
        overlap: Characters carried over from the previous chunk.

    Returns:
        Non-empty chunk strings.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return []
    chunk_size = max(100, int(chunk_size))
    overlap = max(0, min(int(overlap), chunk_size // 2))

    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [cleaned]

    pieces: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            pieces.append(paragraph)
            continue
        start = 0
        while start < len(paragraph):
            end = min(start + chunk_size, len(paragraph))
            if end < len(paragraph):
                # Prefer to cut at the last sentence terminator.
                window = paragraph[start:end]
                for sep in ("。", "！", "？", ". ", "! ", "? ", "\n"):
                    idx = window.rfind(sep)
                    if idx > chunk_size // 2:
                        end = start + idx + len(sep)
                        break
            pieces.append(paragraph[start:end].strip())
            if end >= len(paragraph):
                break
            start = max(end - overlap, start + 1)

    chunks: list[str] = []
    buffer = ""
    for piece in pieces:
        if not buffer:
            buffer = piece
            continue
        if len(buffer) + 1 + len(piece) <= chunk_size:
            buffer = f"{buffer}\n{piece}"
        else:
            chunks.append(buffer)
            buffer = (
                buffer[-overlap:] + "\n" + piece if overlap else piece
            )
    if buffer:
        chunks.append(buffer)
    return [c for c in chunks if c.strip()]
