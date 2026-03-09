from cache.summary import summarize_failures


def test_summarize_failures_keeps_distinct_modes() -> None:
    result = summarize_failures(
        [
            {"failure_mode": "timeout"},
            {"failure_mode": "alias"},
            {"failure_mode": "timeout"},
        ]
    )
    assert result == {"timeout": 2, "alias": 1}
