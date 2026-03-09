"""Unified model adapter interface."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from core.config import ModelConfig
from core.exceptions import RetryExhaustedError, StructuredOutputError
from core.schema_utils import validate_payload
from core.structured_models import (
    CompressionResult,
    ContinueBranchResetDecision,
    FailureAttribution,
    StepDecision,
)

T = TypeVar("T", bound=BaseModel)


class ModelAdapter(ABC):
    """Common interface for Gemini, local endpoint, and mock backbones."""

    def __init__(self, config: ModelConfig) -> None:
        self.config = config
        self._last_call_metadata: dict[str, Any] | None = None

    @property
    def model_id(self) -> str:
        return self.config.model_id

    def _set_last_call_metadata(self, metadata: dict[str, Any] | None) -> None:
        self._last_call_metadata = metadata

    def consume_last_call_metadata(self) -> dict[str, Any] | None:
        metadata = self._last_call_metadata
        self._last_call_metadata = None
        return metadata

    def _parse_and_validate(self, schema_name: str, raw_text: str, model_type: type[T]) -> T:
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise StructuredOutputError("Model output was not valid JSON") from exc
        if not isinstance(payload, dict):
            raise StructuredOutputError("Structured output must decode to a JSON object")
        validate_payload(schema_name, payload)
        return model_type.model_validate(payload)

    def _with_retry(self, schema_name: str, prompt: str, model_type: type[T]) -> T:
        last_error: Exception | None = None
        self._set_last_call_metadata(None)
        for _ in range(self.config.retry_policy.max_retries + 1):
            try:
                raw_text = self._invoke(prompt=prompt, schema_name=schema_name)
                model = self._parse_and_validate(schema_name, raw_text, model_type)
                if self._last_call_metadata is None:
                    self._set_last_call_metadata({"status": "valid", "schema_name": schema_name, "repair_actions": []})
                return model
            except StructuredOutputError as exc:
                last_error = exc
                if self._last_call_metadata is None:
                    self._set_last_call_metadata(
                        {
                            "status": "unrecoverable",
                            "schema_name": schema_name,
                            "repair_actions": [],
                            "failure_kind": "structured_output_error",
                            "error": str(exc),
                        }
                    )
            except Exception as exc:  # pragma: no cover - backend-specific exceptions vary
                last_error = StructuredOutputError(
                    f"Model invocation failed for {schema_name}: {type(exc).__name__}: {exc}"
                )
                self._set_last_call_metadata(
                    {
                        "status": "unrecoverable",
                        "schema_name": schema_name,
                        "repair_actions": [],
                        "failure_kind": "backend_error",
                        "error": str(last_error),
                    }
                )
        raise RetryExhaustedError(
            f"Structured output retries exhausted for {schema_name}: {last_error}"
        ) from last_error

    @abstractmethod
    def _invoke(self, prompt: str, schema_name: str) -> str:
        """Invoke the backend and return a raw JSON string."""

    @abstractmethod
    def plan_step(self, context: dict[str, Any]) -> StepDecision:
        """Produce a structured step decision."""

    @abstractmethod
    def compress_state(self, context: dict[str, Any]) -> CompressionResult:
        """Produce a structured compression result."""

    @abstractmethod
    def diagnose_failure(self, trace: dict[str, Any]) -> FailureAttribution:
        """Produce a structured failure attribution."""

    @abstractmethod
    def choose_continue_branch_reset(
        self, context: dict[str, Any]
    ) -> ContinueBranchResetDecision:
        """Produce a continue/branch/reset decision."""
