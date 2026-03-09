"""Summarize a Layer A suite manifest into a compact CSV and Markdown report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_run_summary(run_record: dict[str, object]) -> pd.DataFrame:
    analysis_dir = Path(str(run_record["analysis_output_dir"]))
    path = analysis_dir / "final_outcomes.csv"
    frame = pd.read_csv(path)
    frame["source_config"] = str(run_record["config"])
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir) if args.output_dir else manifest_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = [_load_run_summary(record) for record in manifest["runs"]]
    all_outcomes = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    all_outcomes.to_csv(output_dir / "suite_final_outcomes.csv", index=False)

    summary = (
        all_outcomes.groupby(["source_config", "controller_id"])["success_final"]
        .mean()
        .reset_index()
        .rename(columns={"success_final": "success_rate"})
    )
    summary.to_csv(output_dir / "suite_success_by_controller.csv", index=False)

    lines = ["# Layer A Suite Summary", "", "## Success by controller", ""]
    if summary.empty:
        lines.append("No outcomes available.")
    else:
        for config, frame in summary.groupby("source_config"):
            lines.append(f"### `{config}`")
            lines.append("")
            for _, row in frame.iterrows():
                lines.append(f"- `{row['controller_id']}`: `{row['success_rate']:.4f}`")
            lines.append("")
    (output_dir / "suite_summary.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(output_dir / "suite_summary.md")


if __name__ == "__main__":
    main()
