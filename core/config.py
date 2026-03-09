"""YAML-backed configuration loading."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, ValidationError

from core.env import load_repo_env
from core.exceptions import ConfigError


class RetryPolicy(BaseModel):
    max_retries: int = Field(default=2, ge=0, le=5)
    timeout_seconds: float = Field(default=30.0, gt=0.0)


class LayerAProfile(BaseModel):
    decision_noise: float = Field(default=0.05, ge=0.0, le=1.0)
    raw_failure_rate: float = Field(default=0.03, ge=0.0, le=1.0)
    evidence_gain_scale: float = Field(default=1.0, ge=0.1)


class ModelConfig(BaseModel):
    model_id: str
    provider: Literal["mock", "gemini", "local_endpoint"]
    endpoint_family: str
    prompt_version: str = "v1"
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    top_p: float | None = Field(default=None, gt=0.0, le=1.0)
    max_output_tokens: int = Field(default=512, gt=0)
    structured_output_mode: str = "json_schema"
    tool_calling_mode: str = "none"
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    api_base: str | None = None
    api_base_env: str | None = None
    api_key_env: str | None = None
    model_id_env: str | None = None
    sdk_version_hint: str | None = None
    local_api_style: Literal["ollama", "openai_compatible"] | None = None
    layer_a_profile: LayerAProfile = Field(default_factory=LayerAProfile)


class ControllerConfig(BaseModel):
    controller_id: str
    family_reserve_min: int = Field(default=2, ge=1)
    compression_caution_threshold: float = Field(default=0.35, ge=0.0, le=1.0)
    reset_threshold: float = Field(default=0.6, ge=0.0)
    random_budget_ratio: float = Field(default=0.8, gt=0.0, le=1.0)
    branch_probability: float = Field(default=0.25, ge=0.0, le=1.0)


class OutputConfig(BaseModel):
    base_dir: str = "artifacts"
    run_name_prefix: str = "run"


class SimulatorExperimentConfig(BaseModel):
    experiment_id: str
    layer: Literal["layer_a"] = "layer_a"
    description: str
    model_path: str = Field(alias="model_config")
    controller_paths: list[str] = Field(alias="controller_configs")
    output: OutputConfig = Field(default_factory=OutputConfig)
    base_seed: int = 7
    episodes_per_condition: int = Field(default=10, gt=0)
    step_limit: int = Field(default=8, ge=4)
    hard_cap_budget: bool = True
    budgets: list[str]
    lags: list[str]
    overlaps: list[str]
    compression_strengths: list[str]
    contamination_levels: list[str]
    reset_cost_levels: list[str]
    families_range: tuple[int, int] = (4, 6)
    routes_per_family_range: tuple[int, int] = (2, 3)


class RealTaskExperimentConfig(BaseModel):
    experiment_id: str
    layer: Literal["layer_b"] = "layer_b"
    description: str
    model_path: str = Field(alias="model_config")
    controller_paths: list[str] = Field(alias="controller_configs")
    output: OutputConfig = Field(default_factory=OutputConfig)
    base_seed: int = 19
    manifest_path: str
    max_turns: int = Field(default=6, gt=0)
    token_budget: int = Field(default=4096, gt=0)
    mock_mode: bool = True
    strict_assets: bool = False
    fixed_backbone_block_label: str = "default_block"


class TaskManifestEntry(BaseModel):
    task_id: str
    repository: str
    title: str
    issue_summary: str
    target_files: list[str] = Field(default_factory=list)
    test_command: str | None = None
    task_assets_path: str | None = None
    proxy_family_hint: str | None = None
    resolving_family_keys: list[str] = Field(default_factory=list)
    suite: str | None = None
    probe_purpose: str | None = None
    target_hypotheses: list[str] = Field(default_factory=list)
    primary_proxy_metrics: list[str] = Field(default_factory=list)
    suitable_backbones: list[str] = Field(default_factory=list)


class TaskManifest(BaseModel):
    manifest_id: str
    description: str
    tasks: list[TaskManifestEntry]


def load_yaml(path: str | Path) -> dict[str, Any]:
    load_repo_env()
    resolved = Path(path)
    if not resolved.exists():
        raise ConfigError(f"Configuration file not found: {resolved}")
    try:
        data = yaml.safe_load(resolved.read_text(encoding='utf-8'))
    except yaml.YAMLError as exc:
        raise ConfigError(f"Could not parse YAML from {resolved}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"Configuration root must be a mapping: {resolved}")
    return data


def load_model(path: str | Path, model_type: type[BaseModel]) -> BaseModel:
    data = load_yaml(path)
    try:
        return model_type.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid configuration in {path}") from exc


def load_model_config(path: str | Path) -> ModelConfig:
    config = load_model(path, ModelConfig)  # type: ignore[assignment]
    if config.model_id_env:
        override = os.environ.get(config.model_id_env)
        if override:
            config = config.model_copy(update={"model_id": override})
    if config.api_base_env:
        override = os.environ.get(config.api_base_env)
        if override:
            config = config.model_copy(update={"api_base": override})
    return config  # type: ignore[return-value]


def load_controller_config(path: str | Path) -> ControllerConfig:
    return load_model(path, ControllerConfig)  # type: ignore[return-value]


def load_simulator_experiment(path: str | Path) -> SimulatorExperimentConfig:
    return load_model(path, SimulatorExperimentConfig)  # type: ignore[return-value]


def load_real_task_experiment(path: str | Path) -> RealTaskExperimentConfig:
    return load_model(path, RealTaskExperimentConfig)  # type: ignore[return-value]


def load_task_manifest(path: str | Path) -> TaskManifest:
    return load_model(path, TaskManifest)  # type: ignore[return-value]
