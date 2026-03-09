"""Layer A simulation engine."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import numpy as np

from controllers.base import ControllerSnapshot, SearchCandidate
from core.config import ModelConfig
from core.event_logger import EventLogger
from core.run_metadata import get_code_revision
from core.structured_models import EventRecord, StepDecision
from simulator.attribution import classify_failure
from simulator.generator import generate_episode
from simulator.types import EpisodeState, RouteState, SimulatorCondition


def _route_to_candidate(route: RouteState) -> SearchCandidate:
    return SearchCandidate(
        candidate_id=route.route_id,
        family_id=route.family_id,
        score=route.local_promise,
        cost=route.retention_cost,
        staleness=route.staleness,
        inertia=route.inertia,
        alias_risk=min(1.0, route.compression_sensitivity + 0.5 * route.overlap_burden),
        evidence_score=route.evidence,
        is_active=route.active,
        is_summary=route.compressed,
        can_substitute=not route.compressed,
        can_branch=True,
        recoverable=route.recoverable,
        metadata={"legacy_load": route.legacy_load},
    )


def _budget_used(state: EpisodeState) -> float:
    return sum(state.routes[route_id].retention_cost for route_id in state.active_route_ids)


def _represented_family_ids(state: EpisodeState) -> list[str]:
    return sorted({state.routes[route_id].family_id for route_id in state.active_route_ids})


def _recoverable_adequate_families(state: EpisodeState) -> list[str]:
    recoverable: set[str] = set()
    for route in state.routes.values():
        if not state.families[route.family_id].adequate:
            continue
        if not route.recoverable or route.alias_flag:
            continue
        threshold = state.families[route.family_id].verification_threshold
        lag_penalty = 0.018 * max(0, state.condition.verification_step - state.step_index)
        alias_penalty = 0.18 if route.alias_flag else 0.0
        stale_penalty = 0.04 * route.staleness + 0.05 * route.legacy_load
        recoverability_score = (
            route.evidence
            + route.latent_verification_gain
            + 0.25 * route.local_promise
            - stale_penalty
            - lag_penalty
            - alias_penalty
        )
        if recoverability_score >= threshold:
            recoverable.add(route.family_id)
    return sorted(recoverable)


def _missed_adequate_family(state: EpisodeState) -> bool:
    for family_id in state.adequate_family_ids_true:
        if state.families[family_id].represented_once:
            return False
    return True


def _build_snapshot(state: EpisodeState) -> ControllerSnapshot:
    active = [_route_to_candidate(state.routes[route_id]) for route_id in state.active_route_ids]
    archived = [_route_to_candidate(state.routes[route_id]) for route_id in state.archived_route_ids]
    return ControllerSnapshot(
        step_index=state.step_index,
        budget_used=_budget_used(state),
        budget_remaining=max(0.0, state.condition.budget_cap - _budget_used(state)),
        represented_family_count=len(_represented_family_ids(state)),
        verification_steps_remaining=max(0, state.condition.verification_step - state.step_index),
        contamination=state.contamination,
        compression_strength=state.condition.compression_level,
        lag_level=state.condition.lag_level,
        active_candidates=active,
        archived_candidates=archived,
    )


def _apply_tool(
    state: EpisodeState,
    decision: StepDecision,
    rng: np.random.Generator,
    model_config: ModelConfig,
) -> dict[str, Any]:
    target_id = decision.target_ids[0]
    route = state.routes[target_id]
    family = state.families[route.family_id]
    gain = model_config.layer_a_profile.evidence_gain_scale * (
        route.latent_verification_gain * (0.85 if family.adequate else 0.55)
    )
    contamination_drag = min(0.55, 0.06 * state.contamination + 0.04 * route.staleness + 0.035 * route.legacy_load)
    noise = rng.normal(0.0, model_config.layer_a_profile.decision_noise)
    effective_gain = gain * (1.0 - contamination_drag)
    route.evidence = float(np.clip(route.evidence + effective_gain + noise, 0.0, 1.2))
    route.local_promise = float(np.clip(route.local_promise + 0.1 * effective_gain + noise, 0.0, 1.0))
    route.tool_requests += 1
    route.last_action = "tool"
    if family.adequate and effective_gain < 0.12 and noise < -0.08:
        state.raw_model_triggered = True
    return {"target_id": target_id, "gain": round(effective_gain + noise, 4)}


def _apply_retire(state: EpisodeState, decision: StepDecision) -> dict[str, Any]:
    retired: list[str] = []
    for route_id in decision.target_ids:
        if route_id not in state.active_route_ids:
            continue
        route = state.routes[route_id]
        route.active = False
        route.last_action = "retire"
        route.recoverable = route.dormant_artifact and route.compressed and not route.alias_flag
        state.active_route_ids.remove(route_id)
        if route_id not in state.archived_route_ids:
            state.archived_route_ids.append(route_id)
        retired.append(route_id)
        if state.families[route.family_id].adequate:
            competing = [
                state.routes[active_id]
                for active_id in state.active_route_ids
                if state.routes[active_id].family_id != route.family_id
            ]
            if competing and max(item.utility_shadow for item in competing) < route.utility_shadow + 0.15:
                state.avoidable_retirement_true = True
    return {"retired_route_ids": retired}


def _apply_substitute(state: EpisodeState, decision: StepDecision) -> dict[str, Any]:
    if len(decision.target_ids) < 2:
        return {"substituted": False}
    old_id, new_id = decision.target_ids[:2]
    if old_id in state.active_route_ids:
        state.active_route_ids.remove(old_id)
        state.archived_route_ids.append(old_id)
        state.routes[old_id].active = False
        state.routes[old_id].recoverable = False
        state.routes[old_id].last_action = "substitute_out"
    if new_id in state.archived_route_ids:
        state.archived_route_ids.remove(new_id)
    state.active_route_ids.append(new_id)
    state.routes[new_id].active = True
    state.routes[new_id].recoverable = True
    state.routes[new_id].ever_active = True
    state.routes[new_id].last_action = "substitute_in"
    state.families[state.routes[new_id].family_id].represented_once = True
    return {"old_route_id": old_id, "new_route_id": new_id}


def _apply_compress(state: EpisodeState, decision: StepDecision) -> dict[str, Any]:
    target_id = decision.target_ids[0]
    route = state.routes[target_id]
    state.compression_count += 1
    route.retention_cost *= state.condition.compression_ratio
    route.compressed = True
    route.dormant_artifact = True
    route.last_action = "compress"
    lag_multiplier = 1.0 + 0.12 * state.condition.verification_step
    alias_score = (
        route.compression_sensitivity * state.condition.compression_alias_scale * lag_multiplier
        + route.overlap_burden
        + 0.08 * route.staleness
    )
    route.alias_flag = alias_score > 0.58
    route.recoverable = not route.alias_flag
    route.evidence = max(0.0, route.evidence - 0.08 * state.condition.compression_alias_scale)
    if route.alias_flag and state.families[route.family_id].adequate:
        state.alias_event_true = True
    return {
        "target_id": target_id,
        "alias_flag": route.alias_flag,
        "new_cost": round(route.retention_cost, 4),
    }


def _apply_branch(state: EpisodeState, decision: StepDecision) -> dict[str, Any]:
    target_id = decision.target_ids[0]
    if target_id in state.archived_route_ids:
        state.archived_route_ids.remove(target_id)
    if target_id not in state.active_route_ids:
        state.active_route_ids.append(target_id)
    route = state.routes[target_id]
    route.active = True
    route.recoverable = True
    route.ever_active = True
    route.last_action = "branch"
    state.branch_count += 1
    state.families[route.family_id].represented_once = True
    return {"target_id": target_id}


def _apply_reset(state: EpisodeState) -> dict[str, Any]:
    state.reset_count += 1
    for route_id in list(state.active_route_ids):
        route = state.routes[route_id]
        route.active = False
        route.last_action = "reset_archive"
        route.recoverable = False
        if route_id not in state.archived_route_ids:
            state.archived_route_ids.append(route_id)
    state.active_route_ids = []
    ranked = sorted(
        state.archived_route_ids,
        key=lambda route_id: state.routes[route_id].local_promise,
        reverse=True,
    )
    used = state.condition.reset_cost
    reactivated: list[str] = []
    for route_id in ranked:
        route = state.routes[route_id]
        if used + route.retention_cost > state.condition.budget_cap:
            continue
        route.active = True
        route.recoverable = True
        route.staleness = 0.0
        route.inertia *= 0.5
        route.legacy_load = 0.0
        route.ever_active = True
        route.last_action = "reset_reactivate"
        state.active_route_ids.append(route_id)
        reactivated.append(route_id)
        used += route.retention_cost
        state.families[route.family_id].represented_once = True
        if len(reactivated) >= 2:
            break
    state.archived_route_ids = [route_id for route_id in state.archived_route_ids if route_id not in reactivated]
    state.contamination = max(0.0, state.contamination * 0.2)
    return {"reactivated_route_ids": reactivated, "reset_cost": state.condition.reset_cost}


def _apply_keep(state: EpisodeState) -> dict[str, Any]:
    for route_id in state.active_route_ids:
        state.routes[route_id].last_action = "keep"
    return {"kept_route_ids": list(state.active_route_ids)}


def _enforce_budget(state: EpisodeState) -> dict[str, Any] | None:
    forced: list[str] = []
    while _budget_used(state) > state.condition.budget_cap and state.active_route_ids:
        worst_id = min(
            state.active_route_ids,
            key=lambda route_id: state.routes[route_id].utility_shadow - state.routes[route_id].retention_cost,
        )
        route = state.routes[worst_id]
        route.active = False
        route.recoverable = False
        route.last_action = "forced_retire"
        state.active_route_ids.remove(worst_id)
        state.archived_route_ids.append(worst_id)
        forced.append(worst_id)
    if _budget_used(state) > state.condition.budget_cap:
        state.budget_collapse = True
    if forced:
        return {"forced_retirements": forced}
    return None


def _update_dynamics(state: EpisodeState, decision_type: str, rng: np.random.Generator) -> None:
    overlap_sum = sum(state.routes[route_id].overlap_burden for route_id in state.active_route_ids)
    active_cost = sum(state.routes[route_id].retention_cost for route_id in state.active_route_ids) or 1.0
    for route in state.routes.values():
        if route.active and decision_type != "reset":
            if decision_type != "tool" or route.route_id not in state.active_route_ids:
                route.staleness += 1.0
            route.inertia = 0.55 * route.inertia + (0.3 if route.last_action == "keep" else 0.15)
            route.legacy_load = 0.75 * route.legacy_load + state.condition.contamination_scale * (
                route.staleness + route.overlap_burden
            )
            if route.compressed and route.alias_flag:
                lag_drag = 0.03 + 0.01 * state.condition.verification_step
                route.evidence = max(0.0, route.evidence - lag_drag)
                route.local_promise = max(0.0, route.local_promise - 0.02)
        elif not route.active:
            route.inertia *= 0.9
            route.legacy_load *= 0.95
            if route.dormant_artifact and route.compressed and not route.alias_flag:
                route.recoverable = True
        route.utility_shadow = (
            route.local_promise
            + 0.4 * route.latent_verification_gain
            + 0.2 * route.evidence
            - 0.25 * route.retention_cost
            - 0.12 * route.staleness
            - 0.08 * route.legacy_load
        )
    stale_ratio = sum(state.routes[route_id].staleness * state.routes[route_id].retention_cost for route_id in state.active_route_ids) / active_cost
    inertia_term = sum(state.routes[route_id].inertia for route_id in state.active_route_ids)
    state.contamination = state.condition.contamination_scale * (
        stale_ratio + overlap_sum + 0.5 * inertia_term
    )
    if state.contamination >= max(0.7, state.condition.reset_cost):
        archived_adequate = [
            route_id
            for route_id in state.archived_route_ids
            if state.families[state.routes[route_id].family_id].adequate and state.routes[route_id].recoverable
        ]
        if archived_adequate:
            state.stale_legacy_triggered = True


def _verification(state: EpisodeState, model_config: ModelConfig) -> dict[str, Any]:
    recoverable = _recoverable_adequate_families(state)
    state.missed_adequate_triggered = _missed_adequate_family(state)
    success = bool(recoverable)
    if not success and not state.alias_event_true and not state.avoidable_retirement_true and not state.stale_legacy_triggered and not state.missed_adequate_triggered:
        state.raw_model_triggered = True
    state.success_final = success
    state.verification_signal = {
        "verification_step": state.step_index,
        "recoverable_adequate_family_ids": recoverable,
        "adequate_family_ids_true": list(state.adequate_family_ids_true),
        "raw_failure_rate": model_config.layer_a_profile.raw_failure_rate,
    }
    if not success:
        failure_channel, triggers = classify_failure(state)
        state.failure_channel_true = failure_channel
        state.mixed_trigger_flags = triggers
    return state.verification_signal


def _event(
    *,
    run_id: str,
    task_id: str,
    seed: int,
    model_config: ModelConfig,
    controller_id: str,
    state: EpisodeState,
    event_type: str,
    prompt_version: str,
    decision: StepDecision | None = None,
    metadata: dict[str, Any] | None = None,
) -> EventRecord:
    return EventRecord(
        run_id=run_id,
        episode_id=state.episode_id,
        task_id=task_id,
        seed=seed,
        layer="layer_a",
        backbone_model_id=model_config.model_id,
        controller_id=controller_id,
        time_step=state.step_index,
        event_type=event_type,
        budget_used=round(_budget_used(state), 4),
        budget_remaining=round(max(0.0, state.condition.budget_cap - _budget_used(state)), 4),
        active_route_ids=list(state.active_route_ids),
        active_family_ids=_represented_family_ids(state),
        represented_family_count=len(_represented_family_ids(state)),
        decision_type=decision.decision_type if decision else None,
        compression_event=metadata.get("compression_event") if metadata else None,
        retirement_event=metadata.get("retirement_event") if metadata else None,
        reset_event=metadata.get("reset_event") if metadata else None,
        tool_calls=metadata.get("tool_calls", []) if metadata else [],
        verification_signal=state.verification_signal,
        success_final=state.success_final,
        prompt_version=prompt_version,
        code_revision=get_code_revision(),
        adequate_family_ids_true=list(state.adequate_family_ids_true),
        recoverable_family_ids_true=_recoverable_adequate_families(state),
        failure_channel_true=state.failure_channel_true,
        alias_event_true=state.alias_event_true,
        avoidable_retirement_true=state.avoidable_retirement_true,
        metadata=metadata or {},
    )


def run_episode(
    *,
    run_id: str,
    seed: int,
    episode_id: str,
    condition: SimulatorCondition,
    controller: Any,
    model_config: ModelConfig,
    logger: EventLogger,
    families_range: tuple[int, int],
    routes_per_family_range: tuple[int, int],
    prompt_version: str,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    state = generate_episode(
        episode_id=episode_id,
        rng=rng,
        condition=condition,
        families_range=families_range,
        routes_per_family_range=routes_per_family_range,
        decision_noise=model_config.layer_a_profile.decision_noise,
    )
    task_id = f"sim-{condition.budget_level}-{condition.lag_level}-{condition.compression_level}"
    logger.log(
        _event(
            run_id=run_id,
            task_id=task_id,
            seed=seed,
            model_config=model_config,
            controller_id=controller.controller_id,
            state=state,
            event_type="episode_start",
            prompt_version=prompt_version,
            metadata={"condition": asdict(condition)},
        )
    )
    for step_index in range(condition.step_limit):
        state.step_index = step_index
        snapshot = _build_snapshot(state)
        decision = controller.decide(snapshot, rng)
        metadata: dict[str, Any] = {"condition": asdict(condition)}
        if decision.decision_type == "tool":
            metadata["tool_calls"] = [_apply_tool(state, decision, rng, model_config)]
        elif decision.decision_type == "retire":
            metadata["retirement_event"] = _apply_retire(state, decision)
        elif decision.decision_type == "substitute-within-family":
            metadata["retirement_event"] = _apply_substitute(state, decision)
        elif decision.decision_type == "compress":
            metadata["compression_event"] = _apply_compress(state, decision)
        elif decision.decision_type == "branch":
            metadata["tool_calls"] = [_apply_branch(state, decision)]
        elif decision.decision_type == "reset":
            metadata["reset_event"] = _apply_reset(state)
        else:
            metadata["tool_calls"] = [_apply_keep(state)]
        budget_event = _enforce_budget(state)
        if budget_event is not None:
            metadata["retirement_event"] = budget_event
        _update_dynamics(state, decision.decision_type, rng)
        logger.log(
            _event(
                run_id=run_id,
                task_id=task_id,
                seed=seed,
                model_config=model_config,
                controller_id=controller.controller_id,
                state=state,
                event_type="step",
                prompt_version=prompt_version,
                decision=decision,
                metadata=metadata,
            )
        )
        if step_index >= condition.verification_step or state.budget_collapse or not state.active_route_ids:
            _verification(state, model_config)
            break
    if state.success_final is None:
        _verification(state, model_config)
    logger.log(
        _event(
            run_id=run_id,
            task_id=task_id,
            seed=seed,
            model_config=model_config,
            controller_id=controller.controller_id,
            state=state,
            event_type="episode_end",
            prompt_version=prompt_version,
            metadata={
                "condition": asdict(condition),
                "branch_count": state.branch_count,
                "compression_count": state.compression_count,
                "reset_count": state.reset_count,
                "failure_triggers": state.mixed_trigger_flags,
            },
        )
    )
    represented = {state.routes[route_id].family_id for route_id in state.active_route_ids}
    recoverable = _recoverable_adequate_families(state)
    return {
        "run_id": run_id,
        "episode_id": state.episode_id,
        "task_id": task_id,
        "success_final": bool(state.success_final),
        "adequate_family_survival_rate": len(set(recoverable)) / max(len(state.adequate_family_ids_true), 1),
        "recoverable_family_count_at_verification": len(recoverable),
        "family_extinction_rate": 1.0 - (len(represented & set(state.adequate_family_ids_true)) / max(len(state.adequate_family_ids_true), 1)),
        "represented_family_count": len(represented),
        "alias_event_true": state.alias_event_true,
        "avoidable_retirement_true": state.avoidable_retirement_true,
        "failure_channel_true": state.failure_channel_true or "",
        "condition": asdict(condition),
        "controller_id": controller.controller_id,
        "backbone_model_id": model_config.model_id,
        "final_success_rate": float(bool(state.success_final)),
    }
