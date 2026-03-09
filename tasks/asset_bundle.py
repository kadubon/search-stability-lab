"""Validation and loading for bundled Layer B task assets."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, ValidationError
import yaml

from core.config import TaskManifestEntry
from core.exceptions import TaskAssetError


class BranchProfile(BaseModel):
    family_key: str
    base_score: float = Field(ge=0.0, le=1.0)
    cost: float = Field(gt=0.0)
    evidence: float = Field(default=0.2, ge=0.0, le=1.0)
    alias_proxy: float = Field(default=0.0, ge=0.0, le=1.0)
    staleness: float = Field(default=0.0, ge=0.0)
    inertia: float = Field(default=0.0, ge=0.0)
    active: bool = True
    compressed: bool = False
    recoverable: bool = True


class ProxyValidityNote(BaseModel):
    captures: list[str] = Field(default_factory=list)
    cannot_capture: list[str] = Field(default_factory=list)
    likely_false_positives: list[str] = Field(default_factory=list)
    likely_false_negatives: list[str] = Field(default_factory=list)


class TaskAssetBundle(BaseModel):
    bundle_id: str
    task_id: str
    suite: str
    intended_mechanism: str
    target_hypotheses: list[str] = Field(default_factory=list)
    primary_proxy_metrics: list[str] = Field(default_factory=list)
    language: str = "python"
    entrypoint: str | None = None
    test_command: str
    allowed_paths: list[str] = Field(default_factory=list)
    evidence_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    initial_contamination: float = Field(default=0.0, ge=0.0)
    reset_recovery_bonus: float = Field(default=0.0, ge=0.0, le=1.0)
    stale_continuation_penalty: float = Field(default=0.0, ge=0.0, le=1.0)
    compression_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    resolution_turn_gate: int = Field(default=0, ge=0)
    required_active_resolving_routes_for_success: int = Field(default=1, ge=1)
    compression_evidence_penalty: float = Field(default=0.0, ge=0.0, le=1.0)
    compression_recoverability_alias_threshold: float = Field(default=1.1, ge=0.0, le=1.0)
    proxy_validity_note: ProxyValidityNote = Field(default_factory=ProxyValidityNote)
    branch_profiles: list[BranchProfile] = Field(default_factory=list)


def _require(path: Path, description: str) -> None:
    if not path.exists():
        raise TaskAssetError(f"Task asset bundle is missing {description}: {path.as_posix()}")


def _read_metadata(path: Path) -> TaskAssetBundle:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise TaskAssetError(f"Could not parse task asset metadata: {path.as_posix()}") from exc
    if not isinstance(raw, dict):
        raise TaskAssetError(f"Task asset metadata must be a mapping: {path.as_posix()}")
    try:
        return TaskAssetBundle.model_validate(raw)
    except ValidationError as exc:
        raise TaskAssetError(f"Invalid task asset metadata: {path.as_posix()}") from exc


def load_task_asset_bundle(task: TaskManifestEntry) -> TaskAssetBundle:
    if not task.task_assets_path:
        raise TaskAssetError(f"Task {task.task_id} has no task_assets_path.")
    bundle_dir = Path(task.task_assets_path)
    _require(bundle_dir, "asset directory")
    _require(bundle_dir / "README.md", "README.md")
    _require(bundle_dir / "metadata.yaml", "metadata.yaml")
    _require(bundle_dir / "workspace", "workspace directory")
    _require(bundle_dir / "evaluation", "evaluation directory")
    bundle = _read_metadata(bundle_dir / "metadata.yaml")
    if bundle.task_id != task.task_id:
        raise TaskAssetError(
            f"Task asset metadata task_id mismatch for {task.task_id}: {bundle.task_id}"
        )
    if task.test_command and bundle.test_command != task.test_command:
        raise TaskAssetError(
            f"Task asset test_command mismatch for {task.task_id}: "
            f"manifest={task.test_command!r}, bundle={bundle.test_command!r}"
        )
    if task.target_files:
        missing_targets = [path for path in task.target_files if path not in bundle.allowed_paths]
        if missing_targets:
            raise TaskAssetError(
                f"Task asset bundle does not cover all manifest target_files for {task.task_id}: "
                f"{missing_targets}"
            )
    if not bundle.branch_profiles:
        raise TaskAssetError(f"Task asset bundle has no branch_profiles for {task.task_id}.")
    if task.suite and task.suite != bundle.suite:
        raise TaskAssetError(
            f"Task asset bundle suite mismatch for {task.task_id}: manifest={task.suite!r}, bundle={bundle.suite!r}"
        )
    if task.primary_proxy_metrics:
        missing_proxy_metrics = [metric for metric in task.primary_proxy_metrics if metric not in bundle.primary_proxy_metrics]
        if missing_proxy_metrics:
            raise TaskAssetError(
                f"Task asset bundle missing primary proxy metrics for {task.task_id}: {missing_proxy_metrics}"
            )
    workspace_files = [item for item in (bundle_dir / "workspace").rglob("*") if item.is_file()]
    if not workspace_files:
        raise TaskAssetError(f"Task asset bundle workspace is empty for {task.task_id}.")
    return bundle
