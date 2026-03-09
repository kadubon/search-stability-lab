"""Shared controller interface and snapshot types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from core.config import ControllerConfig
from core.structured_models import PredictedRisk, StepDecision


@dataclass(slots=True)
class SearchCandidate:
    candidate_id: str
    family_id: str
    score: float
    cost: float
    staleness: float
    inertia: float
    alias_risk: float
    evidence_score: float
    is_active: bool = True
    is_summary: bool = False
    can_substitute: bool = False
    can_branch: bool = False
    recoverable: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ControllerSnapshot:
    step_index: int
    budget_used: float
    budget_remaining: float
    represented_family_count: int
    verification_steps_remaining: int
    contamination: float
    compression_strength: str
    lag_level: str
    active_candidates: list[SearchCandidate]
    archived_candidates: list[SearchCandidate]


def default_risk(snapshot: ControllerSnapshot) -> PredictedRisk:
    active = snapshot.active_candidates or snapshot.archived_candidates
    alias = max((item.alias_risk for item in active), default=0.0)
    stale = max((item.staleness for item in active), default=0.0)
    adequacy = 1.0 / max(snapshot.represented_family_count, 1)
    return PredictedRisk(
        adequacy_loss=min(1.0, adequacy),
        alias_risk=min(1.0, alias),
        staleness_risk=min(1.0, stale / 5.0),
    )


def candidate_utility(candidate: SearchCandidate) -> float:
    return (
        candidate.score
        + 0.35 * candidate.evidence_score
        - 0.25 * candidate.cost
        - 0.15 * candidate.staleness
        - 0.1 * candidate.inertia
        - 0.2 * candidate.alias_risk
    )


class BaseController(ABC):
    """Controller law interface shared across layers."""

    def __init__(self, config: ControllerConfig) -> None:
        self.config = config

    @property
    def controller_id(self) -> str:
        return self.config.controller_id

    @abstractmethod
    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        """Choose a single structured controller action."""
