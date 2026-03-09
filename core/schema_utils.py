"""Runtime JSON schema loading and validation helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from core.exceptions import StructuredOutputError


SCHEMA_DIR = Path("schemas")


def load_schema(schema_name: str) -> dict[str, Any]:
    path = SCHEMA_DIR / f"{schema_name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(schema_name: str, payload: dict[str, Any]) -> None:
    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda item: item.path)
    if errors:
        detail = "; ".join(error.message for error in errors[:3])
        raise StructuredOutputError(
            f"Payload failed schema validation for {schema_name}: {detail}"
        )

