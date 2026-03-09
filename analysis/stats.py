"""Statistical utilities for summary tables and preregistered contrasts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import permutation_test
from statsmodels.stats.proportion import proportion_confint


PREREGISTERED_CONTRASTS = [("C0", "C2"), ("C0", "C3"), ("C0", "C4"), ("C0", "C5"), ("C2", "C5")]


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    lower, upper = proportion_confint(successes, total, method="wilson")
    return float(lower), float(upper)


def pairwise_contrasts(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if df.empty:
        return pd.DataFrame(rows)
    for backbone_model_id in sorted(df["backbone_model_id"].dropna().unique()):
        subset = df[df["backbone_model_id"] == backbone_model_id]
        for left, right in PREREGISTERED_CONTRASTS:
            left_values = subset.loc[subset["controller_id"] == left, "success_final"].astype(int)
            right_values = subset.loc[subset["controller_id"] == right, "success_final"].astype(int)
            if left_values.empty or right_values.empty:
                continue
            if len(left_values) < 2 or len(right_values) < 2:
                p_value = None
            else:
                result = permutation_test(
                    data=(left_values.to_numpy(), right_values.to_numpy()),
                    statistic=lambda x, y, axis: x.mean(axis=axis) - y.mean(axis=axis),
                    permutation_type="independent",
                    n_resamples=min(500, max(100, len(left_values) * len(right_values) * 5)),
                    alternative="two-sided",
                )
                p_value = float(result.pvalue)
            rows.append(
                {
                    "backbone_model_id": backbone_model_id,
                    "contrast": f"{left}_vs_{right}",
                    "left_mean": float(left_values.mean()),
                    "right_mean": float(right_values.mean()),
                    "difference": float(left_values.mean() - right_values.mean()),
                    "p_value": p_value,
                }
            )
    return pd.DataFrame(rows)


def fit_regression(df: pd.DataFrame, output_dir: Path) -> str:
    if df.empty:
        return "No outcomes available for regression."
    frame = df.copy()
    for column in ["budget_level", "lag_level", "compression_level", "contamination_level", "backbone_model_id"]:
        if column not in frame:
            frame[column] = "unknown"
    formula = (
        "success_final ~ C(controller_id) + C(budget_level) + C(lag_level) + "
        "C(compression_level) + C(contamination_level) + C(backbone_model_id)"
    )
    try:
        model = sm.BinomialBayesMixedGLM.from_formula(
            formula,
            {"group": "0 + C(group_id)"},
            frame.assign(group_id=frame["group_id"].astype(str)),
        )
        result = model.fit_vb()
        summary = str(result.summary())
        path = output_dir / "regression_summary.txt"
        path.write_text(summary, encoding="utf-8")
        return "mixed_effects"
    except Exception:
        glm = smf.glm(formula=formula, data=frame, family=sm.families.Binomial()).fit()
        summary = str(glm.summary())
        path = output_dir / "regression_summary.txt"
        path.write_text(summary, encoding="utf-8")
        return "glm_fallback"
