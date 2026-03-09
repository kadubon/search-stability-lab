"""Figure generation for required publication-ready plots."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _backbone_label(frame: pd.DataFrame) -> str:
    if "backbone_model_id" not in frame.columns or frame.empty:
        return "backbone=unspecified"
    values = sorted(str(item) for item in frame["backbone_model_id"].dropna().unique())
    if not values:
        return "backbone=unspecified"
    if len(values) == 1:
        return f"backbone={values[0]}"
    return "backbone=mixed"


def _has_columns(frame: pd.DataFrame, *columns: str) -> bool:
    return all(column in frame.columns for column in columns)


def figure_success_vs_budget(finals: pd.DataFrame, output_dir: Path) -> None:
    if not _has_columns(finals, "layer", "budget_level", "controller_id", "success_final"):
        return
    subset = finals[finals["layer"] == "layer_a"].copy()
    if subset.empty:
        return
    rates = subset.groupby(["controller_id", "budget_level"])["success_final"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    order = ["low", "medium", "high"]
    for controller_id, frame in rates.groupby("controller_id"):
        frame = frame.set_index("budget_level").reindex(order).reset_index()
        ax.plot(frame["budget_level"], frame["success_final"], marker="o", label=controller_id)
    ax.set_title(f"Layer A exact success vs budget by controller ({_backbone_label(subset)})")
    ax.set_xlabel("Budget level")
    ax.set_ylabel("Success rate (exact)")
    ax.set_ylim(0.0, 1.0)
    ax.legend()
    _save(fig, output_dir / "figure_1_success_vs_budget.png")


def figure_success_vs_compression(finals: pd.DataFrame, output_dir: Path) -> None:
    if not _has_columns(finals, "layer", "lag_level", "compression_level", "controller_id", "success_final"):
        return
    subset = finals[(finals["layer"] == "layer_a") & finals["lag_level"].notna()].copy()
    if subset.empty:
        return
    compression_order = ["none", "mild", "strong"]
    lag_order = ["short", "medium", "long"]
    fig, axes = plt.subplots(1, len(lag_order), figsize=(13, 4), sharey=True)
    for axis, lag in zip(axes, lag_order):
        frame = subset[subset["lag_level"] == lag]
        if frame.empty:
            axis.set_visible(False)
            continue
        rates = frame.groupby(["controller_id", "compression_level"])["success_final"].mean().reset_index()
        for controller_id, controller_frame in rates.groupby("controller_id"):
            controller_frame = controller_frame.set_index("compression_level").reindex(compression_order).reset_index()
            axis.plot(controller_frame["compression_level"], controller_frame["success_final"], marker="o", label=controller_id)
        axis.set_title(f"Lag={lag}")
        axis.set_xlabel("Compression strength")
        axis.set_ylim(0.0, 1.0)
    axes[0].set_ylabel("Success rate (exact)")
    handles, labels = axes[0].get_legend_handles_labels()
    if labels:
        fig.legend(handles, labels, loc="upper center", ncol=max(1, len(labels)))
    fig.suptitle(
        f"Layer A exact success vs compression under multiple lag settings ({_backbone_label(subset)})",
        y=1.05,
    )
    _save(fig, output_dir / "figure_2_success_vs_compression_and_lag.png")


def figure_reset_benefit(finals: pd.DataFrame, output_dir: Path) -> None:
    if not _has_columns(
        finals,
        "layer",
        "contamination_level",
        "reset_cost_level",
        "controller_id",
        "success_final",
    ):
        return
    subset = finals[(finals["layer"] == "layer_a") & finals["contamination_level"].notna()].copy()
    if subset.empty:
        return
    baseline = subset[subset["controller_id"] == "C0"].groupby(["contamination_level", "reset_cost_level"])["success_final"].mean()
    theory = subset[subset["controller_id"].isin(["C4", "C5"])].groupby(["contamination_level", "reset_cost_level"])["success_final"].mean()
    benefit = (theory - baseline).reset_index(name="reset_benefit")
    if benefit.empty:
        return
    contamination_order = ["low", "medium", "high"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for reset_cost_level, frame in benefit.groupby("reset_cost_level"):
        frame = frame.set_index("contamination_level").reindex(contamination_order).reset_index()
        ax.plot(frame["contamination_level"], frame["reset_benefit"], marker="o", label=f"reset cost={reset_cost_level}")
    ax.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title(f"Layer A exact reset benefit vs contamination and reset cost ({_backbone_label(subset)})")
    ax.set_xlabel("Legacy contamination")
    ax.set_ylabel("Success-rate lift vs C0")
    ax.legend()
    _save(fig, output_dir / "figure_3_reset_benefit.png")


def figure_failure_composition(finals: pd.DataFrame, output_dir: Path) -> None:
    if not _has_columns(finals, "layer", "failure_channel_true", "controller_id"):
        return
    subset = finals[(finals["layer"] == "layer_a") & finals["failure_channel_true"].notna()].copy()
    if subset.empty:
        return
    composition = (
        subset.groupby(["controller_id", "failure_channel_true"]).size().unstack(fill_value=0)
    )
    composition = composition.div(composition.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bottom = None
    for column in composition.columns:
        values = composition[column]
        ax.bar(composition.index, values, bottom=bottom, label=column)
        bottom = values if bottom is None else bottom + values
    ax.set_title(f"Layer A exact failure-channel composition by controller ({_backbone_label(subset)})")
    ax.set_ylabel("Share of failed episodes")
    ax.set_ylim(0.0, 1.0)
    ax.legend()
    _save(fig, output_dir / "figure_4_failure_channel_composition.png")
