# -*- coding: utf-8 -*-
"""Local fnOS (Feiniu NAS) HTTP client with graceful degradation.

[hanbao modification] New hanbao module (no upstream counterpart).

The client only talks to the fnOS instance configured by the user (the NAS
itself). Every call is wrapped so a missing/unreachable fnOS returns a
structured error instead of raising — the rest of hanbao keeps working.

NOTE: fnOS REST endpoint paths are best-effort defaults. fnOS versions differ;
adjust the *_PATH constants below to match the API exposed by your NAS. Because
all access is local and optional, a wrong path simply yields an empty /
unavailable result rather than a crash.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

# Best-effort fnOS endpoints. Adjust to your fnOS version if needed.
MEDIA_PATH = "/v1/media/movies"
FILES_PATH = "/v1/files"
DOWNLOADS_PATH = "/v1/download/list"


@dataclass
class FnOSResult:
    """Result of a single fnOS call."""

    ok: bool
    data: Any = None
    error: str | None = None


class FnOSClient:
    """Tiny local HTTP client for the fnOS REST API."""

    def __init__(self, host: str, token: str = "", timeout: int = 8):
        self.base_url = (host or "http://localhost:5666").rstrip("/")
        self.token = token or ""
        self.timeout = max(1, min(int(timeout or 8), 30))

    def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        body: Any = None,
    ) -> FnOSResult:
        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8", "replace")
                if not raw.strip():
                    return FnOSResult(True, {})
                try:
                    return FnOSResult(True, json.loads(raw))
                except json.JSONDecodeError:
                    return FnOSResult(True, {"raw": raw})
        except urllib.error.HTTPError as exc:
            return FnOSResult(False, None, f"HTTP {exc.code}: {exc.reason}")
        except (
            urllib.error.URLError,
            socket.timeout,
            ConnectionError,
            OSError,
        ) as exc:
            return FnOSResult(False, None, f"连接失败: {exc}")

    def ping(self) -> FnOSResult:
        """Best-effort connectivity probe."""
        return self._request("GET", "/")

    def list_media(self, query: str | None = None) -> FnOSResult:
        """List / search the local media library."""
        params = {"keyword": query} if query else None
        return self._request("GET", MEDIA_PATH, params=params)

    def list_files(self, path: str = "/") -> FnOSResult:
        """Browse a directory on fnOS file system."""
        return self._request("GET", FILES_PATH, params={"path": path})

    def list_downloads(self) -> FnOSResult:
        """List fnOS download tasks."""
        return self._request("GET", DOWNLOADS_PATH)


def get_client(config) -> "FnOSClient | None":
    """Build a client from *config*, or None when disabled."""
    if not getattr(config, "enabled", False):
        return None
    return FnOSClient(config.host, config.token, config.timeout)


def coerce_items(data: Any) -> list[dict]:
    """Best-effort flatten of an fnOS response into a list of dicts."""
    if data is None:
        return []
    if isinstance(data, list):
        return [d if isinstance(d, dict) else {"value": d} for d in data]
    if isinstance(data, dict):
        for key in ("items", "list", "data", "results"):
            if key in data and isinstance(data[key], list):
                return [
                    d if isinstance(d, dict) else {"value": d}
                    for d in data[key]
                ]
        return [data]
    return [{"value": data}]
