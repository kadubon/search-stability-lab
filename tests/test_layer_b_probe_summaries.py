from __future__ import annotations

import pandas as pd

from analysis.layer_b_probes import (
    conservative_interpretation,
    controller_comparison_summary,
    proxy_metric_summary,
    structured_output_fragility_summary,
)


def test_layer_b_probe_summary_generation_preserves_proxy_scope() -> None:
    finals = pd.DataFrame(
        [
            {
                "suite": "compression",
                "backbone_model_id": "gemini-2.5-flash-lite",
                "controller_id": "C0",
                "success_final": True,
                "represented_candidate_family_count_proxy": 2,
                "recoverable_candidate_count_proxy": 3,
                "compression_collision_proxy": 1,
                "avoidable_retirement_proxy": 0,
                "reset_helpfulness_proxy": None,
                "stale_continuation_proxy": 0.2,
                "post_reset_resolution_improvement_proxy": None,
                "structured_output_invalidity": False,
                "structured_output_invalidity_type": None,
                "structured_output_repaired": False,
            },
            {
                "suite": "compression",
                "backbone_model_id": "gemini-2.5-flash-lite",
                "controller_id": "C1",
                "success_final": False,
                "represented_candidate_family_count_proxy": 1,
                "recoverable_candidate_count_proxy": 2,
                "compression_collision_proxy": 2,
                "avoidable_retirement_proxy": 0,
                "reset_helpfulness_proxy": None,
                "stale_continuation_proxy": 0.3,
                "post_reset_resolution_improvement_proxy": None,
                "structured_output_invalidity": True,
                "structured_output_invalidity_type": "invalid_json",
                "structured_output_repaired": True,
            },
        ]
    )

    comparison = controller_comparison_summary(finals)
    proxies = proxy_metric_summary(finals)
    fragility = structured_output_fragility_summary(finals)
    interpretation = conservative_interpretation(finals, "compression")

    assert not comparison.empty
    assert "compression_collision_proxy" in proxies.columns
    assert "repaired_rate" in fragility.columns
    assert "proxy-only" in interpretation
    assert "compression-heavy control" in interpretation
