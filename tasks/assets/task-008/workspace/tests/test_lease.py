from workers.lease import select_worker_state


def test_reset_state_selects_fresh_worker() -> None:
    assert select_worker_state({"mode": "legacy", "needs_reset": "yes"}) == "fresh"
