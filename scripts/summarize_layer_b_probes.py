"""Generate Layer B probe-suite summaries from analyzed final outcomes."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.layer_b_probes import (
    compression_collision_summary,
    conservative_interpretation,
    controller_comparison_summary,
    load_layer_b_finals,
    proxy_metric_summary,
    structured_output_fragility_summary,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-outcomes", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    finals = load_layer_b_finals(args.final_outcomes)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    controller_comparison_summary(finals).to_csv(output_dir / "controller_comparison_summary.csv", index=False)
    proxy_metric_summary(finals).to_csv(output_dir / "proxy_metric_summary.csv", index=False)
    compression_collision_summary(finals).to_csv(output_dir / "compression_collision_summary.csv", index=False)
    structured_output_fragility_summary(finals).to_csv(
        output_dir / "structured_output_fragility_summary.csv",
        index=False,
    )
    for suite in ["substitution", "compression", "reset"]:
        (output_dir / f"{suite}_interpretation.md").write_text(
            conservative_interpretation(finals, suite),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
