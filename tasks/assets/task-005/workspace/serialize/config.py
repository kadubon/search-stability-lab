"""Serializer configuration for the bundled Layer B micro-task."""


def choose_serializer(config: dict[str, str]) -> str:
    explicit = config.get("serializer")
    if explicit:
        return explicit
    fallback = config.get("default_serializer")
    if fallback:
        return fallback
    return "json"
