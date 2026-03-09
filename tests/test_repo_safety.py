from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analysis.conservative_summary import (
    build_controller_comparison_summary,
    build_layer_a_hypothesis_table,
    build_structured_output_fragility_summary,
    render_current_status,
)
from scripts.check_public_safety import scan_repo


def test_no_real_env_in_working_tree() -> None:
    assert not Path(".env").exists()


def test_public_safety_scan_is_clean() -> None:
    findings = scan_repo(Path("."))
    assert findings == []


def test_env_example_uses_placeholders() -> None:
    text = Path(".env.example").read_text(encoding="utf-8")
    assert "YOUR_GEMINI_API_KEY" in text


def test_metric_registry_marks_exact_proxy_and_confound_explicitly() -> None:
    registry = pd.read_csv("docs/metric_registry.csv")
    metric_classes = set(registry["metric_class"])
    assert "exact_theory_quantity" in metric_classes
    assert "proxy" in metric_classes
    assert "confound_indicator" in metric_classes


def test_current_status_summary_generation_inputs_are_available(tmp_path) -> None:
    tmp_root = tmp_path / "status_inputs"
    layer_a_dir = tmp_root / "layer_a_run" / "analysis"
    layer_a_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "controller_id": "C0",
                "success_final": False,
                "failure_channel_true": "avoidable_retirement",
            },
            {
                "controller_id": "C3",
                "success_final": True,
                "failure_channel_true": None,
            },
        ]
    ).to_csv(layer_a_dir / "final_outcomes.csv", index=False)
    manifest_path = tmp_root / "layer_a_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "runs": [
                    {
                        "config": "configs/experiments/layer_a_h2_substitution_gemini.yaml",
                        "analysis_output_dir": str(layer_a_dir),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    layer_b_summary_gemini = tmp_root / "gemini_summary.csv"
    layer_b_summary_local = tmp_root / "local_summary.csv"
    pd.DataFrame(
        [
            {
                "backbone_model_id": "gemini-2.5-flash-lite",
                "controller_id": "C3",
                "success_rate": 0.5,
                "measurement_scope": "proxy (task harness)",
            }
        ]
    ).to_csv(layer_b_summary_gemini, index=False)
    pd.DataFrame(
        [
            {
                "backbone_model_id": "gemma3:1b",
                "controller_id": "C5",
                "success_rate": 0.25,
                "measurement_scope": "proxy (task harness)",
            }
        ]
    ).to_csv(layer_b_summary_local, index=False)

    layer_b_finals_gemini = tmp_root / "gemini_finals.csv"
    layer_b_finals_local = tmp_root / "local_finals.csv"
    pd.DataFrame(
        [
            {
                "backbone_model_id": "gemini-2.5-flash-lite",
                "controller_id": "C0",
                "structured_output_invalidity": True,
                "structured_output_invalidity_type": "backend_error",
            }
        ]
    ).to_csv(layer_b_finals_gemini, index=False)
    pd.DataFrame(
        [
            {
                "backbone_model_id": "gemma3:1b",
                "controller_id": "C5",
                "structured_output_invalidity": True,
                "structured_output_invalidity_type": "invalid_json",
            }
        ]
    ).to_csv(layer_b_finals_local, index=False)

    hypothesis = build_layer_a_hypothesis_table(manifest_path)
    controller_summary = build_controller_comparison_summary([layer_b_summary_gemini, layer_b_summary_local])
    fragility = build_structured_output_fragility_summary([layer_b_finals_gemini, layer_b_finals_local])
    markdown = render_current_status(
        hypothesis_table=hypothesis,
        controller_summary=controller_summary,
        fragility_summary=fragility,
    )
    assert "`H2`" in markdown
    assert "`C3` success rate" in markdown
    assert "Structured-output fragility" in markdown
