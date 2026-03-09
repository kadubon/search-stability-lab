# Task 007: Digest Routing Compression Probe

This bundled micro-task models a digest router that incorrectly merges timeout and parser failures into one summary label.

Target files:

- `digest/router.py`
- `tests/test_router.py`

Resolution criterion:

- `pytest -q tests/test_router.py`

Proxy validity note:

- useful for compression-collision and represented-family-count proxies
- not a claim about broad summarization quality outside this mechanistic probe

Expected outcome-level sensitivity:

- success now requires preserving two active digest-routing branches until a delayed verification point
- compression-heavy control can keep the family visible while still losing the needed route distinction
