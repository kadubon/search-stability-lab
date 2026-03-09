# Result Summary

## Purpose

This file is the top-level place to understand:

- what this repository is designed to test
- what has been validated about the repository itself
- what outputs to inspect after a run
- what may and may not be claimed from those outputs

It is intentionally not a place to hardcode empirical claims from unpublished runs.

## Theory-backed experiment object

The repository implements experiments around the theory in:

Takahashi, K. (2026). *Search Stability under Finite Context: A Minimal Theory of Adequacy Preservation, Compression, and Reset in Long-Running Agents*. Zenodo. https://doi.org/10.5281/zenodo.18905242

The key object is not generic "agent quality." It is finite-context search stability under delayed verification, where:

- several partially plausible route families may coexist
- active context is limited
- compression may destroy action-relevant distinctions
- reset may be rational under stale legacy contamination

## What this repository can show

Layer A can show exact simulator evidence for:

- adequate-family survival at verification
- recoverable-family count at verification
- compression alias failures
- avoidable retirement
- stale-legacy continuation
- mixed versus raw-model failure attribution

Layer B can show proxy-based or task-level evidence for:

- whether controller-law effects remain directionally visible
- whether family-like branch structure can be tracked consistently
- whether reset, compression, and retirement proxies are auditable

## What this repository cannot show

- universal proof of the theory
- exact latent-family truth on real tasks
- benchmark leaderboard claims from the shipped mock setup
- scientific support from smoke tests alone

## Repository verification status

The repository itself has been checked to support:

- local CPU model integration through Ollama-style HTTP
- Gemini API integration through environment-variable credentials
- Layer A end-to-end simulator runs
- Layer B end-to-end mock-safe harness runs
- analysis pipeline execution from actual logs
- scientific design checks before runs
- offline test coverage for configs, schemas, simulator, harness, and malformed structured output handling

Current repository self-checks:

- `pytest -q` passes
- `scripts/check_experiment_design.py` validates both Layer A and Layer B configs

These are repository readiness checks, not theory-result claims.

## Latest exact Layer A suite

The completed post-redesign Layer A suite is summarized in:

- `docs/LAYER_A_SUITE_REPORT_2026-03-09.md`
- `artifacts/layer_a_suite_2026-03-09/manifest.json`

That report is the correct place to inspect actual simulator findings for H1-H5. It separates:

- supported findings
- partial or directional findings
- results that remain unestablished

## Current release status

The current release-level report is:

- `docs/FINAL_RELEASE_REPORT_2026-03-09.md`
- `docs/CURRENT_STATUS.md`
- `docs/SCIENTIFIC_SCOPE.md`
- `docs/RESULTS_INTERPRETATION.md`
- `docs/LAYER_B_PROBE_REPORT_2026-03-09.md`

In plain terms:

- Layer A exact suite: completed
- Layer B mock runs on Gemini and local CPU: completed
- Layer B non-mock expanded bundled task slice runs on Gemini and local CPU: completed
- Layer B probe-specific substitution/compression/reset configs: added and ready to run

This means the repository is experiment-ready and publicly safe. Broader external-validity evaluation is still pending a benchmark-scale frozen task slice, but the shipped expanded bundled non-mock slice now runs end-to-end.

## Completed run set (2026-03-09)

### Layer A exact suite

- backbone: `gemini-2.5-flash-lite`
- report: `docs/LAYER_A_SUITE_REPORT_2026-03-09.md`
- safe summary:
  - H1: partial support
  - H2: support against the naive baseline
  - H3: support
  - H4: partial support
  - H5: directional support

### Layer B mock runs

- Gemini mock run:
  - `artifacts/real_tasks_gemini/real-gemini-20260308T235203Z-feb0a45f`
  - `3/3` resolved for `C0`, `C3`, `C5`
- local CPU mock run:
  - `artifacts/real_tasks_local_cpu/real-local-20260308T235201Z-29d11f9c`
  - `3/3` resolved for `C0`, `C3`, `C5`

Interpretation:

- these runs validate adapters, logging, proxy instrumentation, and analysis on both backbones
- because they use the shipped mock task slice, they are not evidence about real-world task validity

### Layer B non-mock expanded slice

- report: `docs/LAYER_B_NONMOCK_REPORT_2026-03-09.md`
- suite manifest: `artifacts/layer_b_nonmock_expanded_suite_2026-03-09/manifest.json`
- task count: `6`

Gemini bundled non-mock block:

- backbone: `gemini-2.5-flash-lite`
- `C0`: `0/6`
- `C3`: `3/6`
- `C5`: `2/6`

local CPU bundled non-mock block:

- backbone: `gemma3:1b`
- `C0`: `0/6`
- `C3`: `3/6`
- `C5`: `0/6`

Interpretation:

- these are Layer B task-outcome and proxy results on bundled public-safe micro-tasks
- they are stronger than mock-mode evidence, but they are still not benchmark evidence
- the most stable directional pattern is that `C3` outperformed `C0` on both backbones
- `C5` remained mixed on Gemini and non-supportive on the local CPU block, so Layer B does not show reset dominance on this bundled slice
- the local CPU block logged repeated malformed structured output from the model, so its results must be read with that caveat

If you only want the shortest honest read:

- Layer A exact evidence is strongest for the theory
- Layer B expanded task evidence supports `C3 > C0`
- Layer B reset probe evidence is directional in favor of `C4` and `C5` over `C0` on the authored reset suite
- Layer B compression probe evidence is now limited but outcome-sensitive for `C5` over `C0/C1` on the authored compression suite
- Layer B still does not support `C5` dominance as a general story

## Recommended first runs

1. Validate the design:
   `python scripts/check_experiment_design.py --layer layer_a --config configs/experiments/pilot_gemini.yaml`
   `python scripts/check_experiment_design.py --layer layer_b --config configs/experiments/real_tasks_gemini.yaml`
2. Run one Layer A smoke test:
   `python scripts/run_simulator.py --config configs/experiments/pilot_gemini.yaml --max-conditions 1 --max-episodes 1 --controllers C0`
3. Run one Layer B smoke test:
   `python scripts/run_real_tasks.py --config configs/experiments/real_tasks_gemini.yaml --max-tasks 1 --controllers C0`
4. Analyze:
   `python scripts/analyze_results.py --input-dir artifacts --output-dir artifacts/analysis`

## Where to inspect outputs

For each run directory, inspect:

- `events.jsonl`: full trajectory log
- `outcomes.csv` or `task_results.csv`: per-episode or per-task summary
- `run_manifest.json`: resolved config, backbone, controllers, hypotheses, and design guardrails

For analyzed runs, inspect:

- `summary_tables.csv`
- `pairwise_contrasts.csv`
- `regression_summary.txt`
- `figure_1_success_vs_budget.png`
- `figure_2_success_vs_compression_and_lag.png`
- `figure_3_reset_benefit.png`
- `figure_4_failure_channel_composition.png`

## Interpretation rules

- Make exact mechanism claims only from Layer A exact fields.
- Make proxy-limited claims from Layer B and label them as proxy or task outcome.
- Hold backbone fixed when comparing controller laws.
- Preserve negative and null findings.
- Use "support", "non-support", or "directional evidence", not "proof".

## Final checks for this release

- `pytest -q`: `18 passed`
- design checks:
  - Layer A and Layer B experiment configs returned `OK`
  - warnings were preserved where configs intentionally use mock mode or hypothesis-specific sweeps
- public-safety scans:
  - no local absolute paths in source or docs after excluding ignored caches
  - no obvious live secret patterns in repository files after excluding local `.env` files

## What is still required from the user

- optionally, a larger or more benchmark-like frozen non-mock task slice if you want stronger Layer B evidence beyond the shipped bundled task set
- optionally, a Git checkout if you want `code_revision` to record a commit hash instead of `unknown`
