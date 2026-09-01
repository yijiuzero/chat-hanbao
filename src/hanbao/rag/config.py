# -*- coding: utf-8 -*-
# [hanbao modification]
"""Configuration for the hanbao local knowledge base (RAG).

This module is new hanbao code (no upstream counterpart).

Design note — **zero new dependencies, zero network**:

* Text extraction reuses ``markitdown`` (MIT), already a hanbao
  dependency for the document tools (I-019).  BM25 and the CJK tokenizer
  are implemented here in pure Python.
* Retrieval is lexical (BM25) only.  No embedding calls are made, so
  document text never leaves the NAS.  Adding a cloud embedding would
  violate hanbao's "家庭数据不出 NAS" guarantee, which is why it is not
  offered.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

CONFIG_FILENAME = "knowledge.json"


class KnowledgeConfig(BaseModel):
    """User-editable knowledge base settings."""

    enabled: bool = Field(
        default=False,
        description="Enable the local knowledge base",
    )
    source_dirs: list[str] = Field(
        default_factory=list,
        description=(
            "Local directories to index (e.g. family documents, "
            "bills). Everything stays on this device."
        ),
    )
    include_globs: list[str] = Field(
        default_factory=lambda: [
            "*.md",
            "*.txt",
            "*.pdf",
            "*.docx",
            "*.doc",
            "*.pptx",
            "*.xlsx",
            "*.csv",
            "*.json",
            "*.html",
            "*.htm",
            "*.log",
            "*.yaml",
            "*.yml",
        ],
        description="Filename patterns to index",
    )
    exclude_globs: list[str] = Field(
        default_factory=lambda: [
            "**/.git/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.hanbao*",
            "**/.DS_Store",
            "**/working.secret/**",
            "**/.hanbao.secret/**",
        ],
        description="Patterns that are always skipped",
    )
    max_file_mb: int = Field(
        default=20,
        ge=1,
        le=200,
        description="Files larger than this are skipped",
    )
    chunk_size: int = Field(
        default=700,
        ge=100,
        le=4000,
        description="Approximate characters per chunk",
    )
    chunk_overlap: int = Field(
        default=120,
        ge=0,
        le=1000,
        description="Overlapping characters between chunks",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Default number of chunks returned per query",
    )
    min_score: float = Field(
        default=1.0,
        ge=0.0,
        description="Discard BM25 hits scoring below this",
    )


def config_path(working_dir: str | Path) -> Path:
    """Return the path of the knowledge config file."""
    return Path(working_dir) / CONFIG_FILENAME


def load_knowledge_config(working_dir: str | Path) -> KnowledgeConfig:
    """Load the knowledge config, falling back to defaults."""
    path = config_path(working_dir)
    if not path.is_file():
        return KnowledgeConfig()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return KnowledgeConfig()
    if not isinstance(raw, dict):
        return KnowledgeConfig()
    try:
        return KnowledgeConfig.model_validate(raw)
    except Exception:  # noqa: BLE001 - never block startup on bad config
        return KnowledgeConfig()


def save_knowledge_config(
    working_dir: str | Path,
    config: KnowledgeConfig,
) -> None:
    """Persist *config* atomically."""
    path = config_path(working_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(
            config.model_dump(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    tmp.replace(path)


def config_fingerprint(config: KnowledgeConfig) -> str:
    """Return a short hash used to detect config changes."""
    import hashlib

    payload = json.dumps(
        {
            "dirs": sorted(config.source_dirs),
            "include": sorted(config.include_globs),
            "exclude": sorted(config.exclude_globs),
            "chunk": config.chunk_size,
            "overlap": config.chunk_overlap,
            "max_mb": config.max_file_mb,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def describe_config(config: KnowledgeConfig) -> dict[str, Any]:
    """Return a UI-friendly summary of *config*."""
    return {
        "enabled": config.enabled,
        "source_dirs": list(config.source_dirs),
        "top_k": config.top_k,
        "chunk_size": config.chunk_size,
        "max_file_mb": config.max_file_mb,
    }
