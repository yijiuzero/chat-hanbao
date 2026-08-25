# -*- coding: utf-8 -*-
"""Shared agent template definitions and builders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..config.config import (
    AgentProfileConfig,
    ChannelConfig,
    HeartbeatConfig,
    MCPConfig,
    ToolsConfig,
)

DEFAULT_AGENT_TEMPLATE = "default"
SUPPORTED_AGENT_TEMPLATES = (DEFAULT_AGENT_TEMPLATE,)


@dataclass(frozen=True)
class AgentTemplateBuildResult:
    """Materialized result for creating an agent from a builtin template."""

    agent_config: AgentProfileConfig
    initial_skill_names: tuple[str, ...]
    md_template_id: str | None


def list_supported_agent_templates() -> tuple[str, ...]:
    """Return builtin agent template IDs supported by the application."""
    return SUPPORTED_AGENT_TEMPLATES


def get_workspace_md_template_id(template_id: str | None) -> str | None:
    """Map an agent template id to the workspace markdown template id.

    hanbao only ships the ``default`` agent template, so no markdown
    template override is mapped for any template id.
    """
    return None


def build_agent_template(
    template_id: str,
    *,
    agent_id: str,
    workspace_dir: Path,
    fallback_language: str,
    name: str | None = None,
    description: str | None = None,
    language: str | None = None,
) -> AgentTemplateBuildResult:
    """Build a builtin template into a concrete agent configuration."""
    resolved_language = language or fallback_language or "zh"

    if template_id == DEFAULT_AGENT_TEMPLATE:
        if name is None:
            raise ValueError("Default template requires a name")
        agent_config = AgentProfileConfig(
            id=agent_id,
            name=name,
            description=description or "",
            workspace_dir=str(workspace_dir),
            template_id=template_id,
            language=resolved_language,
            channels=ChannelConfig(),
            mcp=MCPConfig(),
            heartbeat=HeartbeatConfig(),
            tools=ToolsConfig(),
        )
        return AgentTemplateBuildResult(
            agent_config=agent_config,
            initial_skill_names=(),
            md_template_id=get_workspace_md_template_id(template_id),
        )

    raise ValueError(
        f"Unsupported template: {template_id!r}. "
        f"Expected one of {SUPPORTED_AGENT_TEMPLATES}.",
    )
