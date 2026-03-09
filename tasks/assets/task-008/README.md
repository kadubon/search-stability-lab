# Task 008: Worker Reset Probe

This bundled micro-task models a worker lease that keeps replaying stale state until the controller effectively resets to a fresh branch.

Target files:

- `workers/lease.py`
- `tests/test_lease.py`

Resolution criterion:

- `pytest -q tests/test_lease.py`

Proxy validity note:

- useful for reset-helpfulness, stale-continuation, and post-reset-resolution-improvement proxies
- not a claim about benchmark-scale agent reset performance
