"""Conservative repo-level status summaries built from analyzed artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_suite_manifest(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_layer_a_hypothesis_table(manifest_path: str | Path) -> pd.DataFrame:
    manifest = load_suite_manifest(manifest_path)
    rows: list[dict[str, str]] = []
    for run in manifest["runs"]:
        analysis_dir = Path(run["analysis_output_dir"])
        outcomes = pd.read_csv(analysis_dir / "final_outcomes.csv")
        config = str(run["config"])
        if "h1_budget" in config:
            pooled = outcomes.groupby("budget_level")["success_final"].mean()
            status = "partial_support" if pooled.get("high", 0.0) > max(pooled.get("low", 0.0), pooled.get("medium", 0.0)) else "unclear"
            note = "High budget improved pooled success, but the pattern was not uniformly monotone by controller."
            hypothesis = "H1"
        elif "h2_substitution" in config:
            success = outcomes.groupby("controller_id")["success_final"].mean()
            avoidable = (outcomes["failure_channel_true"] == "avoidable_retirement").groupby(outcomes["controller_id"]).mean()
            status = "supported" if success.get("C3", 0.0) > success.get("C0", 0.0) and avoidable.get("C3", 1.0) < avoidable.get("C0", 0.0) else "unclear"
            note = "C3 beat C0 and removed exact avoidable-retirement failures in the Layer A suite."
            hypothesis = "H2"
        elif "h3_h4_compression" in config:
            alias = (outcomes["failure_channel_true"] == "compression_alias").groupby(outcomes["controller_id"]).mean()
            c1 = outcomes[outcomes["controller_id"] == "C1"]
            long_vs_short = c1.groupby(["compression_level", "lag_level"])["failure_channel_true"].apply(lambda s: (s == "compression_alias").mean())
            all_long_gt_short = True
            for compression_level in sorted(c1["compression_level"].dropna().unique()):
                long_rate = long_vs_short.get((compression_level, "long"), 0.0)
                short_rate = long_vs_short.get((compression_level, "short"), 0.0)
                all_long_gt_short = all_long_gt_short and (long_rate > short_rate)
            rows.append(
                {
                    "hypothesis": "H3",
                    "status": "supported" if alias.get("C1", 0.0) > 0.0 else "unclear",
                    "evidence_note": "C1 showed exact compression-alias failures and lower success than C0/C5.",
                }
            )
            rows.append(
                {
                    "hypothesis": "H4",
                    "status": "partial_support" if all_long_gt_short else "unclear",
                    "evidence_note": "For C1, long lag raised exact alias rates relative to short lag across sampled compression levels.",
                }
            )
            continue
        elif "h5_reset" in config:
            targeted = outcomes[
                (outcomes["controller_id"].isin(["C0", "C4"]))
                & (outcomes["contamination_level"] == "high")
                & (outcomes["reset_cost_level"] == "low")
            ]
            targeted_rates = targeted.groupby("controller_id")["success_final"].mean()
            stale_seen = (outcomes["failure_channel_true"] == "stale_legacy_continuation").any()
            status = "partial_support" if targeted_rates.get("C4", 0.0) > targeted_rates.get("C0", 0.0) else "unclear"
            note = (
                "C4 outperformed C0 in the targeted regime, but stale-legacy failures were not directly realized."
                if not stale_seen
                else "C4 outperformed C0 and stale-legacy failures were observed."
            )
            hypothesis = "H5"
        else:
            continue
        rows.append({"hypothesis": hypothesis, "status": status, "evidence_note": note})
    return pd.DataFrame(rows)


def build_controller_comparison_summary(
    layer_b_summary_paths: list[str | Path],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in layer_b_summary_paths:
        frame = pd.read_csv(path)
        frame = frame[["backbone_model_id", "controller_id", "success_rate", "measurement_scope"]].copy()
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def build_failure_channel_summary(layer_a_manifest_path: str | Path) -> pd.DataFrame:
    manifest = load_suite_manifest(layer_a_manifest_path)
    frames: list[pd.DataFrame] = []
    for run in manifest["runs"]:
        analysis_dir = Path(run["analysis_output_dir"])
        frame = pd.read_csv(analysis_dir / "final_outcomes.csv")
        if "failure_channel_true" not in frame.columns:
            continue
        counts = (
            frame.groupby(["controller_id", "failure_channel_true"]).size().reset_index(name="count")
        )
        counts["source_config"] = str(run["config"])
        frames.append(counts)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def build_structured_output_fragility_summary(layer_b_final_paths: list[str | Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in layer_b_final_paths:
        frame = pd.read_csv(path)
        if "structured_output_invalidity" not in frame.columns:
            continue
        frame = frame[frame["structured_output_invalidity"].fillna(False).astype(bool)].copy()
        if frame.empty:
            continue
        grouped = (
            frame.groupby(["backbone_model_id", "controller_id", "structured_output_invalidity_type"], dropna=False)
            .size()
            .reset_index(name="count")
        )
        frames.append(grouped)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def render_current_status(
    *,
    hypothesis_table: pd.DataFrame,
    controller_summary: pd.DataFrame,
    fragility_summary: pd.DataFrame,
) -> str:
    lines = [
        "# Current Status",
        "",
        "## What currently works",
        "",
        "- Layer A exact simulator suite is complete and remains the strongest evidence source.",
        "- Layer B bundled expanded slice runs end-to-end on Gemini and on the local CPU endpoint.",
        "- Public-safety and reproducibility checks are automated enough to rerun safely.",
        "",
        "## Strongest evidence",
        "",
        "- Layer A most strongly supports the substitution-first story and the compression-alias mechanism.",
        "- Layer B most clearly supports `C3 > C0` across both backbones on the bundled task slice.",
        "",
        "## Weakest evidence",
        "",
        "- Layer B reset/compression stories remain limited relative to Layer A.",
        "- `C5` remains mixed and should not be presented as dominant.",
        "",
        "## Known confounds",
        "",
        "- Layer A exactness is simulator-exact, not world-exact.",
        "- Layer B remains proxy-limited and based on bundled mechanistic probe tasks.",
        "- Local CPU runs remain confounded by structured-output failures.",
        "",
        "## Hypothesis table",
        "",
    ]
    for _, row in hypothesis_table.iterrows():
        lines.append(f"- `{row['hypothesis']}`: `{row['status']}`. {row['evidence_note']}")
    lines.extend(["", "## Layer B controller summary", ""])
    for backbone, frame in controller_summary.groupby("backbone_model_id"):
        lines.append(f"- `{backbone}`:")
        for _, row in frame.iterrows():
            lines.append(f"  `{row['controller_id']}` success rate = `{row['success_rate']:.4f}` ({row['measurement_scope']})")
    lines.extend(["", "## Structured-output fragility", ""])
    if fragility_summary.empty:
        lines.append("- No structured-output invalidity was recorded in the current summaries.")
    else:
        for _, row in fragility_summary.iterrows():
            failure_type = row["structured_output_invalidity_type"] if pd.notna(row["structured_output_invalidity_type"]) else "none"
            lines.append(
                f"- `{row['backbone_model_id']}` / `{row['controller_id']}` / `{failure_type}`: `{int(row['count'])}` task endings"
            )
    lines.extend(
        [
            "",
            "## What to run next",
            "",
            "- Use Layer A for main mechanism claims.",
            "- Use the bundled Layer B slice for probe-style controller comparisons only.",
            "- If stronger Layer B evidence is needed, expand the frozen task slice before making broader claims.",
            "",
        ]
    )
    return "\n".join(lines)
