"""Experiment condition helpers for Layer A."""

from __future__ import annotations

from itertools import product

from core.config import SimulatorExperimentConfig
from simulator.types import SimulatorCondition


BUDGET_LEVELS = {"low": 3.6, "medium": 5.2, "high": 7.2}
LAG_STEPS = {"short": 3, "medium": 5, "long": 7}
OVERLAP_LEVELS = {"low": 0.15, "medium": 0.35, "high": 0.55}
COMPRESSION_LEVELS = {
    "none": (1.0, 0.0),
    "mild": (0.72, 0.18),
    "strong": (0.45, 0.4),
}
CONTAMINATION_LEVELS = {"low": 0.12, "medium": 0.28, "high": 0.5}
RESET_COST_LEVELS = {"low": 0.35, "medium": 0.75, "high": 1.2}


def expand_conditions(config: SimulatorExperimentConfig) -> list[SimulatorCondition]:
    conditions: list[SimulatorCondition] = []
    for budget, lag, overlap, compression, contamination, reset_cost in product(
        config.budgets,
        config.lags,
        config.overlaps,
        config.compression_strengths,
        config.contamination_levels,
        config.reset_cost_levels,
    ):
        verification_step = min(config.step_limit - 1, LAG_STEPS[lag])
        ratio, alias_scale = COMPRESSION_LEVELS[compression]
        conditions.append(
            SimulatorCondition(
                budget_level=budget,
                lag_level=lag,
                overlap_level=overlap,
                compression_level=compression,
                contamination_level=contamination,
                reset_cost_level=reset_cost,
                budget_cap=BUDGET_LEVELS[budget],
                verification_step=verification_step,
                overlap_scale=OVERLAP_LEVELS[overlap],
                compression_ratio=ratio,
                compression_alias_scale=alias_scale,
                contamination_scale=CONTAMINATION_LEVELS[contamination],
                reset_cost=RESET_COST_LEVELS[reset_cost],
                step_limit=config.step_limit,
                hard_cap_budget=config.hard_cap_budget,
            )
        )
    return conditions

