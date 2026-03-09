"""Digest routing logic for the bundled Layer B compression probe."""


def route_digest(events: list[dict[str, str]]) -> list[str]:
    labels: list[str] = []
    for event in events:
        kind = event["kind"]
        if kind == "timeout":
            labels.append("timeout")
        elif kind == "parser":
            labels.append("parser")
        else:
            labels.append(kind)
    return labels
