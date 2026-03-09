"""Exact deterministic failure-channel attribution for Layer A."""

from __future__ import annotations

from simulator.types import EpisodeState


def classify_failure(state: EpisodeState) -> tuple[str, list[str]]:
    triggers: list[str] = []
    if state.alias_event_true:
        triggers.append("compression_alias")
    if state.avoidable_retirement_true:
        triggers.append("avoidable_retirement")
    if state.stale_legacy_triggered:
        triggers.append("stale_legacy_continuation")
    if state.missed_adequate_triggered:
        triggers.append("missed_adequate_family")
    if state.raw_model_triggered:
        triggers.append("raw_model_failure")
    structural = [
        item
        for item in triggers
        if item
        in {
            "compression_alias",
            "avoidable_retirement",
            "stale_legacy_continuation",
            "missed_adequate_family",
        }
    ]
    if len(structural) > 1:
        return "mixed_failure", triggers
    if triggers:
        return triggers[0], triggers
    return "raw_model_failure", ["raw_model_failure"]

