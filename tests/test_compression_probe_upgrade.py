from __future__ import annotations

import pandas as pd

from analysis.layer_b_probes import compression_collision_summary, conservative_interpretation
from core.config import load_task_manifest
from tasks.asset_bundle import load_task_asset_bundle


def test_compression_probe_manifest_has_outcome_sensitivity_fields() -> None:
    manifest = load_task_manifest("tasks/manifests/compression_probe_suite_v1.yaml")
    assert len(manifest.tasks) >= 2
    for task in manifest.tasks:
        bundle = load_task_asset_bundle(task)
        assert bundle.suite == "compression"
        assert bundle.required_active_resolving_routes_for_success >= 2
        assert bundle.resolution_turn_gate >= 1
        assert bundle.compression_evidence_penalty > 0


def test_compression_probe_interpretation_distinguishes_proxy_and_outcome() -> None:
    finals = pd.DataFrame(
        [
            {
                "suite": "compression",
                "backbone_model_id": "gemini",
                "controller_id": "C0",
                "success_final": True,
                "compression_collision_proxy": 0,
                "structured_output_invalidity": False,
            },
            {
                "suite": "compression",
                "backbone_model_id": "gemini",
                "controller_id": "C1",
                "success_final": False,
                "compression_collision_proxy": 5,
                "structured_output_invalidity": False,
            },
            {
                "suite": "compression",
                "backbone_model_id": "gemini",
                "controller_id": "C5",
                "success_final": True,
                "compression_collision_proxy": 0,
                "structured_output_invalidity": False,
            },
        ]
    )
    summary = compression_collision_summary(finals)
    interpretation = conservative_interpretation(finals, "compression")
    assert not summary.empty
    assert "outcome-level sensitivity" in interpretation
