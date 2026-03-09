"""Run Layer B task harness from YAML config."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from controllers.factory import build_controller
from core.config import (
    load_controller_config,
    load_model_config,
    load_real_task_experiment,
    load_task_manifest,
)
from core.event_logger import EventLogger
from core.guardrails import validate_real_task_design, write_run_manifest
from core.run_metadata import build_run_id
from models.factory import build_model_adapter
from tasks.harness import run_task_slice


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments/real_tasks.yaml")
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--controllers", nargs="*", default=None)
    args = parser.parse_args()

    experiment = load_real_task_experiment(args.config)
    model_config = load_model_config(experiment.model_path)
    model_adapter = build_model_adapter(model_config)
    manifest = load_task_manifest(experiment.manifest_path)
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
    manifest_entries = manifest.tasks[: args.max_tasks] if args.max_tasks is not None else manifest.tasks
    run_id = build_run_id(experiment.output.run_name_prefix)
    output_dir = Path(experiment.output.base_dir) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = EventLogger(output_dir / "events.jsonl")
    report = validate_real_task_design(experiment, model_config, controller_configs)
    write_run_manifest(
        output_dir=output_dir,
        layer="layer_b",
        experiment=experiment,
        model_config=model_config,
        controllers=controller_configs,
        report=report,
    )
    results: list[dict[str, object]] = []
    for index, controller in enumerate(controllers):
        results.extend(
            run_task_slice(
                run_id=run_id,
                seed=experiment.base_seed + index * 100,
                experiment=experiment,
                manifest_entries=manifest_entries,
                controller=controller,
                model_adapter=model_adapter,
                logger=logger,
            )
        )
    pd.DataFrame(results).to_csv(output_dir / "task_results.csv", index=False)
    print(output_dir)


if __name__ == "__main__":
    main()
