# -*- coding: utf-8 -*-
"""Local fnOS (Feiniu NAS) integration API for the hanbao console.

[hanbao modification] New hanbao router (no upstream counterpart).

Everything under /api/ is covered by AuthMiddleware.  The fnOS token is stored
only in the agent workspace and is never returned to the browser (see
mask_config).  All calls are local to the NAS and degrade gracefully.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import BaseModel, Field

from ..agent_context import get_agent_for_request
from ...fnos.client import coerce_items, get_client
from ...fnos.config import (
    FnOSConfig,
    load_fnos_config,
    mask_config,
    save_fnos_config,
)

router = APIRouter(prefix="/fnos", tags=["fnos"])


class FnOSConfigUpdate(BaseModel):
    """Body for updating the fnOS connection config."""

    enabled: bool | None = None
    host: str | None = None
    token: str | None = None
    timeout: int | None = Field(None, ge=1, le=30)


async def _config(request: Request) -> FnOSConfig:
    """Load the fnOS config for the request's active agent."""
    workspace = await get_agent_for_request(request)
    return load_fnos_config(workspace.workspace_dir)


@router.get(
    "/status",
    summary="fnOS connection status",
    description=(
        "Connection state plus UI-safe config (token masked). Local only."
    ),
)
async def fnos_status(request: Request) -> dict[str, Any]:
    """Return the fnOS connection status."""
    config = await _config(request)
    client = get_client(config)
    connected = False
    error = None
    if client is not None:
        res = client.ping()
        connected = res.ok
        error = res.error
    return {
        **mask_config(config),
        "connected": connected,
        "error": error,
    }


@router.put(
    "/config",
    summary="Update fnOS config",
    description="Update the local fnOS connection settings",
)
async def update_fnos_config(
    request: Request,
    body: FnOSConfigUpdate = Body(...),
) -> dict[str, Any]:
    """Update and persist the fnOS config."""
    workspace = await get_agent_for_request(request)
    current = load_fnos_config(workspace.workspace_dir)
    payload = body.model_dump(exclude_unset=True)
    merged = current.model_copy(update=payload)
    try:
        save_fnos_config(workspace.workspace_dir, merged)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save fnOS config: {exc}",
        ) from exc
    return mask_config(merged)


@router.get(
    "/media",
    summary="List fnOS media library",
    description="Search the local media library (movies / TV). Local only.",
)
async def fnos_media(
    request: Request,
    query: str = Query("", description="Optional keyword"),
) -> dict[str, Any]:
    """Return media library items, or a graceful 'unavailable' payload."""
    config = await _config(request)
    client = get_client(config)
    if client is None:
        return {"available": False, "reason": "fnOS 未启用", "items": []}
    res = client.list_media(query or None)
    if not res.ok:
        return {"available": False, "reason": res.error, "items": []}
    return {"available": True, "items": coerce_items(res.data)}


@router.get(
    "/files",
    summary="Browse fnOS files",
    description="Browse a directory on the NAS file system. Local only.",
)
async def fnos_files(
    request: Request,
    path: str = Query("/", description="Directory path to browse"),
) -> dict[str, Any]:
    """Return file entries, or a graceful 'unavailable' payload."""
    config = await _config(request)
    client = get_client(config)
    if client is None:
        return {"available": False, "reason": "fnOS 未启用", "items": []}
    res = client.list_files(path)
    if not res.ok:
        return {"available": False, "reason": res.error, "items": []}
    return {"available": True, "items": coerce_items(res.data)}


@router.get(
    "/downloads",
    summary="List fnOS download tasks",
    description="List fnOS download tasks. Local only.",
)
async def fnos_downloads(request: Request) -> dict[str, Any]:
    """Return download tasks, or a graceful 'unavailable' payload."""
    config = await _config(request)
    client = get_client(config)
    if client is None:
        return {"available": False, "reason": "fnOS 未启用", "items": []}
    res = client.list_downloads()
    if not res.ok:
        return {"available": False, "reason": res.error, "items": []}
    return {"available": True, "items": coerce_items(res.data)}
