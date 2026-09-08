# -*- coding: utf-8 -*-
"""Tests for stop-handler result application."""
from types import SimpleNamespace

from hanbao.loop.gates.base import StopAction, StopHandlerResult
from hanbao.loop.gates.runner import apply_stop_result, check_pending_gates


# [hanbao modification] I-046 — the two goal-continuation cases were removed
# together with the goal loop mode (they depended on ``GoalTurnGate``).  Only
# the mode-agnostic deferral behaviour is still covered here.
def test_tool_call_defers_termination() -> None:
    """A terminating decision waits until tool results are processed."""
    agent = SimpleNamespace(_gate_pending_stop=None)
    result = StopHandlerResult(
        action=StopAction.TERMINATE,
        reason="Iteration limit reached",
    )

    apply_stop_result(agent, result, is_tool_call=True)

    assert check_pending_gates(agent) is result
    assert vars(agent)["_gate_pending_stop"] is None
