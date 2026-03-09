# Task 003: Summary Cache Collision

This bundled micro-task models a summary cache that collapses distinct failure modes into one label.

Target files:

- `cache/summary.py`
- `tests/test_summary.py`

Resolution criterion:

- `pytest -q tests/test_summary.py`

Expected outcome-level sensitivity:

- success now depends on preserving two active resolving routes until delayed verification
- repeated compression can erase that distinction even when a proxy family is still visible
