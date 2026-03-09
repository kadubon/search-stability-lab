"""Parser selection logic for the bundled Layer B micro-task."""


def select_parser(config: dict[str, str]) -> str:
    explicit = config.get("parser")
    if explicit:
        return explicit
    fallback = config.get("fallback_parser")
    if fallback:
        return fallback
    return "default-parser"
