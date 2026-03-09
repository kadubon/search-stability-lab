"""Validate scientific guardrails for an experiment config."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.config import (  # noqa: E402
    load_controller_config,
    load_model_config,
    load_real_task_experiment,
    load_simulator_experiment,
)
from core.guardrails import validate_real_task_design, validate_simulator_design  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", choices=["layer_a", "layer_b"], required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    if args.layer == "layer_a":
        experiment = load_simulator_experiment(args.config)
        model_config = load_model_config(experiment.model_path)
        controllers = [load_controller_config(path) for path in experiment.controller_paths]
        report = validate_simulator_design(experiment, model_config, controllers)
    else:
        experiment = load_real_task_experiment(args.config)
        model_config = load_model_config(experiment.model_path)
        controllers = [load_controller_config(path) for path in experiment.controller_paths]
        report = validate_real_task_design(experiment, model_config, controllers)

    print("OK" if report.ok else "ERROR")
    if report.checks:
        print("Checks:")
        for item in report.checks:
            print(f"- {item}")
    if report.warnings:
        print("Warnings:")
        for item in report.warnings:
            print(f"- {item}")
    if report.errors:
        print("Errors:")
        for item in report.errors:
            print(f"- {item}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
