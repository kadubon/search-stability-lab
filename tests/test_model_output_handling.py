from __future__ import annotations

import pytest

from core.config import ModelConfig
from core.exceptions import RetryExhaustedError, StructuredOutputError
from core.structured_models import (
    CompressionResult,
    ContinueBranchResetDecision,
    FailureAttribution,
    StepDecision,
)
from models.base import ModelAdapter
from models.local_endpoint_adapter import LocalEndpointAdapter


class BrokenAdapter(ModelAdapter):
    def _invoke(self, prompt: str, schema_name: str) -> str:
        return "{not-json"

    def plan_step(self, context: dict[str, object]) -> StepDecision:
        return self._with_retry("step_decision", "broken", StepDecision)

    def compress_state(self, context: dict[str, object]) -> CompressionResult:
        return self._with_retry("compression_result", "broken", CompressionResult)

    def diagnose_failure(self, trace: dict[str, object]) -> FailureAttribution:
        return self._with_retry("failure_attribution", "broken", FailureAttribution)

    def choose_continue_branch_reset(
        self, context: dict[str, object]
    ) -> ContinueBranchResetDecision:
        return self._with_retry("continue_branch_reset", "broken", ContinueBranchResetDecision)


def test_malformed_model_output_raises_bounded_retry_error() -> None:
    adapter = BrokenAdapter(
        ModelConfig(
            model_id="broken",
            provider="mock",
            endpoint_family="offline",
        )
    )
    with pytest.raises(RetryExhaustedError):
        adapter.plan_step({})


def test_local_adapter_repairs_fenced_json_output() -> None:
    adapter = LocalEndpointAdapter(
        ModelConfig(
            model_id="gemma3:1b",
            provider="local_endpoint",
            endpoint_family="local_cpu_endpoint",
            api_base="http://127.0.0.1:11434",
            local_api_style="ollama",
        )
    )
    payload = """```json
{"step_id":"s1","decision_type":"keep","target_ids":[],"family_ids":["fam"],"confidence":0.6,"rationale_short":"keep the active family","predicted_risk":{"adequacy_loss":0.2,"alias_risk":0.1,"staleness_risk":0.1},"estimated_budget_after":1.0}
```"""
    result = adapter._parse_and_validate("step_decision", payload, StepDecision)
    metadata = adapter.consume_last_call_metadata()
    assert result.step_id == "s1"
    assert metadata is not None
    assert metadata["status"] == "repaired"
    assert "strip_fenced_json" in metadata["repair_actions"][0]


def test_local_adapter_marks_unrecoverable_invalid_structure() -> None:
    adapter = LocalEndpointAdapter(
        ModelConfig(
            model_id="gemma3:1b",
            provider="local_endpoint",
            endpoint_family="local_cpu_endpoint",
            api_base="http://127.0.0.1:11434",
            local_api_style="ollama",
        )
    )
    with pytest.raises(StructuredOutputError):
        adapter._parse_and_validate("step_decision", "plain text without json", StepDecision)
    metadata = adapter.consume_last_call_metadata()
    assert metadata is not None
    assert metadata["status"] == "unrecoverable"


def test_local_adapter_repairs_mixed_text_with_trailing_comma() -> None:
    adapter = LocalEndpointAdapter(
        ModelConfig(
            model_id="gemma3:1b",
            provider="local_endpoint",
            endpoint_family="local_cpu_endpoint",
            api_base="http://127.0.0.1:11434",
            local_api_style="ollama",
        )
    )
    payload = (
        'answer follows {"step_id":"s2","decision_type":"keep","target_ids":[],"family_ids":["fam"],'
        '"confidence":0.7,"rationale_short":"preserve route","predicted_risk":{"adequacy_loss":0.2,'
        '"alias_risk":0.1,"staleness_risk":0.1,},"estimated_budget_after":1.0,} trailing text'
    )
    result = adapter._parse_and_validate("step_decision", payload, StepDecision)
    metadata = adapter.consume_last_call_metadata()
    assert result.step_id == "s2"
    assert metadata is not None
    assert metadata["status"] == "repaired"
    assert metadata["repair_actions"]
