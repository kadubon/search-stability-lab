from __future__ import annotations

from controllers.factory import build_controller
from core.config import (
    load_controller_config,
    load_model_config,
    load_real_task_experiment,
    load_task_manifest,
)
from core.event_logger import EventLogger
from models.factory import build_model_adapter
from tasks.asset_bundle import load_task_asset_bundle
from tasks.harness import run_task_slice


def test_task_harness_mock_smoke(tmp_path) -> None:
    experiment = load_real_task_experiment("configs/experiments/real_tasks.yaml")
    manifest = load_task_manifest(experiment.manifest_path)
    controller = build_controller(load_controller_config("configs/controllers/c3.yaml"))
    model_adapter = build_model_adapter(load_model_config(experiment.model_path))
    logger = EventLogger(tmp_path / "events.jsonl")

    results = run_task_slice(
        run_id="task-run",
        seed=99,
        experiment=experiment,
        manifest_entries=manifest.tasks[:1],
        controller=controller,
        model_adapter=model_adapter,
        logger=logger,
    )

    assert len(results) == 1
    result = results[0]
    assert "represented_candidate_family_count_proxy" in result
    assert isinstance(result["resolved"], bool)


def test_task_harness_skips_missing_assets_without_fake_eval(tmp_path) -> None:
    experiment = load_real_task_experiment("configs/experiments/real_tasks.yaml")
    experiment = experiment.model_copy(update={"mock_mode": False, "strict_assets": False})
    manifest = load_task_manifest(experiment.manifest_path)
    task = manifest.tasks[0].model_copy(update={"task_assets_path": "tasks/local/nonexistent_asset"})
    controller = build_controller(load_controller_config("configs/controllers/c3.yaml"))
    model_adapter = build_model_adapter(load_model_config(experiment.model_path))
    logger = EventLogger(tmp_path / "events.jsonl")

    results = run_task_slice(
        run_id="task-run",
        seed=99,
        experiment=experiment,
        manifest_entries=[task],
        controller=controller,
        model_adapter=model_adapter,
        logger=logger,
    )

    assert len(results) == 1
    result = results[0]
    assert result["resolved"] is None
    assert result["task_status"] == "skipped_missing_assets"


def test_bundled_task_assets_validate() -> None:
    manifest = load_task_manifest("tasks/manifests/frozen_task_slice_v1.yaml")
    bundle = load_task_asset_bundle(manifest.tasks[0])
    assert bundle.task_id == "task-001"
    assert bundle.branch_profiles


def test_expanded_bundled_task_assets_validate() -> None:
    manifest = load_task_manifest("tasks/manifests/frozen_task_slice_v2.yaml")
    assert len(manifest.tasks) >= 6
    bundle = load_task_asset_bundle(manifest.tasks[-1])
    assert bundle.task_id == "task-006"
    assert bundle.branch_profiles


def test_probe_suite_manifests_validate() -> None:
    substitution = load_task_manifest("tasks/manifests/substitution_probe_suite_v1.yaml")
    compression = load_task_manifest("tasks/manifests/compression_probe_suite_v1.yaml")
    reset = load_task_manifest("tasks/manifests/reset_probe_suite_v1.yaml")
    assert {task.suite for task in substitution.tasks} == {"substitution"}
    assert {task.suite for task in compression.tasks} == {"compression"}
    assert {task.suite for task in reset.tasks} == {"reset"}
    assert load_task_asset_bundle(compression.tasks[-1]).task_id == "task-007"
    assert load_task_asset_bundle(reset.tasks[-1]).task_id == "task-008"


def test_task_harness_runs_with_valid_nonmock_assets(tmp_path) -> None:
    experiment = load_real_task_experiment("configs/experiments/real_tasks.yaml")
    experiment = experiment.model_copy(
        update={
            "mock_mode": False,
            "strict_assets": True,
            "manifest_path": "tasks/manifests/frozen_task_slice_v1.yaml",
            "token_budget": 1024,
        }
    )
    manifest = load_task_manifest(experiment.manifest_path)
    controller = build_controller(load_controller_config("configs/controllers/c3.yaml"))
    model_adapter = build_model_adapter(load_model_config(experiment.model_path))
    logger = EventLogger(tmp_path / "events.jsonl")

    results = run_task_slice(
        run_id="task-run-nonmock",
        seed=101,
        experiment=experiment,
        manifest_entries=manifest.tasks[:1],
        controller=controller,
        model_adapter=model_adapter,
        logger=logger,
    )

    assert len(results) == 1
    result = results[0]
    assert isinstance(result["resolved"], bool)
    assert result["family_proxy_rule"] == "parser-defaults"
