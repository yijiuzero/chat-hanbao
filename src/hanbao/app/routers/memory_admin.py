# -*- coding: utf-8 -*-
"""Memory & profile administration API for the hanbao console.

[hanbao modification] New hanbao router (no upstream counterpart).

All endpoints live under ``/api/`` and are therefore covered by
``AuthMiddleware`` — memory content is personal data and must never be
reachable without a session, even on a home LAN.

Read/write goes exclusively through ``MemoryBrowser``, which keeps every
edit inside the memory vault and records an append-only audit entry.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import BaseModel, Field

from ..agent_context import get_agent_for_request
from ...agents.memory.memory_browser import (
    SOURCE_TAGS,
    MemoryBrowser,
    MemoryBrowserError,
)
from ...config import load_config

router = APIRouter(prefix="/memory-admin", tags=["memory-admin"])


# ── Schemas ────────────────────────────────────────────────────────────────


class MemoryEntryDeleteRequest(BaseModel):
    """Request body for deleting one memory entry."""

    file: str = Field(..., description="Vault-relative .md path")
    line: int = Field(..., ge=1, description="1-based line number")
    text: str = Field(
        default="",
        description="Text currently on that line (optimistic guard)",
    )


class MemoryEntryUpdateRequest(BaseModel):
    """Request body for correcting one memory entry."""

    file: str = Field(..., description="Vault-relative .md path")
    line: int = Field(..., ge=1, description="1-based line number")
    new_text: str = Field(..., min_length=1, description="Replacement text")
    text: str = Field(
        default="",
        description="Text currently on that line (optimistic guard)",
    )
    source: str | None = Field(
        default=None,
        description=f"Source tag to apply: {', '.join(SOURCE_TAGS)}",
    )


# ── Helpers ────────────────────────────────────────────────────────────────


async def _browser(request: Request) -> MemoryBrowser:
    """Build a :class:`MemoryBrowser` for the request's active agent."""
    workspace = await get_agent_for_request(request)
    agent_config = getattr(workspace, "_config", None)
    daily_dir = "memory"
    digest_dir = "digest"
    if agent_config is not None:
        try:
            reme = agent_config.running.reme_light_memory_config
            daily_dir = reme.daily_dir or daily_dir
            digest_dir = reme.digest_dir or digest_dir
        except Exception:  # pragma: no cover - defensive
            pass
    return MemoryBrowser(
        workspace.workspace_dir,
        agent_id=workspace.agent_id,
        daily_dir=daily_dir,
        digest_dir=digest_dir,
    )


async def _user_timezone() -> str | None:
    try:
        return getattr(load_config(), "user_timezone", None)
    except Exception:  # pragma: no cover - defensive
        return None


def _translate_error(exc: MemoryBrowserError) -> HTTPException:
    message = str(exc)
    lowered = message.lower()
    # Path-safety rejections are client errors; anything else is a 500.
    if (
        "escapes" in lowered
        or "invalid" in lowered
        or "not a memory file" in lowered
        or "not inside" in lowered
        or "line must be" in lowered
        or "must not be empty" in lowered
        or "unsupported source tag" in lowered
        or "structural" in lowered
        or "changed since" in lowered
        or "only .md" in lowered
    ):
        return HTTPException(status_code=400, detail=message)
    return HTTPException(status_code=500, detail=message)


# ── Endpoints ──────────────────────────────────────────────────────────────


@router.get(
    "/entries",
    summary="List memory entries",
    description=(
        "List individual memory / profile entries with source tag, date "
        "and staleness hint"
    ),
)
async def list_memory_entries(
    request: Request,
    q: str = Query("", description="Substring filter on entry text"),
    source: str = Query("", description="Filter by source tag"),
    file: str = Query("", description="Filter by vault-relative file"),
    include_deprecated: bool = Query(
        True,
        description="Include entries marked [已废弃]",
    ),
    limit: int = Query(200, ge=1, le=500, description="Max entries"),
) -> dict[str, Any]:
    """Return individual memory entries for the active agent."""
    browser = await _browser(request)
    tz = await _user_timezone()
    entries = await _run(
        browser.list_entries,
        query=q,
        source=source,
        file=file,
        include_deprecated=include_deprecated,
        limit=limit,
        user_timezone=tz,
    )
    return {"entries": entries, "count": len(entries)}


@router.get(
    "/stats",
    summary="Memory statistics",
    description="Aggregate counts by source tag for the memory panel",
)
async def memory_stats(request: Request) -> dict[str, Any]:
    """Return aggregate memory statistics."""
    browser = await _browser(request)
    tz = await _user_timezone()
    return await _run(browser.stats, user_timezone=tz)


@router.get(
    "/files",
    summary="List memory files",
    description="List the Markdown files that make up the memory vault",
)
async def list_memory_files(request: Request) -> dict[str, Any]:
    """Return the vault file list (for the panel's file filter)."""
    browser = await _browser(request)
    paths = await _run(browser.vault_files)
    return {
        "files": [
            browser.rel_path(p, browser.working_dir) for p in paths
        ],
    }


@router.post(
    "/entries/delete",
    summary="Delete one memory entry",
    description="Remove a single memory line (audited, vault-contained)",
)
async def delete_memory_entry(
    request: Request,
    body: MemoryEntryDeleteRequest = Body(...),
) -> dict[str, Any]:
    """Delete a single memory entry."""
    browser = await _browser(request)
    try:
        return await _run(
            browser.delete_entry,
            body.file,
            body.line,
            body.text,
        )
    except MemoryBrowserError as exc:
        raise _translate_error(exc) from exc


@router.post(
    "/entries/update",
    summary="Correct one memory entry",
    description="Replace a single memory line (audited, vault-contained)",
)
async def update_memory_entry(
    request: Request,
    body: MemoryEntryUpdateRequest = Body(...),
) -> dict[str, Any]:
    """Correct a single memory entry in place."""
    browser = await _browser(request)
    try:
        return await _run(
            browser.update_entry,
            body.file,
            body.line,
            body.new_text,
            body.text,
            body.source,
        )
    except MemoryBrowserError as exc:
        raise _translate_error(exc) from exc


async def _run(fn, *args, **kwargs):
    """Run a blocking vault operation off the event loop."""
    import asyncio

    def _call():
        return fn(*args, **kwargs)

    return await asyncio.to_thread(_call)
