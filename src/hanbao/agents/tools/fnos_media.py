# -*- coding: utf-8 -*-
"""Tool: search the local fnOS media library.

[hanbao modification] New hanbao tool (no upstream counterpart).

Only talks to the user's own fnOS on the NAS.  When fnOS is disabled or
unreachable the tool returns a helpful message instead of an error so the agent
can keep the conversation going.

Copyright 2026 hanbao contributors
Licensed under the Apache License, Version 2.0
"""
from agentscope.message import TextBlock, ToolResultState
from agentscope.tool import ToolChunk

from ...config.context import get_current_workspace_dir
from ...constant import WORKING_DIR
from ...fnos.client import coerce_items, get_client
from ...fnos.config import load_fnos_config
from ...runtime.tool_registry import tool_descriptor


@tool_descriptor(
    async_execution=True,
    tool_type="internal",
    policy_name="FnOSMedia",
    ui_description="Search local fnOS media library",
    ui_icon="🎬",
)
async def search_fnos_media(query: str, top_k: int = 5) -> ToolChunk:
    """Search the family's local fnOS media library (movies / TV).

    Use this when the user asks what's in their media library, whether a
    movie or show is downloaded, or wants suggestions from their own
    collection. All access is local to the NAS.

    Args:
        query: What to look for, in the user's own words.
        top_k: How many items to return (default 5, max 10).

    Returns:
        ToolChunk with matching media titles and metadata.
    """
    workspace_dir = get_current_workspace_dir() or WORKING_DIR
    limit = max(1, min(int(top_k or 5), 10))
    try:
        config = load_fnos_config(workspace_dir)
        client = get_client(config)
        if client is None:
            return _chunk(
                "本地飞牛影视库尚未启用。可在控制台「飞牛联动」页填写飞牛地址并"
                "启用后，我才能检索你的影视库。",
                ok=False,
            )
        res = client.list_media(query)
        if not res.ok:
            return _chunk(
                f"暂时无法连接飞牛影视库：{res.error}。"
                "请检查控制台「飞牛联动」的连接设置。",
                ok=False,
            )
        items = coerce_items(res.data)[:limit]
        if not items:
            return _chunk(
                f"飞牛影视库中没有找到与「{query}」相关的内容。",
            )
        lines = [f"本地飞牛影视库命中 {len(items)} 条（数据不出本机）：", ""]
        for i, item in enumerate(items, 1):
            title = (
                item.get("title")
                or item.get("name")
                or item.get("value")
                or "未命名"
            )
            lines.append(f"[{i}] {title}")
        return _chunk("\n".join(lines))
    except Exception as exc:  # noqa: BLE001 - degrade, never crash the agent
        return _chunk(f"飞牛影视库检索失败：{exc}", ok=False)


def _chunk(text: str, *, ok: bool = True) -> ToolChunk:
    """Build a single-shot ToolChunk carrying *text*."""
    return ToolChunk(
        is_last=True,
        state=ToolResultState.SUCCESS if ok else ToolResultState.ERROR,
        content=[TextBlock(type="text", text=text)],
    )
