from __future__ import annotations

import pandas as pd

from analysis.aggregate import build_summary_tables, final_outcomes, load_events
from analysis.figures import (
    figure_failure_composition,
    figure_reset_benefit,
    figure_success_vs_budget,
    figure_success_vs_compression,
)
from analysis.stats import pairwise_contrasts
from controllers.factory import build_controller
from core.config import (
    load_controller_config,
    load_model_config,
    load_real_task_experiment,
    load_simulator_experiment,
    load_task_manifest,
)
from core.event_logger import EventLogger
from models.factory import build_model_adapter
from simulator.engine import run_episode
from simulator.scenarios import expand_conditions
from tasks.harness import run_task_slice


def test_analysis_generates_outputs(tmp_path) -> None:
    sim_experiment = load_simulator_experiment("configs/experiments/pilot.yaml")
    sim_model = load_model_config(sim_experiment.model_path)
    sim_controller = build_controller(load_controller_config("configs/controllers/c0.yaml"))
    sim_logger = EventLogger(tmp_path / "sim_events.jsonl")
    condition = expand_conditions(sim_experiment)[0]
    run_episode(
        run_id="analysis-run",
        seed=1,
        episode_id="sim-episode",
        condition=condition,
        controller=sim_controller,
        model_config=sim_model,
        logger=sim_logger,
        families_range=sim_experiment.families_range,
        routes_per_family_range=sim_experiment.routes_per_family_range,
        prompt_version=sim_model.prompt_version,
    )

    task_experiment = load_real_task_experiment("configs/experiments/real_tasks.yaml")
    task_manifest = load_task_manifest(task_experiment.manifest_path)
    task_model = build_model_adapter(load_model_config(task_experiment.model_path))
    task_controller = build_controller(load_controller_config("configs/controllers/c5.yaml"))
    task_logger = EventLogger(tmp_path / "task_events.jsonl")
    run_task_slice(
        run_id="analysis-run",
        seed=2,
        experiment=task_experiment,
        manifest_entries=task_manifest.tasks[:1],
        controller=task_controller,
        model_adapter=task_model,
        logger=task_logger,
    )

    events = load_events([tmp_path / "sim_events.jsonl", tmp_path / "task_events.jsonl"])
    finals = final_outcomes(events)
    summary = build_summary_tables(finals)
    contrasts = pairwise_contrasts(finals[finals["layer"] == "layer_a"])
    output_dir = tmp_path / "analysis"
    output_dir.mkdir()
    figure_success_vs_budget(finals, output_dir)
    figure_success_vs_compression(finals, output_dir)
    figure_reset_benefit(finals, output_dir)
    figure_failure_composition(finals, output_dir)

    assert not events.empty
    assert isinstance(summary, pd.DataFrame)
    assert isinstance(contrasts, pd.DataFrame)
    assert (output_dir / "figure_1_success_vs_budget.png").exists()


def test_analysis_handles_layer_b_only_inputs(tmp_path) -> None:
    task_experiment = load_real_task_experiment("configs/experiments/real_tasks.yaml")
    task_manifest = load_task_manifest(task_experiment.manifest_path)
    task_model = build_model_adapter(load_model_config(task_experiment.model_path))
    task_controller = build_controller(load_controller_config("configs/controllers/c5.yaml"))
    task_logger = EventLogger(tmp_path / "task_events.jsonl")
    run_task_slice(
        run_id="analysis-layer-b-only",
        seed=3,
        experiment=task_experiment,
        manifest_entries=task_manifest.tasks[:1],
        controller=task_controller,
        model_adapter=task_model,
        logger=task_logger,
    )

    events = load_events([tmp_path / "task_events.jsonl"])
    finals = final_outcomes(events)
    output_dir = tmp_path / "analysis"
    output_dir.mkdir()
    figure_success_vs_budget(finals, output_dir)
    figure_success_vs_compression(finals, output_dir)
    figure_reset_benefit(finals, output_dir)
    figure_failure_composition(finals, output_dir)

    assert not finals.empty
    assert not (output_dir / "figure_1_success_vs_budget.png").exists()
