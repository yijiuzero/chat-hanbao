# -*- coding: utf-8 -*-
# pylint: disable=protected-access
"""Tests for mode-owned handler selection and reset lifecycle."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from hanbao.loop.gates.base import (
    StopAction,
    StopHandlerRegistration,
)
from hanbao.loop.gates.handler import StopHandler
from hanbao.loop.gates.rubric import QualitativeRubricGate
from hanbao.loop.gates.runner import _filter_by_scope
from hanbao.runtime.runtime import Runtime


def _registration(
    scope: str,
    *,
    is_active=None,
) -> StopHandlerRegistration:
    return StopHandlerRegistration(
        plugin_id=f"test-{scope}",
        handler=StopHandler(),
        name=f"{scope}-handler",
        scope=scope,
        is_active=is_active,
    )


def test_explicit_mode_scope_replaces_default_scope():
    """An active mode handler suppresses the default handler."""
    default = _registration("default")
    goal = _registration("goal", is_active=lambda: True)

    selected = _filter_by_scope([default, goal])

    assert selected == [goal]


def test_inactive_mode_scope_keeps_default_scope():
    """An inactive mode handler leaves the default handler selected."""
    default = _registration("default")
    goal = _registration("goal", is_active=lambda: False)

    selected = _filter_by_scope([default, goal])

    assert selected == [default]


def test_unscoped_plugin_handler_is_always_selected():
    """Unscoped plugin handlers remain available with explicit modes."""
    plugin = _registration("")
    default = _registration("default")
    goal = _registration("goal", is_active=lambda: True)

    selected = _filter_by_scope([plugin, default, goal])

    assert selected == [plugin, goal]




@pytest.mark.asyncio
async def test_runtime_awaits_mode_turn_start_callbacks():
    """Runtime awaits each registered mode turn-start callback."""
    calls = []

    class _Mode:
        name = "test"

        async def on_turn_start(self, ctx):
            calls.append(ctx)

    workspace = SimpleNamespace(
        plugins=SimpleNamespace(modes=[_Mode()]),
    )
    runtime = Runtime(workspace=workspace, app_services=None)
    ctx = SimpleNamespace()

    await runtime._start_modes(ctx)

    assert calls == [ctx]


@pytest.mark.asyncio
async def test_qualitative_rubric_state_is_session_isolated():
    """Resetting one rubric session leaves another session untouched."""
    gate = QualitativeRubricGate(
        rubric="continue",
        max_evaluations=1,
    )

    with patch(
        "hanbao.loop.gates.loop_gate._session_id",
        return_value="session-a",
    ):
        first_a = await gate.check({})

    with patch(
        "hanbao.loop.gates.loop_gate._session_id",
        return_value="session-b",
    ):
        first_b = await gate.check({})

    with patch(
        "hanbao.loop.gates.loop_gate._session_id",
        return_value="session-a",
    ):
        gate.reset_session()
        next_a = await gate.check({})

    with patch(
        "hanbao.loop.gates.loop_gate._session_id",
        return_value="session-b",
    ):
        next_b = await gate.check({})

    assert first_a.action == StopAction.INTERRUPT_AND_CONTINUE
    assert first_b.action == StopAction.INTERRUPT_AND_CONTINUE
    assert next_a.action == StopAction.INTERRUPT_AND_CONTINUE
    assert next_b.action == StopAction.BYPASS
