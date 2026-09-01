# -*- coding: utf-8 -*-
"""Aggregated channel online/offline status API.

[hanbao modification] New hanbao router (no upstream counterpart).

Complements the existing per-channel ``/api/channels/{name}/health`` and
``/api/channels/{name}/restart`` endpoints (see ``routers/config.py``) by
exposing the **monitor's** bookkeeping in one call: online flag, last
successful heartbeat, consecutive failures, reconnect count and the next
scheduled retry.

Responses are guaranteed secret-free — every free-text field passes
through :func:`redact` before it leaves the process.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Path, Query, Request
from pydantic import BaseModel, Field

from ..agent_context import get_agent_for_request
from ..channels.health_monitor import (
    ChannelHealthMonitor,
    ChannelHealthState,
    redact,
)

router = APIRouter(prefix="/channels-status", tags=["channels-status"])


class ChannelStatus(BaseModel):
    """Public channel status payload (no credentials)."""

    channel: str = Field(..., description="Channel identifier")
    status: str = Field(..., description="healthy/unhealthy/disabled/…")
    online: bool = Field(False, description="Whether the channel is online")
    enabled: bool = Field(True, description="Whether it is enabled")
    detail: str = Field("", description="Redacted status detail")
    last_check_at: float | None = Field(None, description="Epoch seconds")
    last_ok_at: float | None = Field(None, description="Last heartbeat")
    last_error: str | None = Field(None, description="Redacted last error")
    consecutive_failures: int = Field(0, description="Failed checks in a row")
    reconnect_count: int = Field(0, description="Reconnect attempts")
    last_reconnect_at: float | None = Field(None, description="Epoch seconds")
    next_retry_at: float | None = Field(None, description="Epoch seconds")
    last_reconnect_error: str | None = Field(
        None,
        description="Redacted reconnect error",
    )


class ChannelStatusList(BaseModel):
    """Aggregated status for every channel."""

    agent_id: str = Field("", description="Active agent id")
    monitoring: bool = Field(False, description="Monitor running")
    channels: list[ChannelStatus] = Field(default_factory=list)


async def _monitor(request: Request) -> ChannelHealthMonitor | None:
    """Return the health monitor for the request's active agent."""
    workspace = await get_agent_for_request(request)
    return workspace.channel_health_monitor


@router.get(
    "",
    response_model=ChannelStatusList,
    summary="Channel online status",
    description=(
        "Online/offline status, last heartbeat and reconnect counters "
        "for every channel"
    ),
)
async def list_channel_status(
    request: Request,
    refresh: bool = Query(
        False,
        description="Run a live health check instead of the cached state",
    ),
) -> ChannelStatusList:
    """Return the aggregated channel status snapshot."""
    workspace = await get_agent_for_request(request)
    monitor = workspace.channel_health_monitor
    if monitor is None:
        return ChannelStatusList(agent_id=workspace.agent_id)

    if refresh:
        rows = await monitor.check_all()
    else:
        rows = monitor.snapshot()
    return ChannelStatusList(
        agent_id=workspace.agent_id,
        monitoring=True,
        channels=[ChannelStatus(**row) for row in rows],
    )


@router.get(
    "/{channel_name}",
    response_model=ChannelStatus,
    summary="Single channel status",
    description="Status of one channel from the health monitor",
)
async def get_channel_status(
    request: Request,
    channel_name: str = Path(..., min_length=1),
) -> ChannelStatus:
    """Return one channel's status."""
    monitor = await _monitor(request)
    if monitor is None:
        raise HTTPException(
            status_code=503,
            detail="Channel health monitor is not running",
        )
    state: ChannelHealthState | None = monitor.state_for(channel_name)
    if state is None:
        rows = await monitor.check_all()
        row = next(
            (r for r in rows if r["channel"] == channel_name),
            None,
        )
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Channel '{channel_name}' not found",
            )
        return ChannelStatus(**row)
    return ChannelStatus(**state.to_dict())


@router.post(
    "/{channel_name}/reconnect",
    summary="Reconnect a channel",
    description=(
        "Force an immediate reconnect, ignoring the backoff cooldown"
    ),
)
async def reconnect_channel(
    request: Request,
    channel_name: str = Path(..., min_length=1),
    force: bool = Query(
        True,
        description="Ignore the backoff cooldown",
    ),
) -> dict[str, Any]:
    """Trigger a reconnect for one channel."""
    monitor = await _monitor(request)
    if monitor is None:
        raise HTTPException(
            status_code=503,
            detail="Channel health monitor is not running",
        )
    try:
        result = await monitor.reconnect(channel_name, force=force)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Channel '{channel_name}' not found",
        ) from exc
    result["detail"] = redact(result.get("detail"))
    return result
