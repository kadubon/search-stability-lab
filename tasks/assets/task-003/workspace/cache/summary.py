"""Summary cache logic for the bundled Layer B micro-task."""


def summarize_failures(events: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        label = event["failure_mode"]
        counts[label] = counts.get(label, 0) + 1
    return counts
