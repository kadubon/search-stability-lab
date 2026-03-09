"""Deterministic mock adapter for offline tests and smoke runs."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from core.config import ModelConfig
from core.structured_models import (
    CompressionResult,
    ContinueBranchResetDecision,
    FailureAttribution,
    PredictedRisk,
    StepDecision,
    SummaryState,
)
from models.base import ModelAdapter


def _seed_from_payload(payload: dict[str, Any]) -> int:
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return int(hashlib.sha256(encoded).hexdigest()[:8], 16)


class MockAdapter(ModelAdapter):
    """Purely local deterministic adapter."""

    def __init__(self, config: ModelConfig) -> None:
        super().__init__(config)

    def _invoke(self, prompt: str, schema_name: str) -> str:
        raise NotImplementedError("MockAdapter does not use text prompts directly.")

    def plan_step(self, context: dict[str, Any]) -> StepDecision:
        active = context.get("active_candidates", [])
        archived = context.get("archived_candidates", [])
        target = (active or archived or [{"candidate_id": "none", "family_id": "none"}])[0]
        represented = context.get("represented_family_count", 1)
        decision = "tool"
        if represented < 2 and archived:
            decision = "branch"
        elif context.get("budget_remaining", 0.0) < 0.3 and active:
            decision = "compress"
        return StepDecision(
            step_id=context.get("step_id", "mock-step"),
            decision_type=decision,
            target_ids=[target["candidate_id"]],
            family_ids=[target["family_id"]],
            confidence=0.66,
            rationale_short="Deterministic mock decision based on budget and family coverage.",
            predicted_risk=PredictedRisk(
                adequacy_loss=min(1.0, 1.0 / max(represented, 1)),
                alias_risk=min(1.0, context.get("alias_risk", 0.1)),
                staleness_risk=min(1.0, context.get("staleness_risk", 0.1)),
            ),
            estimated_budget_after=max(0.0, context.get("budget_remaining", 0.0) - 0.2),
        )

    def compress_state(self, context: dict[str, Any]) -> CompressionResult:
        seed = _seed_from_payload(context)
        source_ids = context.get("source_route_ids", ["route-0"])
        family_ids = context.get("source_family_ids", ["family-0"])
        return CompressionResult(
            compression_id=f"cmp-{seed}",
            source_route_ids=source_ids,
            source_family_ids=family_ids,
            summary_text="Compressed summary preserving open discriminators.",
            summary_state=SummaryState(
                open_questions=["Which branch survives verification?"],
                assumptions=["Summary used only as a recoverable placeholder."],
                critical_discriminators=["Adequate-family evidence still unresolved."],
            ),
            estimated_information_loss=min(0.9, 0.2 + 0.1 * len(source_ids)),
        )

    def diagnose_failure(self, trace: dict[str, Any]) -> FailureAttribution:
        channel = trace.get("candidate_channel", "mixed_failure")
        return FailureAttribution(
            run_id=trace.get("run_id", "mock-run"),
            success=bool(trace.get("success", False)),
            failure_channel=channel,
            confidence=0.61,
            notes="Deterministic mock attribution from provided trace summary.",
        )

    def choose_continue_branch_reset(
        self, context: dict[str, Any]
    ) -> ContinueBranchResetDecision:
        continue_value = float(context.get("continue_value", 0.5))
        branch_value = float(context.get("branch_value", 0.55))
        reset_value = float(context.get("reset_value", 0.4))
        decision = "branch"
        if reset_value > max(continue_value, branch_value):
            decision = "reset"
        elif continue_value > branch_value:
            decision = "continue"
        return ContinueBranchResetDecision(
            decision=decision,
            estimated_continue_value=continue_value,
            estimated_branch_value=branch_value,
            estimated_reset_value=reset_value,
            estimated_reset_cost=float(context.get("reset_cost", 0.25)),
            justification_short="Deterministic mock comparison of continuation, branching, and reset values.",
        )

