from planner.state import choose_plan


def test_choose_plan_prefers_fresh_replan() -> None:
    assert choose_plan(has_fresh_plan=True, legacy_plan_available=True) == "reset-and-replan"
