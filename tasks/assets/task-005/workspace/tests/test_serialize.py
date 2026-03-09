from serialize.config import choose_serializer


def test_choose_serializer_uses_default_serializer() -> None:
    assert choose_serializer({}) == "json"
