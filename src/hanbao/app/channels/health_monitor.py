# -*- coding: utf-8 -*-
"""Channel online/offline health monitor with active reconnection.

[hanbao modification] New hanbao module (no upstream counterpart).

Upstream only reconnects lazily: a channel that loses its long-poll /
WebSocket session stays "down" until the next inbound message happens to
fail.  This monitor polls every channel's ``health_check()`` on a fixed
interval and actively restarts channels that report unhealthy, with
exponential backoff so a permanently broken credential does not turn into
a restart storm.

Secrets are never exposed: the public snapshot contains only channel
names, coarse status strings, counters and **redacted** detail text.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import asyncio
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Statuses considered "down" for the purpose of auto-reconnect.
_UNHEALTHY_STATUSES = frozenset({"unhealthy", "error", "disconnected"})

# Anything that smells like a credential is scrubbed before it leaves the
# process.  Channel implementations own their own error strings, so we
# redact defensively rather than trusting them.
_SECRET_KEY_RE = re.compile(
    r"(?i)\b(token|secret|password|passwd|cookie|api[_-]?key|"
    r"access[_-]?key|authorization|credential|signature|sign)\b"
    r"\s*[=:]\s*\S+",
)
_LONG_OPAQUE_RE = re.compile(r"\b[A-Za-z0-9_\-]{32,}\b")


def redact(text: str | None) -> str:
    """Remove credential-looking substrings from *text*."""
    if not text:
        return ""
    scrubbed = _SECRET_KEY_RE.sub(lambda m: f"{m.group(1)}=***", str(text))
    return _LONG_OPAQUE_RE.sub("***", scrubbed)


@dataclass
class ChannelHealthState:
    """Runtime health bookkeeping for a single channel."""

    channel: str
    status: str = "unknown"
    detail: str = ""
    enabled: bool = True
    last_check_at: float | None = None
    last_ok_at: float | None = None
    last_error: str | None = None
    consecutive_failures: int = 0
    reconnect_count: int = 0
    last_reconnect_at: float | None = None
    next_retry_at: float | None = None
    last_reconnect_error: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe snapshot (no secrets)."""
        return {
            "channel": self.channel,
            "status": self.status,
            "detail": self.detail,
            "enabled": self.enabled,
            "online": self.status == "healthy",
            "last_check_at": self.last_check_at,
            "last_ok_at": self.last_ok_at,
            "last_error": self.last_error,
            "consecutive_failures": self.consecutive_failures,
            "reconnect_count": self.reconnect_count,
            "last_reconnect_at": self.last_reconnect_at,
            "next_retry_at": self.next_retry_at,
            "last_reconnect_error": self.last_reconnect_error,
        }


class ChannelHealthMonitor:
    """Periodically health-checks channels and reconnects broken ones."""

    def __init__(
        self,
        channel_manager,
        agent_id: str = "",
        *,
        interval: float = 60.0,
        failure_threshold: int = 2,
        backoff_base: float = 30.0,
        backoff_max: float = 900.0,
        auto_reconnect: bool = True,
    ):
        self._manager = channel_manager
        self.agent_id = agent_id
        self.interval = max(10.0, float(interval))
        self.failure_threshold = max(1, int(failure_threshold))
        self.backoff_base = max(5.0, float(backoff_base))
        self.backoff_max = max(self.backoff_base, float(backoff_max))
        self.auto_reconnect = bool(auto_reconnect)
        self._states: dict[str, ChannelHealthState] = {}
        self._task: asyncio.Task | None = None
        self._stopping = asyncio.Event()

    # ------------------------------------------------------------------
    # Lifecycle (called by the workspace ServiceManager)
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the background health-check loop."""
        if self._task is not None and not self._task.done():
            return
        self._stopping.clear()
        self._task = asyncio.create_task(
            self._loop(),
            name=f"channel-health-{self.agent_id or 'default'}",
        )
        logger.info(
            "Channel health monitor started (interval=%ss, agent=%s)",
            self.interval,
            self.agent_id,
        )

    async def stop(self) -> None:
        """Stop the background health-check loop."""
        self._stopping.set()
        task = self._task
        self._task = None
        if task is None:
            return
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):  # noqa: BLE001
            pass
        logger.info("Channel health monitor stopped")

    async def _loop(self) -> None:
        # Give channels time to finish their initial handshake.
        try:
            await asyncio.wait_for(
                self._stopping.wait(),
                timeout=min(self.interval, 30.0),
            )
            return
        except asyncio.TimeoutError:
            pass

        while not self._stopping.is_set():
            try:
                await self.check_all()
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001 - monitor must never die
                logger.exception("Channel health check iteration failed")
            try:
                await asyncio.wait_for(
                    self._stopping.wait(),
                    timeout=self.interval,
                )
            except asyncio.TimeoutError:
                continue

    # ------------------------------------------------------------------
    # Checking
    # ------------------------------------------------------------------

    @staticmethod
    def _channel_enabled(channel_instance) -> bool:
        return bool(getattr(channel_instance, "enabled", True))

    @staticmethod
    def _channel_label(channel_instance) -> str:
        return str(getattr(channel_instance, "channel", ""))

    async def check_all(self) -> list[dict[str, Any]]:
        """Health-check every channel once.  Returns the raw snapshot."""
        manager = self._manager
        if manager is None:
            return []

        channels = list(getattr(manager, "channels", []) or [])
        known: set[str] = set()
        results: list[dict[str, Any]] = []

        for instance in channels:
            name = self._channel_label(instance)
            if not name:
                continue
            known.add(name)
            state = self._states.setdefault(
                name,
                ChannelHealthState(channel=name),
            )
            state.enabled = self._channel_enabled(instance)
            await self._check_one(name, state)

        # Channels that are available but not instantiated (e.g. never
        # configured) are reported as offline rather than silently omitted.
        for name in self._available_channels():
            if name in known:
                continue
            state = self._states.setdefault(
                name,
                ChannelHealthState(channel=name),
            )
            state.status = "not_running"
            state.enabled = False
            state.detail = "Channel is not configured or not running."

        for state in self._states.values():
            results.append(state.to_dict())
        results.sort(key=lambda item: item["channel"])
        return results

    async def _check_one(self, name: str, state: ChannelHealthState) -> None:
        manager = self._manager
        now = time.time()
        state.last_check_at = now
        try:
            health = await manager.get_channel_health(name)
        except KeyError:
            state.status = "not_running"
            state.detail = "Channel is not running."
            state.last_check_at = now
            return
        except Exception as exc:  # noqa: BLE001 - health_check may throw
            health = {
                "channel": name,
                "status": "unhealthy",
                "detail": str(exc),
            }

        status = str(health.get("status") or "unknown")
        detail = redact(health.get("detail"))
        state.status = status
        state.detail = detail
        for key, value in health.items():
            if key in {"channel", "status", "detail"}:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                state.extra[redact(str(key))] = (
                    redact(str(value)) if isinstance(value, str) else value
                )

        if status == "healthy":
            state.last_ok_at = now
            state.consecutive_failures = 0
            state.last_error = None
            state.next_retry_at = None
            return

        if status == "disabled":
            # Disabled on purpose — never auto-reconnect.
            state.consecutive_failures = 0
            state.next_retry_at = None
            return

        state.consecutive_failures += 1
        state.last_error = detail or status

        if status not in _UNHEALTHY_STATUSES:
            return
        if not self.auto_reconnect or not state.enabled:
            return
        if state.consecutive_failures < self.failure_threshold:
            return
        if state.next_retry_at and now < state.next_retry_at:
            return

        await self._reconnect(name, state)

    async def _reconnect(self, name: str, state: ChannelHealthState) -> None:
        """Restart *name* and schedule the next attempt with backoff."""
        now = time.time()
        delay = min(
            self.backoff_base
            * (2 ** min(state.reconnect_count, 5)),
            self.backoff_max,
        )
        try:
            result = await self._manager.restart_channel(name)
            state.reconnect_count += 1
            state.last_reconnect_at = now
            state.last_reconnect_error = None
            state.consecutive_failures = 0
            state.status = "reconnecting"
            state.detail = redact(
                str(result.get("detail") if result else "")
                or "Reconnect requested.",
            )
            logger.warning(
                "Auto-reconnected channel '%s' (attempt #%s)",
                name,
                state.reconnect_count,
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - never crash the monitor
            state.reconnect_count += 1
            state.last_reconnect_at = now
            state.last_reconnect_error = redact(str(exc))
            state.detail = f"Reconnect failed: {redact(str(exc))}"
            logger.warning(
                "Auto-reconnect failed for channel '%s': %s",
                name,
                redact(str(exc)),
            )
        state.next_retry_at = now + delay

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def _available_channels(self) -> set[str]:
        try:
            from ...config import get_available_channels

            return set(get_available_channels() or ())
        except Exception:  # pragma: no cover - defensive
            return set()

    def snapshot(self) -> list[dict[str, Any]]:
        """Return the last known state without performing a new check."""
        items = [state.to_dict() for state in self._states.values()]
        for name in self._available_channels():
            if any(item["channel"] == name for item in items):
                continue
            items.append(
                ChannelHealthState(
                    channel=name,
                    status="not_running",
                    enabled=False,
                    detail="Channel is not configured or not running.",
                ).to_dict(),
            )
        items.sort(key=lambda item: item["channel"])
        return items

    def state_for(self, channel_name: str) -> ChannelHealthState | None:
        """Return the mutable state object for *channel_name*."""
        return self._states.get(channel_name)

    async def reconnect(
        self,
        channel_name: str,
        *,
        force: bool = True,
    ) -> dict[str, Any]:
        """Manually trigger a reconnect for *channel_name*.

        Args:
            channel_name: Channel identifier.
            force: When True, ignore the backoff cooldown.

        Returns:
            Dict with ``ok``, ``channel``, ``detail`` and the counters.
        """
        state = self._states.setdefault(
            channel_name,
            ChannelHealthState(channel=channel_name),
        )
        if force:
            state.next_retry_at = None
        elif state.next_retry_at and time.time() < state.next_retry_at:
            return {
                "ok": False,
                "channel": channel_name,
                "detail": "Reconnect is cooling down; try again shortly.",
                **state.to_dict(),
            }
        if self._manager is None:
            return {
                "ok": False,
                "channel": channel_name,
                "detail": "Channel manager is not available.",
                **state.to_dict(),
            }
        await self._reconnect(channel_name, state)
        return {
            "ok": state.last_reconnect_error is None,
            "channel": channel_name,
            "detail": state.detail,
            **state.to_dict(),
        }
