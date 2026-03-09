"""Session state transitions for the bundled Layer B micro-task."""


def next_action(token_valid: bool, refresh_available: bool) -> str:
    if token_valid:
        return "continue"
    if refresh_available:
        return "refresh"
    return "reauth"
