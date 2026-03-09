"""Aggregate JSONL logs into analysis-ready tables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from core.structured_models import EventRecord
from analysis.stats import wilson_interval


def _structured_output_invalidity_type(value: Any) -> str | None:
    if pd.isna(value) or value == "":
        return None
    text = str(value).lower()
    if "not valid json" in text:
        return "invalid_json"
    if "timeout" in text:
        return "timeout"
    if "schema" in text:
        return "schema_validation"
    if "bounded repair" in text:
        return "invalid_json"
    if "invocation failed" in text:
        return "backend_error"
    return "other_invalid_structure"


def load_events(jsonl_paths: list[Path]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in jsonl_paths:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                payload = json.loads(line)
                event = EventRecord.model_validate(payload)
                row = event.model_dump(mode="json")
                metadata = row.pop("metadata", {}) or {}
                condition = metadata.pop("condition", None)
                if isinstance(condition, dict):
                    for key, value in condition.items():
                        row[key] = value
                for key, value in metadata.items():
                    row[key] = value
                rows.append(row)
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def final_outcomes(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return events
    finals = events[events["event_type"].isin(["episode_end", "task_end"])].copy()
    finals = finals[finals["success_final"].notna()].copy()
    finals["success_final"] = finals["success_final"].astype(bool)
    finals["group_id"] = finals.apply(
        lambda row: str(row["seed"]) if row["layer"] == "layer_a" else str(row["task_id"]),
        axis=1,
    )
    if "last_model_error" in finals.columns:
        finals["structured_output_invalidity"] = finals["last_model_error"].fillna("").astype(str).str.len() > 0
        finals["structured_output_invalidity_type"] = finals["last_model_error"].apply(
            _structured_output_invalidity_type
        )
    if "structured_output_unrecoverable_call_count" in finals.columns:
        finals["structured_output_invalidity"] = finals["structured_output_unrecoverable_call_count"].fillna(0).astype(float) > 0
    if "structured_output_failure_kind" in finals.columns:
        finals["structured_output_invalidity_type"] = finals["structured_output_failure_kind"].where(
            finals["structured_output_failure_kind"].notna(),
            finals.get("structured_output_invalidity_type"),
        )
    if "structured_output_repaired_call_count" in finals.columns:
        finals["structured_output_repaired"] = finals["structured_output_repaired_call_count"].fillna(0).astype(float) > 0
    return finals


def build_summary_tables(finals: pd.DataFrame) -> pd.DataFrame:
    if finals.empty:
        return pd.DataFrame()
    group_columns = [
        column
        for column in [
            "layer",
            "backbone_model_id",
            "controller_id",
            "budget_level",
            "lag_level",
            "compression_level",
            "contamination_level",
            "reset_cost_level",
        ]
        if column in finals.columns
    ]
    grouped = finals.groupby(group_columns, dropna=False)
    rows: list[dict[str, Any]] = []
    for keys, frame in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = {group_columns[index]: keys[index] for index in range(len(group_columns))}
        successes = int(frame["success_final"].sum())
        total = int(len(frame))
        lower, upper = wilson_interval(successes, total)
        row.update(
            {
                "sample_count": total,
                "success_rate": successes / total if total else 0.0,
                "wilson_lower": lower,
                "wilson_upper": upper,
                "compute_cost_summary": float(frame["budget_used"].mean()) if "budget_used" in frame else 0.0,
                "measurement_scope": "exact (simulator)" if row.get("layer") == "layer_a" else "proxy (task harness)",
            }
        )
        if "structured_output_invalidity" in frame.columns:
            row["structured_output_invalidity_rate"] = float(frame["structured_output_invalidity"].mean())
        if "structured_output_repaired" in frame.columns:
            row["structured_output_repaired_rate"] = float(frame["structured_output_repaired"].mean())
        rows.append(row)
    return pd.DataFrame(rows)
