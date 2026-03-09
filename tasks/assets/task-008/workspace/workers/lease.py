"""Worker lease logic for the bundled Layer B reset probe."""


def select_worker_state(state: dict[str, str]) -> str:
    if state.get("needs_reset") == "yes":
        return "fresh"
    return state.get("mode", "legacy")
