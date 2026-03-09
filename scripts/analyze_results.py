"""Aggregate JSONL logs and produce tables and figures."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analysis.aggregate import build_summary_tables, final_outcomes, load_events
from analysis.figures import (
    figure_failure_composition,
    figure_reset_benefit,
    figure_success_vs_budget,
    figure_success_vs_compression,
)
from analysis.stats import fit_regression, pairwise_contrasts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_paths = list(input_dir.rglob("events.jsonl"))
    events = load_events(jsonl_paths)
    events.to_csv(output_dir / "events_flat.csv", index=False)
    finals = final_outcomes(events)
    finals.to_csv(output_dir / "final_outcomes.csv", index=False)
    summary = build_summary_tables(finals)
    summary.to_csv(output_dir / "summary_tables.csv", index=False)
    contrasts = pairwise_contrasts(finals[finals["layer"] == "layer_a"])
    contrasts.to_csv(output_dir / "pairwise_contrasts.csv", index=False)
    fit_regression(finals, output_dir)
    figure_success_vs_budget(finals, output_dir)
    figure_success_vs_compression(finals, output_dir)
    figure_reset_benefit(finals, output_dir)
    figure_failure_composition(finals, output_dir)
    print(output_dir)


if __name__ == "__main__":
    main()
