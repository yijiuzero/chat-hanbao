# -*- coding: utf-8 -*-
"""Tool: search the family local knowledge base (RAG).

[hanbao modification] New hanbao tool (no upstream counterpart).

Retrieval is fully local (BM25 over the on-disk index) — the query never
leaves the device.  When the knowledge base is disabled or empty the tool
returns an explanatory message instead of an error, so the agent can
carry on with the conversation.
"""

from agentscope.message import TextBlock
from agentscope.message import ToolResultState
from agentscope.tool import ToolChunk

from ...config.context import get_current_workspace_dir
from ...constant import WORKING_DIR
from ...rag.service import get_knowledge_service
from ...runtime.tool_registry import tool_descriptor


@tool_descriptor(
    async_execution=True,
    tool_type="internal",
    policy_name="KnowledgeSearch",
    ui_description="Search local knowledge base",
    ui_icon="📚",
)
async def search_knowledge(
    query: str,
    top_k: int = 5,
) -> ToolChunk:
    """Search the local family knowledge base (documents, bills, notes).

    Use this when the user asks about the content of their own local
    files — family documents, invoices, contracts, study notes, album
    folder names — or references something that was indexed into the
    knowledge base. The search runs entirely on this device.

    Args:
        query: What to look for, in the user's own words.
        top_k: How many passages to return (default 5, max 10).

    Returns:
        ToolChunk with the matching passages and their source paths.
    """
    workspace_dir = get_current_workspace_dir() or WORKING_DIR
    limit = max(1, min(int(top_k or 5), 10))

    try:
        service = get_knowledge_service(workspace_dir)
        result = await service.search(query, top_k=limit)
    except Exception as exc:  # noqa: BLE001 - degrade, never crash the agent
        return _chunk(f"知识库检索失败：{exc}", ok=False)

    if not result.get("enabled"):
        return _chunk(
            "本地知识库尚未启用。请在控制台「知识库」页面添加要索引的本地"
            "目录并构建索引后，我才能检索你的家庭文档。",
            ok=False,
        )

    results = result.get("results") or []
    if not results:
        return _chunk(
            f"知识库中没有找到与「{query}」相关的内容。"
            "可以换几个关键词，或先在控制台「知识库」页面构建/更新索引。",
        )

    lines = [f"本地知识库命中 {len(results)} 段（数据不出本机）：", ""]
    for i, hit in enumerate(results, 1):
        location = hit.get("path") or hit.get("source") or ""
        lines.append(f"[{i}] {location}  (相关度 {hit['score']})")
        lines.append(hit.get("text", "").strip())
        lines.append("")

    lines.append(
        "引用时请标注来源文件名；若内容看起来过期，提醒用户核对原件。",
    )
    return _chunk("\n".join(lines))


def _chunk(text: str, *, ok: bool = True) -> ToolChunk:
    """Build a single-shot ToolChunk carrying *text*."""
    return ToolChunk(
        is_last=True,
        state=ToolResultState.SUCCESS if ok else ToolResultState.ERROR,
        content=[TextBlock(type="text", text=text)],
    )
