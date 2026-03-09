"""Pydantic models for structured model outputs and log payloads."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


DecisionType = Literal[
    "keep",
    "retire",
    "substitute-within-family",
    "compress",
    "branch",
    "reset",
    "tool",
]

FailureChannel = Literal[
    "missed_adequate_family",
    "compression_alias",
    "avoidable_retirement",
    "stale_legacy_continuation",
    "raw_model_failure",
    "mixed_failure",
]


class PredictedRisk(BaseModel):
    adequacy_loss: float = Field(ge=0.0, le=1.0)
    alias_risk: float = Field(ge=0.0, le=1.0)
    staleness_risk: float = Field(ge=0.0, le=1.0)


class StepDecision(BaseModel):
    step_id: str
    decision_type: DecisionType
    target_ids: list[str] = Field(default_factory=list)
    family_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale_short: str
    predicted_risk: PredictedRisk
    estimated_budget_after: float = Field(ge=0.0)


class SummaryState(BaseModel):
    open_questions: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    critical_discriminators: list[str] = Field(default_factory=list)


class CompressionResult(BaseModel):
    compression_id: str
    source_route_ids: list[str]
    source_family_ids: list[str]
    summary_text: str
    summary_state: SummaryState
    estimated_information_loss: float = Field(ge=0.0, le=1.0)


class ContinueBranchResetDecision(BaseModel):
    decision: Literal["continue", "branch", "reset"]
    estimated_continue_value: float
    estimated_branch_value: float
    estimated_reset_value: float
    estimated_reset_cost: float = Field(ge=0.0)
    justification_short: str


class FailureAttribution(BaseModel):
    run_id: str
    success: bool
    failure_channel: FailureChannel
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str


class EventRecord(BaseModel):
    run_id: str
    episode_id: str
    task_id: str
    seed: int
    layer: Literal["layer_a", "layer_b"]
    backbone_model_id: str
    controller_id: str
    time_step: int
    event_type: str
    budget_used: float
    budget_remaining: float
    active_route_ids: list[str] = Field(default_factory=list)
    active_family_ids: list[str] = Field(default_factory=list)
    represented_family_count: int = Field(ge=0)
    decision_type: str | None = None
    compression_event: dict[str, Any] | None = None
    retirement_event: dict[str, Any] | None = None
    reset_event: dict[str, Any] | None = None
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    verification_signal: dict[str, Any] | None = None
    success_final: bool | None = None
    prompt_version: str
    code_revision: str
    adequate_family_ids_true: list[str] | None = None
    recoverable_family_ids_true: list[str] | None = None
    failure_channel_true: str | None = None
    alias_event_true: bool | None = None
    avoidable_retirement_true: bool | None = None
    failure_channel_proxy: str | None = None
    human_audit_label: str | None = None
    proxy_confidence: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

