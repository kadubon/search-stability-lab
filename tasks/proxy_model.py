"""Explicit Layer B proxy-construction helpers."""

from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

from core.config import TaskManifestEntry
from tasks.asset_bundle import TaskAssetBundle
from tasks.proxy import family_proxy_key

if TYPE_CHECKING:
    from tasks.harness import BranchState


def task_authored_proxy_metadata(task: TaskManifestEntry, bundle: TaskAssetBundle | None) -> dict[str, Any]:
    metadata = {
        "family_proxy_rule": family_proxy_key(task),
        "suite": task.suite,
        "probe_purpose": task.probe_purpose,
        "target_hypotheses": task.target_hypotheses,
        "primary_proxy_metrics": task.primary_proxy_metrics,
        "suitable_backbones": task.suitable_backbones,
    }
    if bundle is not None:
        metadata.update(
            {
                "task_asset_bundle_id": bundle.bundle_id,
                "intended_mechanism": bundle.intended_mechanism,
                "proxy_validity_note": bundle.proxy_validity_note.model_dump(mode="json"),
            }
        )
    return metadata


def derived_proxy_features(task: TaskManifestEntry, bundle: TaskAssetBundle | None) -> dict[str, Any]:
    features = {
        "derived_proxy_family_key": family_proxy_key(task),
        "derived_target_file_count": len(task.target_files),
        "derived_resolving_family_count": len(task.resolving_family_keys),
    }
    if bundle is not None:
        features.update(
            {
                "derived_bundle_suite": bundle.suite,
                "derived_branch_profile_count": len(bundle.branch_profiles),
                "derived_compression_pressure": bundle.compression_pressure,
                "derived_initial_contamination": bundle.initial_contamination,
            }
        )
    return features


def runtime_state_proxies(
    *,
    task: TaskManifestEntry,
    bundle: TaskAssetBundle | None,
    branches: list[BranchState],
    compression_collision_proxy: int,
    avoidable_retirement_proxy: int,
    reset_helpfulness_proxy: float | None,
    stale_continuation_proxy: float,
    post_reset_resolution_improvement_proxy: float | None,
) -> dict[str, Any]:
    active = [branch for branch in branches if branch.active]
    recoverable = [branch for branch in branches if branch.recoverable]
    proxies = {
        "represented_candidate_family_count_proxy": len({branch.family_key for branch in active}),
        "recoverable_candidate_count_proxy": len(recoverable),
        "compression_collision_proxy": compression_collision_proxy,
        "avoidable_retirement_proxy": avoidable_retirement_proxy,
        "reset_helpfulness_proxy": reset_helpfulness_proxy,
        "stale_continuation_proxy": round(stale_continuation_proxy, 4),
        "post_reset_resolution_improvement_proxy": post_reset_resolution_improvement_proxy,
        "runtime_active_branch_count_proxy": len(active),
        "runtime_compressed_branch_count_proxy": sum(1 for branch in active if branch.compressed),
        "runtime_proxy_family_matches_resolving": any(
            branch.active and branch.family_key in task.resolving_family_keys for branch in branches
        ),
    }
    if bundle is not None:
        proxies["proxy_validity_note"] = bundle.proxy_validity_note.model_dump(mode="json")
    return proxies
