"""Gemini adapter using the official Google Gen AI SDK."""

from __future__ import annotations

import json
import os
from typing import Any

from core.config import ModelConfig
from core.exceptions import ConfigError
from core.prompts import load_prompt_text
from core.schema_utils import load_schema
from core.structured_models import (
    CompressionResult,
    ContinueBranchResetDecision,
    FailureAttribution,
    StepDecision,
)
from models.base import ModelAdapter


class GeminiAdapter(ModelAdapter):
    """Adapter for Gemini structured JSON generation."""

    def __init__(self, config: ModelConfig) -> None:
        super().__init__(config)
        api_key_env = config.api_key_env or "GEMINI_API_KEY"
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise ConfigError(f"Missing Gemini API key in environment variable {api_key_env}")
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ConfigError("google-genai is required for Gemini runs.") from exc
        self._genai = genai
        self._types = types
        self._client = genai.Client(api_key=api_key)

    def _invoke(self, prompt: str, schema_name: str) -> str:
        schema = load_schema(schema_name)
        response = self._client.models.generate_content(
            model=self.config.model_id,
            contents=prompt,
            config=self._types.GenerateContentConfig(
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_output_tokens=self.config.max_output_tokens,
                response_mime_type="application/json",
                response_json_schema=schema,
            ),
        )
        text = getattr(response, "text", None)
        if not text:
            raise ValueError("Gemini response did not contain text output.")
        return text

    def _render_prompt(self, prompt_name: str, context: dict[str, Any]) -> str:
        template = load_prompt_text(prompt_name, self.config.prompt_version)
        return template.format(context_json=json.dumps(context, sort_keys=True))

    def plan_step(self, context: dict[str, Any]) -> StepDecision:
        return self._with_retry(
            "step_decision",
            self._render_prompt("step_decision", context),
            StepDecision,
        )

    def compress_state(self, context: dict[str, Any]) -> CompressionResult:
        return self._with_retry(
            "compression_result",
            self._render_prompt("compression_result", context),
            CompressionResult,
        )

    def diagnose_failure(self, trace: dict[str, Any]) -> FailureAttribution:
        return self._with_retry(
            "failure_attribution",
            self._render_prompt("failure_attribution", trace),
            FailureAttribution,
        )

    def choose_continue_branch_reset(
        self, context: dict[str, Any]
    ) -> ContinueBranchResetDecision:
        return self._with_retry(
            "continue_branch_reset",
            self._render_prompt("continue_branch_reset", context),
            ContinueBranchResetDecision,
        )

