# Final Release Report (2026-03-09)

## Release scope

This report records the final experiment status of the public-safe repository as of 2026-03-09.

It distinguishes:

- completed exact simulator evidence
- completed mock-only harness evidence
- completed bundled non-mock evaluation
- final security and reproducibility checks

## Completed experiments

### Layer A exact suite

Status: completed.

- fixed backbone: `gemini-2.5-flash-lite`
- suite manifest: `artifacts/layer_a_suite_2026-03-09/manifest.json`
- detailed report: `docs/LAYER_A_SUITE_REPORT_2026-03-09.md`

Safe summary:

- H1: partial support
- H2: support against the naive baseline
- H3: support
- H4: partial support
- H5: directional support

These claims are exact Layer A claims only.

### Layer B mock harness

Status: completed as instrumentation validation, not as real-task evidence.

Run directories:

- Gemini mock run: `artifacts/real_tasks_gemini/real-gemini-20260308T235203Z-feb0a45f`
- local CPU mock run: `artifacts/real_tasks_local_cpu/real-local-20260308T235201Z-29d11f9c`

Observed task outcomes:

- Gemini mock: `3/3` resolved for each of `C0`, `C3`, `C5`
- local CPU mock: `3/3` resolved for each of `C0`, `C3`, `C5`

Interpretation:

- the Layer B harness, adapters, logging, and analysis pipeline run end-to-end on both backbones
- these are mock tasks with deterministic proxy behavior, so they should not be interpreted as external-validity evidence
- regression warnings appeared during analysis because the sample is tiny and outcomes are perfectly separated; this is expected and not hidden

### Layer B non-mock expanded frozen manifest

Status: completed on the expanded bundled frozen micro-task slice.

Configs:

- `configs/experiments/real_tasks_gemini_nonmock_frozen.yaml`
- `configs/experiments/real_tasks_local_cpu_nonmock_frozen.yaml`
- `configs/experiments/real_tasks_gemini_nonmock_expanded.yaml`
- `configs/experiments/real_tasks_local_cpu_nonmock_expanded.yaml`

Detailed report:

- `docs/LAYER_B_NONMOCK_REPORT_2026-03-09.md`

Interpretation:

- the repository now ships an expanded bundled public-safe frozen micro-task slice under `tasks/assets/`
- non-mock Layer B task-outcome runs completed on both backbones for the six-task slice
- these runs are still micro-task evidence, not benchmark evidence

## Final checks

### Reproducibility

- `pytest -q`: `18 passed`
- `python scripts/validate_task_assets.py --manifest tasks/manifests/frozen_task_slice_v2.yaml`: `OK` for all six bundled tasks
- suite summary regeneration command:

```bash
python scripts/summarize_layer_a_suite.py --manifest artifacts/layer_a_suite_2026-03-09/manifest.json --output-dir artifacts/layer_a_suite_2026-03-09
```

- all analyzed runs have `events.jsonl`, `final_outcomes.csv` or `task_results.csv`, and `run_manifest.json`
- `code_revision` remains `unknown` because the workspace is not a Git checkout

### Guardrails

`scripts/check_experiment_design.py` returned `OK` for:

- `configs/experiments/layer_a_h1_budget_threshold_gemini.yaml`
- `configs/experiments/layer_a_h2_substitution_gemini.yaml`
- `configs/experiments/layer_a_h3_h4_compression_gemini.yaml`
- `configs/experiments/layer_a_h5_reset_gemini.yaml`
- `configs/experiments/real_tasks_gemini.yaml`
- `configs/experiments/real_tasks_local_cpu.yaml`
- `configs/experiments/real_tasks_gemini_nonmock_frozen.yaml`
- `configs/experiments/real_tasks_gemini_nonmock_expanded.yaml`
- `configs/experiments/real_tasks_local_cpu_nonmock_expanded.yaml`

Warnings were preserved rather than suppressed:

- Layer B mock configs are valid for pipeline checks but not for real-task evidence
- some hypothesis-focused configs intentionally emphasize only the dimensions needed for that hypothesis and therefore warn about omitted sweeps

### Public-repo safety

- no local absolute paths were found in source or documentation after excluding `.env` and ignored bytecode caches
- no obvious live secret patterns were found in repository files after excluding local `.env` files
- `.gitignore` excludes `.env`, `tasks/assets/local/`, `artifacts/`, and Python caches

## Final scientific status

This repository is final and release-ready in the following sense:

- the exact Layer A mechanism suite is complete and documented
- the Layer B harness is complete in mock mode on both supported backbones
- the bundled non-mock Layer B slice is complete on both supported backbones

This repository is not final in the sense of having completed broad external-validity evaluation. That would require a larger or more benchmark-like frozen task slice beyond the shipped bundled micro-task assets.
