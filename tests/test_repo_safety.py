from __future__ import annotations

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


def test_current_status_summary_generation_inputs_are_available() -> None:
    hypothesis = build_layer_a_hypothesis_table("artifacts/layer_a_suite_2026-03-09/manifest.json")
    controller_summary = build_controller_comparison_summary(
        [
            "artifacts/real_tasks_gemini_nonmock_expanded/real-gemini-nonmock-expanded-20260309T011314Z-b3d4732e/analysis/summary_tables.csv",
            "artifacts/real_tasks_local_cpu_nonmock_expanded_suite_2026-03-09/analysis/summary_tables.csv",
        ]
    )
    fragility = build_structured_output_fragility_summary(
        [
            "artifacts/real_tasks_gemini_nonmock_expanded/real-gemini-nonmock-expanded-20260309T011314Z-b3d4732e/analysis/final_outcomes.csv",
            "artifacts/real_tasks_local_cpu_nonmock_expanded_suite_2026-03-09/analysis/final_outcomes.csv",
        ]
    )
    markdown = render_current_status(
        hypothesis_table=hypothesis,
        controller_summary=controller_summary,
        fragility_summary=fragility,
    )
    assert "`H2`" in markdown
    assert "`C3` success rate" in markdown
    assert "Structured-output fragility" in markdown
