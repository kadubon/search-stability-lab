from src.parser import select_parser


def test_select_parser_uses_default_when_keys_are_absent() -> None:
    assert select_parser({}) == "default-parser"


def test_select_parser_prefers_explicit_parser() -> None:
    assert select_parser({"parser": "fast"}) == "fast"
