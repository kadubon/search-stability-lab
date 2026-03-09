# Bundled Layer B Assets

This directory contains frozen, public-safe micro-task slices for Layer B non-mock runs.

Scope notes:

- these are bundled micro-repositories, not SWE-Bench assets
- they are intended to exercise the harness in a reproducible, inspectable way
- they support proxy-based Layer B evaluation only

Each task bundle includes:

- `README.md`
- `metadata.yaml`
- `workspace/`
- `evaluation/`

Current bundled tasks:

- `task-001` parser fallback preservation
- `task-002` auth refresh preservation
- `task-003` summary-cache collision avoidance
- `task-004` checkpoint resume recovery
- `task-005` serializer default preservation
- `task-006` planner reset recovery
- `task-007` digest-routing compression probe
- `task-008` worker-reset recovery probe

Probe suites:

- substitution: `task-001`, `task-005`
- compression: `task-003`, `task-007`
- reset: `task-002`, `task-004`, `task-006`, `task-008`
