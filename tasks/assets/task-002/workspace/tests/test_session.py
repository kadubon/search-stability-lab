from auth.session import next_action


def test_next_action_uses_refresh_when_token_is_invalid() -> None:
    assert next_action(token_valid=False, refresh_available=True) == "refresh"


def test_next_action_reauths_without_refresh() -> None:
    assert next_action(token_valid=False, refresh_available=False) == "reauth"
