# Repository Map

## Where to start

1. `README.md`
2. `result_summary.md`
3. `docs/CURRENT_STATUS.md`
4. `docs/SCIENTIFIC_SCOPE.md`

## Core directories

- `simulator/`
  Layer A generator and engine. This is where simulator-exact quantities are defined.
- `controllers/`
  Controller laws `C0` through `C6`.
- `models/`
  Gemini, local endpoint, and mock adapters.
- `tasks/`
  Layer B harness, proxy rules, bundled task assets, and task manifests.
- `analysis/`
  Aggregation, statistics, figure generation, and conservative summary helpers.
- `scripts/`
  Runnable entry points and repo audit helpers.
- `configs/`
  Frozen model, controller, and experiment YAML files.
- `docs/`
  Scope, interpretation, audit, and reproducibility notes.
- `artifacts/`
  Saved run outputs and analyzed result directories.

## Exact vs proxy locations

- exact (simulator): `simulator/`, Layer A configs, Layer A artifacts, `failure_channel_true`, `adequate_family_ids_true`
- proxy (task harness): `tasks/`, Layer B configs, Layer B artifacts, `failure_channel_proxy`, `avoidable_retirement_proxy`

## Logs and results

- raw events: `artifacts/**/events.jsonl`
- analyzed tables: `artifacts/**/analysis/*.csv`
- top-level summaries: `result_summary.md`, `docs/CURRENT_STATUS.md`

## Smoke-test entry points

- simulator smoke: `python scripts/run_simulator.py --config configs/experiments/pilot.yaml --max-conditions 1 --max-episodes 1 --controllers C0`
- local mock e2e: `python scripts/run_real_tasks.py --config configs/experiments/real_tasks.yaml --max-tasks 1 --controllers C0`
- status generation: `python scripts/generate_status_summary.py`

## Audit helpers

- task asset validation: `python scripts/validate_task_assets.py --manifest tasks/manifests/frozen_task_slice_v2.yaml`
- public safety scan: `python scripts/check_public_safety.py`
