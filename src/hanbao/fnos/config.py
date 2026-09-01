# -*- coding: utf-8 -*-
"""Local fnOS (Feiniu NAS) integration configuration.

[hanbao modification] New hanbao module (no upstream counterpart).

All fnOS access is strictly local: the configured host is the NAS itself
(default http://localhost:5666) and the optional token is stored only in the
agent workspace (fnos.json) — it is never returned to the browser and never
leaves the device. If fnOS is unreachable the integration degrades gracefully
(see client.py) instead of raising.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

CONFIG_FILENAME = "fnos.json"


class FnOSConfig(BaseModel):
    """User-editable fnOS connection settings (local only)."""

    enabled: bool = Field(
        default=False,
        description="Enable local fnOS integration",
    )
    host: str = Field(
        default="http://localhost:5666",
        description="fnOS base URL (the NAS itself, not a public host)",
    )
    token: str = Field(
        default="",
        description=(
            "Optional fnOS API token. Stored locally in the workspace; "
            "never exposed to the UI or sent off-device."
        ),
    )
    timeout: int = Field(
        default=8,
        ge=1,
        le=30,
        description="Per-request timeout in seconds",
    )


def config_path(working_dir: str | Path) -> Path:
    """Return the path of the fnOS config file."""
    return Path(working_dir) / CONFIG_FILENAME


def load_fnos_config(working_dir: str | Path) -> FnOSConfig:
    """Load the fnOS config, falling back to defaults."""
    path = config_path(working_dir)
    if not path.is_file():
        return FnOSConfig()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return FnOSConfig()
    if not isinstance(raw, dict):
        return FnOSConfig()
    try:
        return FnOSConfig.model_validate(raw)
    except Exception:  # noqa: BLE001 - never block startup on bad config
        return FnOSConfig()


def save_fnos_config(working_dir: str | Path, config: FnOSConfig) -> None:
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


def mask_config(config: FnOSConfig) -> dict:
    """Return a UI-safe view (token replaced with a boolean flag)."""
    return {
        "enabled": config.enabled,
        "host": config.host,
        "timeout": config.timeout,
        "token_set": bool(config.token),
    }
