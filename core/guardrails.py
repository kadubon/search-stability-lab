"""Scientific guardrails and run-manifest helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.config import (
    ControllerConfig,
    ModelConfig,
    RealTaskExperimentConfig,
    SimulatorExperimentConfig,
)
from core.run_metadata import get_code_revision


THEORY_HYPOTHESES = {
    "H1": "Budget-threshold hypothesis",
    "H2": "Substitution-first hypothesis",
    "H3": "Compression-alias hypothesis",
    "H4": "Lag-amplification hypothesis",
    "H5": "Reset-rationality hypothesis",
    "H6": "Controller-not-model hypothesis",
}


@dataclass(slots=True)
class GuardrailReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_simulator_design(
    experiment: SimulatorExperimentConfig,
    model_config: ModelConfig,
    controllers: list[ControllerConfig],
) -> GuardrailReport:
    report = GuardrailReport()
    report.checks.append("Single model config is used for the whole simulator comparison block.")
    if len(controllers) < 2:
        report.warnings.append(
            "Simulator comparison block has fewer than two controllers; this is valid for smoke tests but weak for theory comparison."
        )
    if not experiment.hard_cap_budget:
        report.warnings.append(
            "Main theory-aligned simulator analysis is specified around hard-cap budgets; soft-budget-only use should be labeled separately."
        )
    if len(experiment.budgets) < 2:
        report.warnings.append("Budget sweep is narrow; H1 is hard to evaluate without at least two budget levels.")
    if "strong" not in experiment.compression_strengths:
        report.warnings.append(
            "Compression sweep does not include a strong level; H3 and H4 will be weakly identified."
        )
    if "long" not in experiment.lags:
        report.warnings.append("Lag sweep does not include a long condition; H4 will be weakly identified.")
    if not any(controller.controller_id in {"C4", "C5"} for controller in controllers):
        report.warnings.append("No reset-aware controller is present; H5 cannot be tested.")
    if model_config.provider not in {"mock", "gemini", "local_endpoint"}:
        report.errors.append(f"Unsupported model provider: {model_config.provider}")
    return report


def validate_real_task_design(
    experiment: RealTaskExperimentConfig,
    model_config: ModelConfig,
    controllers: list[ControllerConfig],
) -> GuardrailReport:
    report = GuardrailReport()
    report.checks.append("Single model config is used for the whole real-task comparison block.")
    if len(controllers) < 2:
        report.warnings.append(
            "Real-task comparison block has fewer than two controllers; this is acceptable for smoke tests but not for controller-law comparison."
        )
    if experiment.mock_mode:
        report.warnings.append(
            "Layer B is running in mock mode. This is valid for pipeline checks but should not be presented as real-task evidence."
        )
    if experiment.max_turns < 4:
        report.warnings.append("Max turns is very small; delayed-verification effects may be muted.")
    if model_config.provider == "mock":
        report.warnings.append(
            "Mock backbone is useful for pipeline checks only. Claims about external validity should use Gemini or the local CPU model."
        )
    return report


def write_run_manifest(
    *,
    output_dir: Path,
    layer: str,
    experiment: SimulatorExperimentConfig | RealTaskExperimentConfig,
    model_config: ModelConfig,
    controllers: list[ControllerConfig],
    report: GuardrailReport,
) -> Path:
    payload: dict[str, Any] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "code_revision": get_code_revision(),
        "layer": layer,
        "experiment": experiment.model_dump(mode="json", by_alias=True),
        "backbone_model_id": model_config.model_id,
        "model_config": model_config.model_dump(mode="json"),
        "controller_ids": [controller.controller_id for controller in controllers],
        "theory_hypotheses": THEORY_HYPOTHESES,
        "scientific_rules": {
            "fixed_backbone_within_block": True,
            "exact_vs_proxy_separation": True,
            "negative_results_preserved": True,
            "scope_honesty_required": True,
        },
        "guardrail_report": asdict(report),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "run_manifest.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path
