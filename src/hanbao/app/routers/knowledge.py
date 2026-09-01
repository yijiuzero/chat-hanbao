# -*- coding: utf-8 -*-
"""Local knowledge base (RAG) API for the hanbao console.

[hanbao modification] New hanbao router (no upstream counterpart).

Everything under ``/api/`` is covered by ``AuthMiddleware``, and the
knowledge base is explicitly *local*: indexing and search perform no
outbound network requests at all.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, Request
from pydantic import BaseModel, Field

from ..agent_context import get_agent_for_request
from ...rag.config import KnowledgeConfig
from ...rag.service import get_knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeConfigUpdate(BaseModel):
    """Body for updating the knowledge base configuration."""

    enabled: bool | None = Field(None, description="Enable/disable")
    source_dirs: list[str] | None = Field(
        None,
        description="Local directories to index",
    )
    include_globs: list[str] | None = None
    exclude_globs: list[str] | None = None
    max_file_mb: int | None = Field(None, ge=1, le=200)
    chunk_size: int | None = Field(None, ge=100, le=4000)
    chunk_overlap: int | None = Field(None, ge=0, le=1000)
    top_k: int | None = Field(None, ge=1, le=50)
    min_score: float | None = Field(None, ge=0.0)


class KnowledgeSearchRequest(BaseModel):
    """Body for a knowledge search."""

    query: str = Field(..., min_length=1, description="Search query")
    top_k: int | None = Field(None, ge=1, le=50, description="Result count")


async def _service(request: Request):
    """Return the knowledge service for the active agent."""
    workspace = await get_agent_for_request(request)
    return get_knowledge_service(workspace.workspace_dir)


@router.get(
    "/status",
    summary="Knowledge base status",
    description="Config plus index statistics (files, chunks, last build)",
)
async def get_status(request: Request) -> dict[str, Any]:
    """Return the knowledge base status."""
    service = await _service(request)
    return await service.status()


@router.get(
    "/config",
    summary="Get knowledge base config",
)
async def get_config(request: Request) -> KnowledgeConfig:
    """Return the knowledge base configuration."""
    service = await _service(request)
    return service.get_config()


@router.put(
    "/config",
    summary="Update knowledge base config",
    description="Update one or more knowledge base settings",
)
async def update_config(
    request: Request,
    body: KnowledgeConfigUpdate,
) -> KnowledgeConfig:
    """Update the knowledge base configuration."""
    service = await _service(request)
    current = service.get_config()
    payload = body.model_dump(exclude_unset=True)
    merged = current.model_copy(update=payload)
    try:
        return service.update_config(merged)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save knowledge config: {exc}",
        ) from exc


@router.post(
    "/build",
    summary="Build the knowledge index",
    description=(
        "Index the configured local directories. Runs in the background; "
        "poll /knowledge/status for progress."
    ),
)
async def build_index(
    request: Request,
    rebuild: bool = Query(
        False,
        description="Ignore cached files and re-extract everything",
    ),
) -> dict[str, Any]:
    """Build or refresh the knowledge index."""
    service = await _service(request)
    if service.is_building:
        return {
            "ok": False,
            "error": "A build is already running",
        }
    config = service.get_config()
    if not config.source_dirs:
        raise HTTPException(
            status_code=400,
            detail="No source directories configured",
        )
    return await service.build(rebuild=rebuild)


@router.post(
    "/search",
    summary="Search the knowledge base",
    description="BM25 search over the indexed local documents",
)
async def search_knowledge(
    request: Request,
    body: KnowledgeSearchRequest = Body(...),
) -> dict[str, Any]:
    """Search the local knowledge base."""
    service = await _service(request)
    return await service.search(body.query, top_k=body.top_k)


@router.get(
    "/sources",
    summary="List indexed files",
)
async def list_sources(request: Request) -> dict[str, Any]:
    """Return the indexed file list."""
    service = await _service(request)
    return {"sources": await service.sources()}


@router.delete(
    "/index",
    summary="Delete the knowledge index",
    description="Drop the index (source documents are untouched)",
)
async def clear_index(request: Request) -> dict[str, Any]:
    """Delete the knowledge index."""
    service = await _service(request)
    return await service.clear()
