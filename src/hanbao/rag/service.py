# -*- coding: utf-8 -*-
# [hanbao modification]
"""Async service wrapper for the hanbao local knowledge base.

This module is new hanbao code (no upstream counterpart).

Index building is CPU/IO bound (MarkItDown conversion in particular), so
every call is off-loaded to a worker thread via ``asyncio.to_thread`` and
serialised by a per-workspace lock.  One service instance is cached per
workspace directory.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import asyncio
import logging
import threading
from pathlib import Path
from typing import Any

from .config import (
    KnowledgeConfig,
    config_fingerprint,
    load_knowledge_config,
    save_knowledge_config,
)
from .store import KnowledgeStore

logger = logging.getLogger(__name__)

_services: dict[str, "KnowledgeService"] = {}
_services_lock = threading.Lock()


class KnowledgeService:
    """Per-workspace knowledge base facade."""

    def __init__(self, working_dir: str | Path):
        self.working_dir = Path(working_dir)
        self.store = KnowledgeStore(self.working_dir)
        self._build_lock = asyncio.Lock()
        self._building = False
        self._last_result: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def get_config(self) -> KnowledgeConfig:
        """Return the persisted knowledge configuration."""
        return load_knowledge_config(self.working_dir)

    def update_config(self, config: KnowledgeConfig) -> KnowledgeConfig:
        """Persist *config* and return it."""
        save_knowledge_config(self.working_dir, config)
        return config

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    @property
    def is_building(self) -> bool:
        """Whether a build is currently running."""
        return self._building

    async def build(
        self,
        *,
        rebuild: bool = False,
    ) -> dict[str, Any]:
        """Build or refresh the index in a worker thread."""
        async with self._build_lock:
            self._building = True
            try:
                config = load_knowledge_config(self.working_dir)
                fingerprint = config_fingerprint(config)
                result = await asyncio.to_thread(
                    self.store.build,
                    config,
                    rebuild=rebuild,
                    fingerprint=fingerprint,
                )
                self._last_result = result
                return result
            except Exception as exc:  # noqa: BLE001 - report, never crash
                logger.exception("Knowledge index build failed")
                return {"ok": False, "error": str(exc)}
            finally:
                self._building = False

    # ------------------------------------------------------------------
    # Query / introspection
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        *,
        top_k: int | None = None,
    ) -> dict[str, Any]:
        """Search the index.  Returns ``{"results": [...], "enabled": …}``."""
        config = load_knowledge_config(self.working_dir)
        if not config.enabled:
            return {
                "enabled": False,
                "results": [],
                "reason": "Knowledge base is disabled",
            }
        limit = top_k or config.top_k
        results = await asyncio.to_thread(
            self.store.search,
            query,
            top_k=limit,
            min_score=config.min_score,
        )
        return {
            "enabled": True,
            "query": query,
            "count": len(results),
            "results": results,
        }

    async def status(self) -> dict[str, Any]:
        """Return config + index status for the console."""
        config = load_knowledge_config(self.working_dir)
        stats = await asyncio.to_thread(self.store.status)
        return {
            "config": config.model_dump(),
            "index": stats,
            "building": self._building,
            "last_build": self._last_result,
        }

    async def sources(self) -> list[dict[str, Any]]:
        """Return the indexed file list."""
        return await asyncio.to_thread(self.store.sources)

    async def clear(self) -> dict[str, Any]:
        """Delete the index."""
        await asyncio.to_thread(self.store.clear)
        self._last_result = None
        return {"ok": True}


def get_knowledge_service(working_dir: str | Path) -> KnowledgeService:
    """Return the cached :class:`KnowledgeService` for *working_dir*."""
    key = str(Path(working_dir).resolve(strict=False))
    with _services_lock:
        service = _services.get(key)
        if service is None:
            service = KnowledgeService(key)
            _services[key] = service
        return service


def reset_knowledge_services() -> None:
    """Drop the service cache (tests / reload)."""
    with _services_lock:
        _services.clear()
