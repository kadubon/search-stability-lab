"""Safe Layer B real-task harness with mock mode."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from controllers.base import ControllerSnapshot, SearchCandidate
from core.config import ModelConfig, RealTaskExperimentConfig, TaskManifestEntry
from core.event_logger import EventLogger
from core.exceptions import MissingAssetError, RetryExhaustedError, StructuredOutputError, TaskAssetError
from core.run_metadata import get_code_revision
from core.structured_models import EventRecord
from models.base import ModelAdapter
from tasks.asset_bundle import TaskAssetBundle, load_task_asset_bundle
from tasks.proxy import derived_family_candidates, family_proxy_key
from tasks.proxy_model import derived_proxy_features, runtime_state_proxies, task_authored_proxy_metadata


@dataclass(slots=True)
class BranchState:
    branch_id: str
    family_key: str
    score: float
    cost: float
    active: bool = True
    compressed: bool = False
    recoverable: bool = True
    staleness: float = 0.0
    inertia: float = 0.0
    evidence: float = 0.2
    alias_proxy: float = 0.0


def _build_initial_branches(
    task: TaskManifestEntry,
    bundle: TaskAssetBundle | None = None,
) -> list[BranchState]:
    if bundle is not None:
        return [
            BranchState(
                branch_id=f"{task.task_id}-branch-{index}",
                family_key=profile.family_key,
                score=profile.base_score,
                cost=profile.cost,
                active=profile.active,
                compressed=profile.compressed,
                recoverable=profile.recoverable,
                evidence=profile.evidence,
                alias_proxy=profile.alias_proxy,
                staleness=profile.staleness,
                inertia=profile.inertia,
            )
            for index, profile in enumerate(bundle.branch_profiles)
        ]
    families = derived_family_candidates(task)
    branches: list[BranchState] = []
    for index, family in enumerate(families):
        branches.append(
            BranchState(
                branch_id=f"{task.task_id}-branch-{index}",
                family_key=family,
                score=0.62 - 0.05 * index,
                cost=1.0 + 0.2 * index,
                alias_proxy=0.18 * index,
                evidence=0.25 + 0.05 * (index == 0),
            )
        )
    return branches


def _snapshot(
    turn: int,
    branches: list[BranchState],
    token_budget: int,
    contamination: float,
    max_turns: int,
    compression_strength: str = "mild",
) -> ControllerSnapshot:
    budget_cap = token_budget / 256.0
    active = [
        SearchCandidate(
            candidate_id=branch.branch_id,
            family_id=branch.family_key,
            score=branch.score,
            cost=branch.cost,
            staleness=branch.staleness,
            inertia=branch.inertia,
            alias_risk=branch.alias_proxy,
            evidence_score=branch.evidence,
            is_active=branch.active,
            is_summary=branch.compressed,
            can_substitute=not branch.compressed,
            can_branch=False,
            recoverable=branch.recoverable,
        )
        for branch in branches
        if branch.active
    ]
    archived = [
        SearchCandidate(
            candidate_id=branch.branch_id,
            family_id=branch.family_key,
            score=branch.score,
            cost=branch.cost,
            staleness=branch.staleness,
            inertia=branch.inertia,
            alias_risk=branch.alias_proxy,
            evidence_score=branch.evidence,
            is_active=False,
            is_summary=branch.compressed,
            can_substitute=True,
            can_branch=True,
            recoverable=branch.recoverable,
        )
        for branch in branches
        if not branch.active
    ]
    used = sum(branch.cost for branch in branches if branch.active)
    return ControllerSnapshot(
        step_index=turn,
        budget_used=used,
        budget_remaining=max(0.0, budget_cap - used),
        represented_family_count=len({branch.family_key for branch in branches if branch.active}),
        verification_steps_remaining=max(0, max_turns - turn - 1),
        contamination=contamination,
        compression_strength=compression_strength,
        lag_level="task",
        active_candidates=active,
        archived_candidates=archived,
    )


def _find_branch(branches: list[BranchState], branch_id: str) -> BranchState | None:
    return next((branch for branch in branches if branch.branch_id == branch_id), None)


def run_task_slice(
    *,
    run_id: str,
    seed: int,
    experiment: RealTaskExperimentConfig,
    manifest_entries: list[TaskManifestEntry],
    controller: Any,
    model_adapter: ModelAdapter,
    logger: EventLogger,
) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    results: list[dict[str, Any]] = []
    for task_index, task in enumerate(manifest_entries):
        task_seed = seed + task_index
        bundle: TaskAssetBundle | None = None
        asset_error: str | None = None
        if not experiment.mock_mode:
            if not task.task_assets_path or not Path(task.task_assets_path).exists():
                asset_error = f"Task assets missing for {task.task_id} and strict_assets={experiment.strict_assets}."
            else:
                try:
                    bundle = load_task_asset_bundle(task)
                except TaskAssetError as exc:
                    asset_error = str(exc)
        if asset_error and experiment.strict_assets:
            if "missing" in asset_error.lower():
                raise MissingAssetError(asset_error)
            raise TaskAssetError(asset_error)
        if asset_error:
            logger.log(
                EventRecord(
                    run_id=run_id,
                    episode_id=f"{task.task_id}-episode",
                    task_id=task.task_id,
                    seed=task_seed,
                    layer="layer_b",
                    backbone_model_id=model_adapter.model_id,
                    controller_id=controller.controller_id,
                    time_step=0,
                    event_type="task_skipped",
                    budget_used=0.0,
                    budget_remaining=float(experiment.token_budget),
                    active_route_ids=[],
                    active_family_ids=[],
                    represented_family_count=0,
                    decision_type=None,
                    compression_event=None,
                    retirement_event=None,
                    reset_event=None,
                    tool_calls=[],
                    verification_signal={"skipped": True, "reason": "invalid_or_missing_task_assets"},
                    success_final=None,
                    prompt_version=model_adapter.config.prompt_version,
                    code_revision=get_code_revision(),
                    failure_channel_proxy=None,
                    human_audit_label=None,
                    proxy_confidence=None,
                    metadata={
                        "repository": task.repository,
                        "mock_mode": experiment.mock_mode,
                        "task_status": "skipped_missing_assets",
                        "skip_reason": asset_error,
                        "family_proxy_rule": family_proxy_key(task),
                    },
                )
            )
            results.append(
                {
                    "run_id": run_id,
                    "task_id": task.task_id,
                    "resolved": None,
                    "task_status": "skipped_missing_assets",
                    "candidate_branch_count": None,
                    "reset_count": None,
                    "compression_count": None,
                    "retired_branch_count": None,
                    "patch_revision_count": None,
                    "time_to_first_plausible_patch": None,
                    "time_to_first_test_passing_patch": None,
                    "failure_channel_proxy": None,
                    "proxy_confidence": None,
                    "controller_id": controller.controller_id,
                    "backbone_model_id": model_adapter.model_id,
                    "represented_candidate_family_count_proxy": None,
                    "recoverable_candidate_count_proxy": None,
                    "compression_collision_proxy": None,
                    "avoidable_retirement_proxy": None,
                    "reset_helpfulness_proxy": None,
                    "family_proxy_rule": family_proxy_key(task),
                }
            )
            continue
        branches = _build_initial_branches(task, bundle)
        contamination = bundle.initial_contamination if bundle is not None else 0.0
        evidence_threshold = bundle.evidence_threshold if bundle is not None else 0.65
        compression_collision_proxy = 0
        avoidable_retirement_proxy = 0
        reset_helpfulness_proxy: float | None = None
        stale_continuation_proxy = contamination
        post_reset_resolution_improvement_proxy: float | None = None
        resolved = False
        patch_revision_count = 0
        reset_count = 0
        compression_count = 0
        retired_branch_count = 0
        candidate_branch_count = len(branches)
        last_error: str | None = None
        valid_structured_output_count = 0
        repaired_structured_output_count = 0
        unrecoverable_structured_output_count = 0
        structured_output_failure_kind: str | None = None
        repair_actions_seen: list[str] = []
        for turn in range(experiment.max_turns):
            snapshot = _snapshot(turn, branches, experiment.token_budget, contamination, experiment.max_turns)
            context = {
                "step_id": f"{task.task_id}-turn-{turn}",
                "task_id": task.task_id,
                "issue_summary": task.issue_summary,
                "active_candidates": [
                    {"candidate_id": candidate.candidate_id, "family_id": candidate.family_id}
                    for candidate in snapshot.active_candidates
                ],
                "archived_candidates": [
                    {"candidate_id": candidate.candidate_id, "family_id": candidate.family_id}
                    for candidate in snapshot.archived_candidates
                ],
                "represented_family_count": snapshot.represented_family_count,
                "budget_remaining": snapshot.budget_remaining,
                "alias_risk": max((candidate.alias_risk for candidate in snapshot.active_candidates), default=0.0),
                "staleness_risk": max((candidate.staleness for candidate in snapshot.active_candidates), default=0.0),
            }
            if bundle is not None:
                context["task_asset_bundle_id"] = bundle.bundle_id
                context["allowed_paths"] = bundle.allowed_paths
                context["test_command"] = bundle.test_command
            model_event: dict[str, Any] = {}
            try:
                model_suggestion = model_adapter.plan_step(context)
                model_event["model_suggestion"] = model_suggestion.model_dump(mode="json")
            except (RetryExhaustedError, StructuredOutputError) as exc:
                last_error = str(exc)
                model_event["model_output_error"] = last_error
            call_metadata = model_adapter.consume_last_call_metadata()
            if call_metadata:
                model_event["structured_output"] = call_metadata
                status = call_metadata.get("status")
                if status == "valid":
                    valid_structured_output_count += 1
                elif status == "repaired":
                    repaired_structured_output_count += 1
                    repair_actions_seen.extend(call_metadata.get("repair_actions", []))
                elif status == "unrecoverable":
                    unrecoverable_structured_output_count += 1
                    structured_output_failure_kind = call_metadata.get("failure_kind", structured_output_failure_kind)
            decision = controller.decide(snapshot, rng)
            if decision.decision_type == "tool" and decision.target_ids:
                branch = _find_branch(branches, decision.target_ids[0])
                if branch is not None:
                    patch_revision_count += 1
                    model_bonus = 0.1 if model_event.get("model_suggestion", {}).get("family_ids") == [branch.family_key] else 0.0
                    branch.evidence = min(1.0, branch.evidence + 0.22 + model_bonus)
                    branch.score = min(1.0, branch.score + 0.12 + model_bonus)
                    branch.staleness = max(0.0, branch.staleness - 0.5)
            elif decision.decision_type == "compress" and decision.target_ids:
                branch = _find_branch(branches, decision.target_ids[0])
                if branch is not None:
                    compression_count += 1
                    branch.compressed = True
                    branch.cost *= 0.55
                    branch.alias_proxy = min(1.0, branch.alias_proxy + 0.25 + (bundle.compression_pressure if bundle is not None else 0.0))
                    if bundle is not None and bundle.compression_evidence_penalty:
                        branch.evidence = max(0.0, branch.evidence - bundle.compression_evidence_penalty)
                        branch.score = max(0.0, branch.score - 0.5 * bundle.compression_evidence_penalty)
                    if (
                        bundle is not None
                        and branch.alias_proxy >= bundle.compression_recoverability_alias_threshold
                    ):
                        branch.recoverable = False
                    if branch.alias_proxy > 0.55:
                        compression_collision_proxy += 1
                    try:
                        compression = model_adapter.compress_state(
                            {
                                "source_route_ids": [branch.branch_id],
                                "source_family_ids": [branch.family_key],
                                "task_id": task.task_id,
                            }
                        )
                        model_event["compression"] = compression.model_dump(mode="json")
                    except (RetryExhaustedError, StructuredOutputError) as exc:
                        model_event["compression_error"] = str(exc)
                    call_metadata = model_adapter.consume_last_call_metadata()
                    if call_metadata:
                        model_event.setdefault("structured_output_events", []).append(call_metadata)
                        status = call_metadata.get("status")
                        if status == "valid":
                            valid_structured_output_count += 1
                        elif status == "repaired":
                            repaired_structured_output_count += 1
                            repair_actions_seen.extend(call_metadata.get("repair_actions", []))
                        elif status == "unrecoverable":
                            unrecoverable_structured_output_count += 1
                            structured_output_failure_kind = call_metadata.get("failure_kind", structured_output_failure_kind)
            elif decision.decision_type == "retire" and decision.target_ids:
                for branch_id in decision.target_ids:
                    branch = _find_branch(branches, branch_id)
                    if branch is None or not branch.active:
                        continue
                    branch.active = False
                    retired_branch_count += 1
                    if branch.family_key in task.resolving_family_keys:
                        surviving = [item for item in branches if item.active and item.family_key in task.resolving_family_keys]
                        if not surviving:
                            avoidable_retirement_proxy += 1
            elif decision.decision_type == "substitute-within-family" and len(decision.target_ids) >= 2:
                old_branch = _find_branch(branches, decision.target_ids[0])
                new_branch = _find_branch(branches, decision.target_ids[1])
                if old_branch is not None:
                    old_branch.active = False
                if new_branch is not None:
                    new_branch.active = True
                    new_branch.recoverable = True
            elif decision.decision_type == "branch":
                inactive = next((branch for branch in branches if not branch.active), None)
                if inactive is not None:
                    inactive.active = True
                    inactive.recoverable = True
                    candidate_branch_count = max(candidate_branch_count, sum(1 for branch in branches if branch.active))
            elif decision.decision_type == "reset":
                reset_count += 1
                pre_reset_best = max(
                    (branch.evidence for branch in branches if branch.family_key in task.resolving_family_keys),
                    default=0.0,
                )
                for branch in branches:
                    branch.active = False
                    branch.staleness = 0.0
                    branch.inertia *= 0.4
                primary = next((branch for branch in branches if branch.family_key == family_proxy_key(task)), branches[0])
                primary.active = True
                primary.recoverable = True
                if bundle is not None:
                    primary.evidence = min(1.0, primary.evidence + bundle.reset_recovery_bonus)
                    primary.score = min(1.0, primary.score + 0.5 * bundle.reset_recovery_bonus)
                contamination *= 0.25
                try:
                    reset_decision = model_adapter.choose_continue_branch_reset(
                        {
                            "task_id": task.task_id,
                            "continue_value": 0.4,
                            "branch_value": 0.45,
                            "reset_value": 0.6,
                            "reset_cost": 0.25,
                        }
                    )
                    model_event["reset_decision"] = reset_decision.model_dump(mode="json")
                except (RetryExhaustedError, StructuredOutputError) as exc:
                    model_event["reset_error"] = str(exc)
                call_metadata = model_adapter.consume_last_call_metadata()
                if call_metadata:
                    model_event.setdefault("structured_output_events", []).append(call_metadata)
                    status = call_metadata.get("status")
                    if status == "valid":
                        valid_structured_output_count += 1
                    elif status == "repaired":
                        repaired_structured_output_count += 1
                        repair_actions_seen.extend(call_metadata.get("repair_actions", []))
                    elif status == "unrecoverable":
                        unrecoverable_structured_output_count += 1
                        structured_output_failure_kind = call_metadata.get("failure_kind", structured_output_failure_kind)
                post_reset_best = max(
                    (branch.evidence for branch in branches if branch.family_key in task.resolving_family_keys and branch.active),
                    default=0.0,
                )
                post_reset_resolution_improvement_proxy = round(max(0.0, post_reset_best - pre_reset_best), 4)
            for branch in branches:
                if branch.active:
                    branch.staleness += 0.5
                    branch.inertia = 0.5 * branch.inertia + 0.2
                    if bundle is not None and bundle.stale_continuation_penalty:
                        branch.score = max(0.0, branch.score - branch.staleness * 0.02 * bundle.stale_continuation_penalty)
            contamination = 0.25 * sum(branch.alias_proxy + branch.staleness for branch in branches if branch.active)
            stale_continuation_proxy = round(
                contamination
                + sum(branch.staleness for branch in branches if branch.active and branch.family_key not in task.resolving_family_keys),
                4,
            )
            active_resolving = [
                branch
                for branch in branches
                if branch.active and branch.family_key in task.resolving_family_keys
            ]
            if (
                turn >= (bundle.resolution_turn_gate if bundle is not None else 0)
                and len(active_resolving)
                >= (bundle.required_active_resolving_routes_for_success if bundle is not None else 1)
                and any(branch.evidence >= evidence_threshold for branch in active_resolving)
            ):
                resolved = True
                if reset_count:
                    reset_helpfulness_proxy = 1.0
                break
            logger.log(
                EventRecord(
                    run_id=run_id,
                    episode_id=f"{task.task_id}-episode",
                    task_id=task.task_id,
                    seed=task_seed,
                    layer="layer_b",
                    backbone_model_id=model_adapter.model_id,
                    controller_id=controller.controller_id,
                    time_step=turn,
                    event_type="task_step",
                    budget_used=round(snapshot.budget_used, 4),
                    budget_remaining=round(snapshot.budget_remaining, 4),
                    active_route_ids=[branch.branch_id for branch in branches if branch.active],
                    active_family_ids=sorted({branch.family_key for branch in branches if branch.active}),
                    represented_family_count=len({branch.family_key for branch in branches if branch.active}),
                    decision_type=decision.decision_type,
                    compression_event=model_event.get("compression"),
                    retirement_event={"retired_branch_count": retired_branch_count} if retired_branch_count else None,
                    reset_event=model_event.get("reset_decision"),
                    tool_calls=[model_event] if model_event else [],
                    verification_signal=None,
                    success_final=None,
                    prompt_version=model_adapter.config.prompt_version,
                    code_revision=get_code_revision(),
                    failure_channel_proxy=None,
                    human_audit_label=None,
                    proxy_confidence=0.55 if model_event else None,
                    metadata={
                        "repository": task.repository,
                        "mock_mode": experiment.mock_mode,
                        "task_asset_bundle_id": bundle.bundle_id if bundle is not None else None,
                        **task_authored_proxy_metadata(task, bundle),
                        **derived_proxy_features(task, bundle),
                        **runtime_state_proxies(
                            task=task,
                            bundle=bundle,
                            branches=branches,
                            compression_collision_proxy=compression_collision_proxy,
                            avoidable_retirement_proxy=avoidable_retirement_proxy,
                            reset_helpfulness_proxy=reset_helpfulness_proxy,
                            stale_continuation_proxy=stale_continuation_proxy,
                            post_reset_resolution_improvement_proxy=post_reset_resolution_improvement_proxy,
                        ),
                    },
                )
            )
        if not resolved:
            try:
                diagnosis = model_adapter.diagnose_failure(
                    {
                        "run_id": run_id,
                        "success": False,
                        "candidate_channel": "avoidable_retirement" if avoidable_retirement_proxy else "mixed_failure",
                    }
                )
                failure_channel_proxy = diagnosis.failure_channel
                proxy_confidence = diagnosis.confidence
            except (RetryExhaustedError, StructuredOutputError):
                failure_channel_proxy = "mixed_failure"
                proxy_confidence = 0.0
            call_metadata = model_adapter.consume_last_call_metadata()
            if call_metadata:
                status = call_metadata.get("status")
                if status == "valid":
                    valid_structured_output_count += 1
                elif status == "repaired":
                    repaired_structured_output_count += 1
                    repair_actions_seen.extend(call_metadata.get("repair_actions", []))
                elif status == "unrecoverable":
                    unrecoverable_structured_output_count += 1
                    structured_output_failure_kind = call_metadata.get("failure_kind", structured_output_failure_kind)
        else:
            failure_channel_proxy = None
            proxy_confidence = None
            if reset_count and reset_helpfulness_proxy is None:
                reset_helpfulness_proxy = 0.0
        task_failure_category = (
            "structured_output_invalidity"
            if unrecoverable_structured_output_count > 0
            else "controller_or_proxy_failure"
            if not resolved and failure_channel_proxy not in (None, "mixed_failure")
            else "task_failure"
            if not resolved
            else "resolved"
        )
        logger.log(
            EventRecord(
                run_id=run_id,
                episode_id=f"{task.task_id}-episode",
                task_id=task.task_id,
                seed=task_seed,
                layer="layer_b",
                backbone_model_id=model_adapter.model_id,
                controller_id=controller.controller_id,
                time_step=experiment.max_turns,
                event_type="task_end",
                budget_used=round(sum(branch.cost for branch in branches if branch.active), 4),
                budget_remaining=round(
                    max(0.0, experiment.token_budget / 256.0 - sum(branch.cost for branch in branches if branch.active)),
                    4,
                ),
                active_route_ids=[branch.branch_id for branch in branches if branch.active],
                active_family_ids=sorted({branch.family_key for branch in branches if branch.active}),
                represented_family_count=len({branch.family_key for branch in branches if branch.active}),
                decision_type=None,
                compression_event=None,
                retirement_event=None,
                reset_event=None,
                tool_calls=[],
                verification_signal={"resolved": resolved},
                success_final=resolved,
                prompt_version=model_adapter.config.prompt_version,
                code_revision=get_code_revision(),
                failure_channel_proxy=failure_channel_proxy,
                human_audit_label=None,
                proxy_confidence=proxy_confidence,
                metadata={
                    "repository": task.repository,
                    "task_status": "completed",
                    "task_asset_bundle_id": bundle.bundle_id if bundle is not None else None,
                    "candidate_branch_count": candidate_branch_count,
                    "reset_count": reset_count,
                    "compression_count": compression_count,
                    "retired_branch_count": retired_branch_count,
                    "patch_revision_count": patch_revision_count,
                    "last_model_error": last_error,
                    "structured_output_valid_call_count": valid_structured_output_count,
                    "structured_output_repaired_call_count": repaired_structured_output_count,
                    "structured_output_unrecoverable_call_count": unrecoverable_structured_output_count,
                    "structured_output_failure_kind": structured_output_failure_kind,
                    "structured_output_repair_actions": sorted(set(repair_actions_seen)),
                    "task_failure_category": task_failure_category,
                    **task_authored_proxy_metadata(task, bundle),
                    **derived_proxy_features(task, bundle),
                    **runtime_state_proxies(
                        task=task,
                        bundle=bundle,
                        branches=branches,
                        compression_collision_proxy=compression_collision_proxy,
                        avoidable_retirement_proxy=avoidable_retirement_proxy,
                        reset_helpfulness_proxy=reset_helpfulness_proxy,
                        stale_continuation_proxy=stale_continuation_proxy,
                        post_reset_resolution_improvement_proxy=post_reset_resolution_improvement_proxy,
                    ),
                },
            )
        )
        results.append(
            {
                "run_id": run_id,
                "task_id": task.task_id,
                "resolved": resolved,
                "candidate_branch_count": candidate_branch_count,
                "reset_count": reset_count,
                "compression_count": compression_count,
                "retired_branch_count": retired_branch_count,
                "patch_revision_count": patch_revision_count,
                "time_to_first_plausible_patch": 1 if patch_revision_count else None,
                "time_to_first_test_passing_patch": 1 if resolved else None,
                "failure_channel_proxy": failure_channel_proxy,
                "proxy_confidence": proxy_confidence,
                "controller_id": controller.controller_id,
                "backbone_model_id": model_adapter.model_id,
                "structured_output_valid_call_count": valid_structured_output_count,
                "structured_output_repaired_call_count": repaired_structured_output_count,
                "structured_output_unrecoverable_call_count": unrecoverable_structured_output_count,
                "structured_output_failure_kind": structured_output_failure_kind,
                "task_failure_category": task_failure_category,
                **task_authored_proxy_metadata(task, bundle),
                **derived_proxy_features(task, bundle),
                **runtime_state_proxies(
                    task=task,
                    bundle=bundle,
                    branches=branches,
                    compression_collision_proxy=compression_collision_proxy,
                    avoidable_retirement_proxy=avoidable_retirement_proxy,
                    reset_helpfulness_proxy=reset_helpfulness_proxy,
                    stale_continuation_proxy=stale_continuation_proxy,
                    post_reset_resolution_improvement_proxy=post_reset_resolution_improvement_proxy,
                ),
            }
        )
    return results
