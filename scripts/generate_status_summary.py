"""Generate conservative repo-level status summaries and CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.conservative_summary import (
    build_controller_comparison_summary,
    build_failure_channel_summary,
    build_layer_a_hypothesis_table,
    build_structured_output_fragility_summary,
    render_current_status,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/current_status")
    parser.add_argument("--markdown-path", default="docs/CURRENT_STATUS.md")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    layer_a_manifest = "artifacts/layer_a_suite_2026-03-09/manifest.json"
    gemini_layer_b_dir = "artifacts/real_tasks_gemini_nonmock_expanded/real-gemini-nonmock-expanded-20260309T011314Z-b3d4732e/analysis"
    local_layer_b_dir = "artifacts/real_tasks_local_cpu_nonmock_expanded_suite_2026-03-09/analysis"

    hypothesis_table = build_layer_a_hypothesis_table(layer_a_manifest)
    controller_summary = build_controller_comparison_summary(
        [
            Path(gemini_layer_b_dir) / "summary_tables.csv",
            Path(local_layer_b_dir) / "summary_tables.csv",
        ]
    )
    failure_summary = build_failure_channel_summary(layer_a_manifest)
    fragility_summary = build_structured_output_fragility_summary(
        [
            Path(gemini_layer_b_dir) / "final_outcomes.csv",
            Path(local_layer_b_dir) / "final_outcomes.csv",
        ]
    )

    hypothesis_table.to_csv(output_dir / "hypothesis_support.csv", index=False)
    controller_summary.to_csv(output_dir / "controller_comparison_summary.csv", index=False)
    failure_summary.to_csv(output_dir / "failure_channel_composition_summary.csv", index=False)
    fragility_summary.to_csv(output_dir / "structured_output_fragility_summary.csv", index=False)

    markdown = render_current_status(
        hypothesis_table=hypothesis_table,
        controller_summary=controller_summary,
        fragility_summary=fragility_summary,
    )
    markdown_path = Path(args.markdown_path)
    markdown_path.write_text(markdown, encoding="utf-8")
    print(markdown_path)


if __name__ == "__main__":
    main()
