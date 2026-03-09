"""Dataclasses for Layer A simulator state."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RouteState:
    route_id: str
    family_id: str
    local_promise: float
    latent_verification_gain: float
    retention_cost: float
    overlap_burden: float
    staleness: float
    inertia: float
    compression_sensitivity: float
    evidence: float
    dormant_artifact: bool = False
    active: bool = False
    recoverable: bool = False
    compressed: bool = False
    alias_flag: bool = False
    legacy_load: float = 0.0
    ever_active: bool = False
    last_action: str = "init"
    utility_shadow: float = 0.0
    tool_requests: int = 0


@dataclass(slots=True)
class FamilyState:
    family_id: str
    adequate: bool
    route_ids: list[str]
    verification_threshold: float
    represented_once: bool = False


@dataclass(slots=True)
class SimulatorCondition:
    budget_level: str
    lag_level: str
    overlap_level: str
    compression_level: str
    contamination_level: str
    reset_cost_level: str
    budget_cap: float
    verification_step: int
    overlap_scale: float
    compression_ratio: float
    compression_alias_scale: float
    contamination_scale: float
    reset_cost: float
    step_limit: int
    hard_cap_budget: bool = True


@dataclass(slots=True)
class EpisodeState:
    episode_id: str
    step_index: int
    condition: SimulatorCondition
    families: dict[str, FamilyState]
    routes: dict[str, RouteState]
    adequate_family_ids_true: list[str]
    active_route_ids: list[str]
    archived_route_ids: list[str]
    contamination: float = 0.0
    reset_count: int = 0
    compression_count: int = 0
    branch_count: int = 0
    alias_event_true: bool = False
    avoidable_retirement_true: bool = False
    budget_collapse: bool = False
    mixed_trigger_flags: list[str] = field(default_factory=list)
    stale_legacy_triggered: bool = False
    missed_adequate_triggered: bool = False
    raw_model_triggered: bool = False
    success_final: bool | None = None
    verification_signal: dict[str, object] | None = None
    failure_channel_true: str | None = None
