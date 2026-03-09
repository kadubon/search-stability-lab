from digest.router import route_digest


def test_route_digest_keeps_timeout_and_parser_separate() -> None:
    assert route_digest([{"kind": "timeout"}, {"kind": "parser"}]) == ["timeout", "parser"]
