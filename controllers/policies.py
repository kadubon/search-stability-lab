"""Concrete controller families C0 through C6."""

from __future__ import annotations

from collections import Counter

import numpy as np

from controllers.base import (
    BaseController,
    ControllerSnapshot,
    SearchCandidate,
    candidate_utility,
    default_risk,
)
from core.structured_models import StepDecision


def _sorted_active(snapshot: ControllerSnapshot) -> list[SearchCandidate]:
    return sorted(snapshot.active_candidates, key=candidate_utility, reverse=True)


def _family_counts(snapshot: ControllerSnapshot) -> Counter[str]:
    return Counter(item.family_id for item in snapshot.active_candidates)


def _best_archived_for_family(
    snapshot: ControllerSnapshot, family_id: str
) -> SearchCandidate | None:
    candidates = [item for item in snapshot.archived_candidates if item.family_id == family_id]
    if not candidates:
        return None
    return max(candidates, key=candidate_utility)


class GreedySingleRouteController(BaseController):
    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        ranked = _sorted_active(snapshot)
        top = ranked[0]
        if len(ranked) > 1 and snapshot.budget_remaining < 0.5:
            retire_ids = [item.candidate_id for item in ranked[1:]]
            retire_families = sorted({item.family_id for item in ranked[1:]})
            return StepDecision(
                step_id=f"step-{snapshot.step_index}",
                decision_type="retire",
                target_ids=retire_ids,
                family_ids=retire_families,
                confidence=0.8,
                rationale_short="Keep the top local route and retire the rest under budget pressure.",
                predicted_risk=default_risk(snapshot),
                estimated_budget_after=max(0.0, snapshot.budget_remaining + sum(item.cost for item in ranked[1:])),
            )
        return StepDecision(
            step_id=f"step-{snapshot.step_index}",
            decision_type="tool",
            target_ids=[top.candidate_id],
            family_ids=[top.family_id],
            confidence=0.72,
            rationale_short="Deepen the highest-scoring active route.",
            predicted_risk=default_risk(snapshot),
            estimated_budget_after=max(0.0, snapshot.budget_remaining - min(0.5, snapshot.budget_remaining)),
        )


class GreedySummarizeController(BaseController):
    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        ranked = sorted(snapshot.active_candidates, key=lambda item: (item.cost, item.staleness), reverse=True)
        compressible = next((item for item in ranked if not item.is_summary), ranked[0])
        return StepDecision(
            step_id=f"step-{snapshot.step_index}",
            decision_type="compress",
            target_ids=[compressible.candidate_id],
            family_ids=[compressible.family_id],
            confidence=0.76,
            rationale_short="Aggressively summarize expensive active state to preserve budget.",
            predicted_risk=default_risk(snapshot),
            estimated_budget_after=snapshot.budget_remaining + 0.5 * compressible.cost,
        )


class ReserveAwareController(BaseController):
    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        represented = {item.family_id for item in snapshot.active_candidates}
        if len(represented) < self.config.family_reserve_min:
            branchable = next((item for item in snapshot.archived_candidates if item.can_branch), None)
            if branchable is not None:
                return StepDecision(
                    step_id=f"step-{snapshot.step_index}",
                    decision_type="branch",
                    target_ids=[branchable.candidate_id],
                    family_ids=[branchable.family_id],
                    confidence=0.81,
                    rationale_short="Restore family reserve before verification.",
                    predicted_risk=default_risk(snapshot),
                    estimated_budget_after=max(0.0, snapshot.budget_remaining - branchable.cost),
                )
        least_helpful = min(snapshot.active_candidates, key=candidate_utility)
        if snapshot.budget_remaining < 0.4 and _family_counts(snapshot)[least_helpful.family_id] > 1:
            return StepDecision(
                step_id=f"step-{snapshot.step_index}",
                decision_type="retire",
                target_ids=[least_helpful.candidate_id],
                family_ids=[least_helpful.family_id],
                confidence=0.74,
                rationale_short="Retire a redundant route while preserving family reserve.",
                predicted_risk=default_risk(snapshot),
                estimated_budget_after=snapshot.budget_remaining + least_helpful.cost,
            )
        best = _sorted_active(snapshot)[0]
        return StepDecision(
            step_id=f"step-{snapshot.step_index}",
            decision_type="tool",
            target_ids=[best.candidate_id],
            family_ids=[best.family_id],
            confidence=0.68,
            rationale_short="Request evidence while holding a reserve of represented families.",
            predicted_risk=default_risk(snapshot),
            estimated_budget_after=max(0.0, snapshot.budget_remaining - 0.25),
        )


class SubstitutionFirstController(BaseController):
    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        for candidate in sorted(snapshot.active_candidates, key=lambda item: item.cost, reverse=True):
            substitute = _best_archived_for_family(snapshot, candidate.family_id)
            if candidate.can_substitute and substitute is not None and substitute.cost <= candidate.cost:
                return StepDecision(
                    step_id=f"step-{snapshot.step_index}",
                    decision_type="substitute-within-family",
                    target_ids=[candidate.candidate_id, substitute.candidate_id],
                    family_ids=[candidate.family_id],
                    confidence=0.83,
                    rationale_short="Swap to a cheaper same-family route before deleting cross-family options.",
                    predicted_risk=default_risk(snapshot),
                    estimated_budget_after=snapshot.budget_remaining + max(0.0, candidate.cost - substitute.cost),
                )
        return ReserveAwareController(self.config).decide(snapshot, rng)


class ResetAwareController(BaseController):
    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        reset_value = snapshot.contamination + 0.2 * sum(item.staleness for item in snapshot.active_candidates)
        if reset_value >= self.config.reset_threshold and snapshot.verification_steps_remaining > 1:
            return StepDecision(
                step_id=f"step-{snapshot.step_index}",
                decision_type="reset",
                target_ids=[item.candidate_id for item in snapshot.active_candidates],
                family_ids=sorted({item.family_id for item in snapshot.active_candidates}),
                confidence=0.79,
                rationale_short="Reset because stale legacy contamination dominates continuation value.",
                predicted_risk=default_risk(snapshot),
                estimated_budget_after=max(0.0, snapshot.budget_remaining - 0.5),
            )
        return ReserveAwareController(self.config).decide(snapshot, rng)


class FullTheoryController(BaseController):
    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        reset_value = snapshot.contamination + 0.25 * sum(item.staleness for item in snapshot.active_candidates)
        if reset_value >= self.config.reset_threshold and snapshot.verification_steps_remaining > 1:
            return ResetAwareController(self.config).decide(snapshot, rng)
        for candidate in sorted(snapshot.active_candidates, key=lambda item: item.cost, reverse=True):
            substitute = _best_archived_for_family(snapshot, candidate.family_id)
            if candidate.can_substitute and substitute is not None and substitute.cost < candidate.cost:
                return SubstitutionFirstController(self.config).decide(snapshot, rng)
        low_alias = [
            item for item in snapshot.active_candidates if item.alias_risk <= self.config.compression_caution_threshold
        ]
        if snapshot.budget_remaining < 0.5 and low_alias:
            target = max(low_alias, key=lambda item: item.cost + item.staleness)
            return StepDecision(
                step_id=f"step-{snapshot.step_index}",
                decision_type="compress",
                target_ids=[target.candidate_id],
                family_ids=[target.family_id],
                confidence=0.78,
                rationale_short="Compress only low-alias-risk state under budget pressure.",
                predicted_risk=default_risk(snapshot),
                estimated_budget_after=snapshot.budget_remaining + 0.5 * target.cost,
            )
        reserve_action = ReserveAwareController(self.config).decide(snapshot, rng)
        if reserve_action.decision_type != "tool":
            return reserve_action
        best = _sorted_active(snapshot)[0]
        return StepDecision(
            step_id=f"step-{snapshot.step_index}",
            decision_type="tool",
            target_ids=[best.candidate_id],
            family_ids=[best.family_id],
            confidence=0.8,
            rationale_short="Preserve reserve, prefer substitution, and deepen the best recoverable branch.",
            predicted_risk=default_risk(snapshot),
            estimated_budget_after=max(0.0, snapshot.budget_remaining - 0.25),
        )


class RandomBudgetMatchedController(BaseController):
    ACTIONS = [
        "keep",
        "retire",
        "substitute-within-family",
        "compress",
        "branch",
        "reset",
        "tool",
    ]

    def decide(self, snapshot: ControllerSnapshot, rng: np.random.Generator) -> StepDecision:
        ranked = _sorted_active(snapshot)
        target = ranked[0]
        decision_type = rng.choice(self.ACTIONS).item()
        target_ids = [target.candidate_id]
        family_ids = [target.family_id]
        if decision_type == "retire" and len(ranked) > 1:
            target = ranked[-1]
            target_ids = [target.candidate_id]
            family_ids = [target.family_id]
        elif decision_type == "substitute-within-family":
            substitute = _best_archived_for_family(snapshot, target.family_id)
            if substitute is not None:
                target_ids = [target.candidate_id, substitute.candidate_id]
            else:
                decision_type = "tool"
        elif decision_type == "branch":
            branchable = next((item for item in snapshot.archived_candidates if item.can_branch), None)
            if branchable is not None:
                target_ids = [branchable.candidate_id]
                family_ids = [branchable.family_id]
                target = branchable
            else:
                decision_type = "keep"
        return StepDecision(
            step_id=f"step-{snapshot.step_index}",
            decision_type=decision_type,
            target_ids=target_ids,
            family_ids=family_ids,
            confidence=0.45,
            rationale_short="Randomized budget-matched baseline action.",
            predicted_risk=default_risk(snapshot),
            estimated_budget_after=max(0.0, snapshot.budget_remaining - 0.1 * target.cost),
        )


CONTROLLER_REGISTRY = {
    "C0": GreedySingleRouteController,
    "C1": GreedySummarizeController,
    "C2": ReserveAwareController,
    "C3": SubstitutionFirstController,
    "C4": ResetAwareController,
    "C5": FullTheoryController,
    "C6": RandomBudgetMatchedController,
}

