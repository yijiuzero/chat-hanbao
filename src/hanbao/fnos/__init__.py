# -*- coding: utf-8 -*-
# [hanbao modification]
"""hanbao local fnOS (Feiniu NAS) integration.

This package is new hanbao code (no upstream counterpart).  All access is
strictly local to the user's NAS; no data leaves the device.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""

from .client import FnOSClient, FnOSResult, get_client
from .config import (
    FnOSConfig,
    load_fnos_config,
    mask_config,
    save_fnos_config,
)

__all__ = [
    "FnOSClient",
    "FnOSResult",
    "FnOSConfig",
    "get_client",
    "load_fnos_config",
    "save_fnos_config",
    "mask_config",
]
