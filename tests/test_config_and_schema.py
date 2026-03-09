from __future__ import annotations

import pytest

from core.config import (
    load_controller_config,
    load_model_config,
    load_real_task_experiment,
    load_simulator_experiment,
    load_task_manifest,
)
from core.guardrails import validate_real_task_design, validate_simulator_design, write_run_manifest
from core.exceptions import StructuredOutputError
from core.schema_utils import validate_payload


def test_experiment_configs_load_with_aliases() -> None:
    simulator = load_simulator_experiment("configs/experiments/pilot.yaml")
    real_tasks = load_real_task_experiment("configs/experiments/real_tasks.yaml")
    manifest = load_task_manifest("tasks/examples/mock_task_slice.yaml")

    assert simulator.model_path == "configs/models/mock.yaml"
    assert simulator.controller_paths
    assert real_tasks.model_path == "configs/models/mock.yaml"
    assert len(manifest.tasks) == 3


def test_model_config_env_overrides(monkeypatch) -> None:
    monkeypatch.setenv("LOCAL_LLM_MODEL", "gemma3:1b")
    monkeypatch.setenv("LOCAL_LLM_ENDPOINT", "http://127.0.0.1:11434")
    model_config = load_model_config("configs/models/local_cpu.yaml")
    assert model_config.model_id == "gemma3:1b"
    assert model_config.api_base == "http://127.0.0.1:11434"


def test_guardrails_and_run_manifest(tmp_path) -> None:
    sim_experiment = load_simulator_experiment("configs/experiments/pilot.yaml")
    sim_model = load_model_config(sim_experiment.model_path)
    sim_controller_configs = [
        load_controller_config("configs/controllers/c0.yaml"),
        load_controller_config("configs/controllers/c5.yaml"),
    ]
    sim_report = validate_simulator_design(sim_experiment, sim_model, sim_controller_configs)
    assert sim_report.ok
    manifest_path = write_run_manifest(
        output_dir=tmp_path / "sim",
        layer="layer_a",
        experiment=sim_experiment,
        model_config=sim_model,
        controllers=sim_controller_configs,
        report=sim_report,
    )
    assert manifest_path.exists()

    real_experiment = load_real_task_experiment("configs/experiments/real_tasks.yaml")
    real_model = load_model_config(real_experiment.model_path)
    real_controller_configs = [
        load_controller_config("configs/controllers/c0.yaml"),
        load_controller_config("configs/controllers/c3.yaml"),
    ]
    real_report = validate_real_task_design(real_experiment, real_model, real_controller_configs)
    assert real_report.ok


def test_schema_validation_rejects_malformed_payload() -> None:
    valid = {
        "step_id": "s1",
        "decision_type": "tool",
        "target_ids": ["r1"],
        "family_ids": ["f1"],
        "confidence": 0.5,
        "rationale_short": "test",
        "predicted_risk": {
            "adequacy_loss": 0.2,
            "alias_risk": 0.1,
            "staleness_risk": 0.3,
        },
        "estimated_budget_after": 1.0,
    }
    validate_payload("step_decision", valid)
    invalid = {"decision_type": "tool"}
    with pytest.raises(StructuredOutputError):
        validate_payload("step_decision", invalid)
