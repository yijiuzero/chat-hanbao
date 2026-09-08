# -*- coding: utf-8 -*-
"""Rubric evaluation strategies for loop completion.

Architecture:
    RubricStrategy (ABC)
    ├── DefaultRubric     — always SATISFIED (no rubric)
    └── SubAgentRubric    — placeholder for subagent eval
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# [hanbao modification] I-046 — ``GoalStatusRubric`` was goal-mode-only and is
# removed together with the goal loop mode; ``Callable``/``Optional`` went with it.
from typing import Any

from .base import (
    StopAction,
    StopHandlerResult,
)
from .loop_gate import LoopGate

logger = logging.getLogger(__name__)


class RubricVerdict(str, Enum):
    """Grader verdicts."""

    SATISFIED = "satisfied"
    NEEDS_REVISION = "needs_revision"
    FAILED = "failed"
    GRADER_ERROR = "grader_error"
    MAX_ITERATIONS = "max_iterations_reached"


@dataclass
class RubricEvaluation:
    """Result of one rubric evaluation pass."""

    iteration: int
    verdict: RubricVerdict
    explanation: str = ""
    feedback: str = ""


# ---- Abstract Strategy ----


class RubricStrategy(ABC):
    """Base class for rubric evaluation strategies."""

    @abstractmethod
    async def evaluate(
        self,
        goal: str,
        agent_output: str,
        iteration: int,
    ) -> RubricEvaluation:
        """Evaluate whether the goal is met."""


# ---- Concrete Strategies ----


class DefaultRubric(RubricStrategy):
    """No rubric — always SATISFIED.

    Used for loops that have no rubric requirement.
    The loop terminates normally after each turn.
    """

    async def evaluate(
        self,
        goal: str,
        agent_output: str,
        iteration: int,
    ) -> RubricEvaluation:
        return RubricEvaluation(
            iteration=iteration,
            verdict=RubricVerdict.SATISFIED,
            explanation="No rubric registered",
        )


class SubAgentRubric(RubricStrategy):
    """Placeholder for subagent-based verification.

    Concrete implementation should follow the
    oh-my-claudecode/ralph pattern: spawn a subagent
    to verify, then check state file key-values for
    the verdict (not LLM output parsing).

    TODO: implement file-based state verification.
    """

    def __init__(
        self,
        spawn_fn: Any = None,
        fork: bool = False,
    ) -> None:
        self._spawn_fn = spawn_fn
        self._fork = fork

    async def evaluate(
        self,
        goal: str,
        agent_output: str,
        iteration: int,
    ) -> RubricEvaluation:
        """Placeholder — returns GRADER_ERROR."""
        return RubricEvaluation(
            iteration=iteration,
            verdict=RubricVerdict.GRADER_ERROR,
            explanation=("SubAgentRubric not yet implemented"),
        )


@dataclass
class _QualitativeRubricState:
    """Per-session qualitative evaluation count."""

    evaluations: int = 0


class QualitativeRubricGate(LoopGate):
    """Apply a qualitative rubric to text-only responses.

    Prevents premature stop when the LLM outputs text
    without any tool calls.  Counts interventions per
    request cycle; stops re-prompting after
    ``max_evaluations``.
    """

    def __init__(
        self,
        rubric: str = "",
        max_evaluations: int = 1,
    ) -> None:
        super().__init__()
        self._rubric = rubric
        self._max_evaluations = max_evaluations

    def _ensure_state(self) -> _QualitativeRubricState:
        """Return current session state, creating it when needed."""
        state = self._state()
        if state is None:
            state = _QualitativeRubricState()
            self.activate(state)
        return state

    @property
    def name(self) -> str:
        return "qualitative-rubric"

    @property
    def priority(self) -> int:
        return 90

    async def check(
        self,
        ctx: Any,
    ) -> StopHandlerResult:
        """Intervene up to the configured evaluation limit.

        Only triggers on text-only responses
        (no tool calls).
        """
        _bypass = StopHandlerResult(
            action=StopAction.BYPASS,
        )
        if isinstance(ctx, dict) and ctx.get(
            "has_tool_calls",
        ):
            return _bypass

        state = self._ensure_state()
        if state.evaluations >= self._max_evaluations:
            return _bypass

        state.evaluations += 1
        logger.debug(
            "QualitativeRubricGate: evaluate %d/%d",
            state.evaluations,
            self._max_evaluations,
        )
        return StopHandlerResult(
            action=StopAction.INTERRUPT_AND_CONTINUE,
            reason="qualitative rubric requested revision",
            reset_peers=True,
        )

    def build_continuation(self) -> str:
        """Return the re-prompt text."""
        return self._rubric

    def reset_turn(self) -> None:
        """Reset evaluation counter for a new turn."""
        state = self._state()
        if state is not None:
            state.evaluations = 0


__all__ = [
    "QualitativeRubricGate",
    "DefaultRubric",
    "RubricEvaluation",
    "RubricStrategy",
    "RubricVerdict",
    "SubAgentRubric",
]
