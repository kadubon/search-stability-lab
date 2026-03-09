"""Layer B probe-suite summaries."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_layer_b_finals(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    return frame[frame["layer"] == "layer_b"].copy() if "layer" in frame.columns else frame


def controller_comparison_summary(finals: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        finals.groupby(["suite", "backbone_model_id", "controller_id"], dropna=False)["success_final"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "success_rate", "count": "sample_count"})
    )
    grouped["measurement_scope"] = "proxy (task harness)"
    return grouped


def proxy_metric_summary(finals: pd.DataFrame) -> pd.DataFrame:
    metric_columns = [
        "represented_candidate_family_count_proxy",
        "recoverable_candidate_count_proxy",
        "compression_collision_proxy",
        "avoidable_retirement_proxy",
        "reset_helpfulness_proxy",
        "stale_continuation_proxy",
        "post_reset_resolution_improvement_proxy",
    ]
    available = [column for column in metric_columns if column in finals.columns]
    if not available:
        return pd.DataFrame()
    grouped = finals.groupby(["suite", "backbone_model_id", "controller_id"], dropna=False)[available].mean().reset_index()
    grouped["measurement_scope"] = "proxy (task harness)"
    return grouped


def compression_collision_summary(finals: pd.DataFrame) -> pd.DataFrame:
    block = finals[finals["suite"] == "compression"].copy()
    if block.empty or "compression_collision_proxy" not in block.columns:
        return pd.DataFrame()
    grouped = (
        block.groupby(["backbone_model_id", "controller_id"], dropna=False)["compression_collision_proxy"]
        .agg(["mean", "max"])
        .reset_index()
        .rename(columns={"mean": "mean_collision_proxy", "max": "max_collision_proxy"})
    )
    grouped["measurement_scope"] = "proxy (task harness)"
    return grouped


def structured_output_fragility_summary(finals: pd.DataFrame) -> pd.DataFrame:
    available = finals.copy()
    if "structured_output_invalidity" not in available.columns:
        return pd.DataFrame()
    grouped = (
        available.groupby(
            ["suite", "backbone_model_id", "controller_id", "structured_output_invalidity_type"],
            dropna=False,
        )["structured_output_invalidity"]
        .agg(["mean", "sum"])
        .reset_index()
        .rename(columns={"mean": "invalidity_rate", "sum": "invalidity_count"})
    )
    if "structured_output_repaired" in available.columns:
        repaired = (
            available.groupby(["suite", "backbone_model_id", "controller_id"], dropna=False)["structured_output_repaired"]
            .mean()
            .reset_index()
            .rename(columns={"structured_output_repaired": "repaired_rate"})
        )
        grouped = grouped.merge(repaired, on=["suite", "backbone_model_id", "controller_id"], how="left")
    grouped["measurement_scope"] = "proxy (task harness)"
    return grouped


def conservative_interpretation(finals: pd.DataFrame, suite: str) -> str:
    block = finals[finals["suite"] == suite].copy()
    if block.empty:
        return f"# {suite.title()} Probe Status\n\nNo analyzed outcomes are available for this suite yet.\n"
    success = block.groupby("controller_id")["success_final"].mean()
    invalidity = (
        block.groupby("controller_id")["structured_output_invalidity"].mean()
        if "structured_output_invalidity" in block.columns
        else pd.Series(dtype=float)
    )
    lines = [
        f"# {suite.title()} Probe Status",
        "",
        "This summary is probe-scale and proxy-only. It is not broad benchmark validation.",
        "",
        "## Conservative read",
        "",
    ]
    if suite == "substitution":
        if success.get("C3", 0.0) > success.get("C0", 0.0):
            lines.append("- `C3 > C0` remains the clearest Layer B substitution result in the available runs.")
        else:
            lines.append("- The available runs do not yet show a clean substitution advantage.")
    elif suite == "compression":
        proxy_means = (
            block.groupby("controller_id")["compression_collision_proxy"].mean()
            if "compression_collision_proxy" in block.columns
            else pd.Series(dtype=float)
        )
        if max(success.get("C0", 0.0), success.get("C5", 0.0)) > success.get("C1", 0.0):
            lines.append("- The available runs now show outcome-level sensitivity against compression-heavy control.")
        elif proxy_means.get("C1", 0.0) > max(proxy_means.get("C0", 0.0), proxy_means.get("C5", 0.0)):
            lines.append("- The available runs show compression evidence mainly through proxy-level collision signals.")
        else:
            lines.append("- The available runs do not yet isolate a clear compression signal.")
    elif suite == "reset":
        if success.get("C4", 0.0) > success.get("C0", 0.0):
            lines.append("- The available runs are directionally consistent with targeted reset helping in some probe tasks.")
        else:
            lines.append("- The available runs do not yet isolate a clean reset advantage.")
    if not invalidity.empty and invalidity.max() > 0:
        lines.append("- Structured-output invalidity remains a confound and should be checked before reading controller differences.")
    lines.extend(
        [
            "",
            "## Scope limit",
            "",
            "- Treat this suite as a mechanistic probe block that complements Layer A.",
            "- Do not read proxy behavior here as latent truth about adequate-family survival in the world.",
            "",
        ]
    )
    return "\n".join(lines)
