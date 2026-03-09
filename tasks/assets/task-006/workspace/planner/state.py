"""Planner state transitions for the bundled Layer B micro-task."""


def choose_plan(has_fresh_plan: bool, legacy_plan_available: bool) -> str:
    if has_fresh_plan:
        return "reset-and-replan"
    if legacy_plan_available:
        return "continue-legacy"
    return "bootstrap-plan"
