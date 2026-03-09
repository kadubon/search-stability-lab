"""Local endpoint adapter for CPU-runnable models via Ollama or OpenAI-compatible APIs."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

from core.config import ModelConfig
from core.exceptions import ConfigError, StructuredOutputError
from core.prompts import load_prompt_text
from core.schema_utils import load_schema
from core.structured_models import (
    CompressionResult,
    ContinueBranchResetDecision,
    FailureAttribution,
    StepDecision,
)
from models.base import ModelAdapter


class LocalEndpointAdapter(ModelAdapter):
    """HTTP adapter for a local CPU model server."""

    def __init__(self, config: ModelConfig) -> None:
        super().__init__(config)
        if not config.api_base:
            raise ConfigError("Local endpoint adapter requires api_base in the model config.")

    def _invoke(self, prompt: str, schema_name: str) -> str:
        if self.config.local_api_style == "openai_compatible":
            return self._invoke_openai_compatible(prompt, schema_name)
        return self._invoke_ollama(prompt, schema_name)

    def _invoke_ollama(self, prompt: str, schema_name: str) -> str:
        schema = load_schema(schema_name)
        body = {
            "model": self.config.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "format": schema,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_output_tokens,
            },
        }
        return self._post_json(f"{self.config.api_base}/api/chat", body, response_key=("message", "content"))

    def _invoke_openai_compatible(self, prompt: str, schema_name: str) -> str:
        schema = load_schema(schema_name)
        body = {
            "model": self.config.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_output_tokens,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": schema_name, "schema": schema},
            },
        }
        return self._post_json(
            f"{self.config.api_base}/v1/chat/completions",
            body,
            response_key=("choices", 0, "message", "content"),
        )

    def _post_json(self, url: str, body: dict[str, Any], response_key: tuple[Any, ...]) -> str:
        request = urllib.request.Request(
            url=url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.retry_policy.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise StructuredOutputError(f"Local endpoint request failed: {exc}") from exc
        node: Any = payload
        for key in response_key:
            node = node[key]
        if not isinstance(node, str):
            raise StructuredOutputError("Local endpoint did not return a JSON string payload.")
        return node

    def _render_prompt(self, prompt_name: str, context: dict[str, Any]) -> str:
        template = load_prompt_text(prompt_name, self.config.prompt_version)
        return template.format(context_json=json.dumps(context, sort_keys=True))

    def _extract_first_json_object(self, text: str) -> str | None:
        start = text.find("{")
        if start < 0:
            return None
        depth = 0
        in_string = False
        escaped = False
        for index, char in enumerate(text[start:], start=start):
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        return None

    def _candidate_repairs(self, raw_text: str) -> list[tuple[str, str]]:
        candidates: list[tuple[str, str]] = []
        stripped = raw_text.strip()
        fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
        if fenced:
            candidates.append(("strip_fenced_json", fenced.group(1).strip()))
        extracted = self._extract_first_json_object(raw_text)
        if extracted and extracted != raw_text:
            candidates.append(("extract_first_json_object", extracted.strip()))
        trailing = re.sub(r",(\s*[}\]])", r"\1", stripped)
        if trailing != stripped:
            candidates.append(("remove_trailing_commas", trailing))
        if stripped.startswith('"') and stripped.endswith('"'):
            try:
                unwrapped = json.loads(stripped)
            except json.JSONDecodeError:
                unwrapped = None
            if isinstance(unwrapped, str):
                candidates.append(("unwrap_stringified_json", unwrapped.strip()))
        chained: list[tuple[str, str]] = []
        for action, candidate in list(candidates):
            cleaned = re.sub(r",(\s*[}\]])", r"\1", candidate)
            if cleaned != candidate:
                chained.append((f"{action}+remove_trailing_commas", cleaned))
            extracted = self._extract_first_json_object(candidate)
            if extracted and extracted != candidate:
                chained.append((f"{action}+extract_first_json_object", extracted.strip()))
        seen: set[str] = set()
        deduped: list[tuple[str, str]] = []
        for action, candidate in [*candidates, *chained]:
            if candidate and candidate not in seen:
                seen.add(candidate)
                deduped.append((action, candidate))
        return deduped

    def _parse_and_validate(self, schema_name: str, raw_text: str, model_type: type[Any]) -> Any:
        attempts: list[dict[str, Any]] = []
        try:
            model = super()._parse_and_validate(schema_name, raw_text, model_type)
            self._set_last_call_metadata(
                {
                    "status": "valid",
                    "schema_name": schema_name,
                    "repair_actions": [],
                    "repair_attempts": attempts,
                }
            )
            return model
        except StructuredOutputError as original_exc:
            attempts.append({"action": "direct_parse", "outcome": "failed", "error": str(original_exc)})
            for action, candidate in self._candidate_repairs(raw_text):
                try:
                    model = super()._parse_and_validate(schema_name, candidate, model_type)
                    attempts.append({"action": action, "outcome": "applied"})
                    self._set_last_call_metadata(
                        {
                            "status": "repaired",
                            "schema_name": schema_name,
                            "repair_actions": [action],
                            "repair_attempts": attempts,
                        }
                    )
                    return model
                except StructuredOutputError as repair_exc:
                    attempts.append({"action": action, "outcome": "failed", "error": str(repair_exc)})
            failure_kind = "invalid_json"
            original_text = str(original_exc).lower()
            if "schema" in original_text or "must decode" in original_text:
                failure_kind = "schema_validation"
            self._set_last_call_metadata(
                {
                    "status": "unrecoverable",
                    "schema_name": schema_name,
                    "repair_actions": [],
                    "repair_attempts": attempts,
                    "failure_kind": failure_kind,
                }
            )
            raise StructuredOutputError(
                f"Local structured output remained invalid after bounded repair for {schema_name}"
            ) from original_exc

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
