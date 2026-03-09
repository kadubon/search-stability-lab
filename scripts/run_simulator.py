"""Run Layer A simulator experiments from YAML config."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from controllers.factory import build_controller
from core.config import load_controller_config, load_model_config, load_simulator_experiment
from core.event_logger import EventLogger
from core.guardrails import validate_simulator_design, write_run_manifest
from core.run_metadata import build_run_id
from simulator.engine import run_episode
from simulator.scenarios import expand_conditions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments/pilot.yaml")
    parser.add_argument("--max-conditions", type=int, default=None)
    parser.add_argument("--max-episodes", type=int, default=None)
    parser.add_argument("--controllers", nargs="*", default=None)
    args = parser.parse_args()

    experiment = load_simulator_experiment(args.config)
    model_config = load_model_config(experiment.model_path)
    controller_configs = [load_controller_config(path) for path in experiment.controller_paths]
    controllers = [build_controller(config) for config in controller_configs]
    if args.controllers:
        allowed = set(args.controllers)
        paired = [
            (controller, config)
            for controller, config in zip(controllers, controller_configs, strict=False)
            if controller.controller_id in allowed
        ]
        controllers = [controller for controller, _ in paired]
        controller_configs = [config for _, config in paired]
    run_id = build_run_id(experiment.output.run_name_prefix)
    output_dir = Path(experiment.output.base_dir) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = EventLogger(output_dir / "events.jsonl")
    report = validate_simulator_design(experiment, model_config, controller_configs)
    write_run_manifest(
        output_dir=output_dir,
        layer="layer_a",
        experiment=experiment,
        model_config=model_config,
        controllers=controller_configs,
        report=report,
    )
    conditions = expand_conditions(experiment)
    if args.max_conditions is not None:
        conditions = conditions[: args.max_conditions]
    outcomes: list[dict[str, object]] = []
    for controller in controllers:
        for condition_index, condition in enumerate(conditions):
            episode_count = args.max_episodes or experiment.episodes_per_condition
            for episode_index in range(episode_count):
                seed = experiment.base_seed + condition_index * 1000 + episode_index
                outcome = run_episode(
                    run_id=run_id,
                    seed=seed,
                    episode_id=f"{controller.controller_id}-cond-{condition_index}-ep-{episode_index}",
                    condition=condition,
                    controller=controller,
                    model_config=model_config,
                    logger=logger,
                    families_range=experiment.families_range,
                    routes_per_family_range=experiment.routes_per_family_range,
                    prompt_version=model_config.prompt_version,
                )
                outcomes.append(outcome)
    pd.DataFrame(outcomes).to_csv(output_dir / "outcomes.csv", index=False)
    print(output_dir)


if __name__ == "__main__":
    main()
