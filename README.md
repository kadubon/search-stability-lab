# Search Stability Lab

This repository implements a reproducible experiment codebase for studying search stability under finite context. It operationalizes the theory paper with two layers:

- Layer A: a controlled simulator with simulator-exact latent adequacy and exact failure-channel attribution.
- Layer B: a lightweight task harness with deterministic family proxies and bundled mechanistic probe tasks.

The repository is designed for scientific use. It tests scoped hypotheses about controller laws under finite-context constraints. It does not prove the theory universally, does not bundle copyrighted benchmark assets, and does not fabricate empirical results. The strongest current cross-layer result is the substitution-first story (`C3 > C0`). Layer B now also shows directional reset-probe evidence against `C0`, plus limited outcome-sensitive compression evidence on a tiny authored suite, and some local CPU results remain confounded by malformed structured output.

## Theoretical basis

This repository is an implementation-oriented companion to the following preprint, which defines the theory and terminology used here:

Takahashi, K. (2026). *Search Stability under Finite Context: A Minimal Theory of Adequacy Preservation, Compression, and Reset in Long-Running Agents*. Zenodo. [https://doi.org/10.5281/zenodo.18905242](https://doi.org/10.5281/zenodo.18905242)

For experiment design and interpretation, see `docs/THEORY_VALIDATION_GUIDE.md` and `docs/SCIENTIFIC_CHECKLIST.md`.
The final experiment-readiness audit is recorded in `docs/FINAL_AUDIT.md`.
The post-pilot redesign rationale is recorded in `docs/EXPERIMENT_REDESIGN.md`.
The current conservative status page is `docs/CURRENT_STATUS.md`.
The repository scientific scope note is `docs/SCIENTIFIC_SCOPE.md`.
The results interpretation note is `docs/RESULTS_INTERPRETATION.md`.
Layer B-specific scope and probe design notes are `docs/LAYER_B_STATUS.md`, `docs/LAYER_B_PROXY_MODEL.md`, and `docs/LAYER_B_PROBE_MATRIX.md`.
The completed Layer B probe-block report is `docs/LAYER_B_PROBE_REPORT_2026-03-09.md`.

## What this repo tests

- Whether controller-law changes affect adequate-family survival under finite active-context budgets.
- Whether substitution-first, reserve-aware, compression-cautious, and reset-aware policies differ under controlled conditions.
- Whether small real-task harnesses show directionally similar controller effects when only proxies are available.

## Who this repo is for

- AI engineers who need a lightweight, theory-aligned harness for long-running agent evaluation
- AI agents that need explicit rules for what may be claimed from simulator versus real-task evidence
- researchers who want a falsifiable, CPU-feasible layer before investing in larger benchmark runs

## Why this theory is useful

The repository is meant to make long-running agent failures more legible. Instead of treating every miss as generic model weakness, it helps test whether failure came from:

- loss of adequate-family reserve before verification
- harmful compression aliasing
- avoidable retirement of a still-useful route family
- stale-legacy continuation when reset would have been rational
- a mixture of ecological and raw-model failure

## What this repo does not test

- It is not a leaderboard implementation.
- It does not claim benchmark completeness for SWE-Bench Lite.
- It does not validate the theory outside the implemented simulator conditions and the chosen fixed task slice.

## Setup

Python 3.11+ is required.

```bash
python -m pip install -r requirements.txt
```

Environment variables:

- `GEMINI_API_KEY` for Gemini runs
- `LOCAL_LLM_ENDPOINT` and `LOCAL_LLM_MODEL` when using a local CPU model server

The repository ships `.env.example` only. Do not commit `.env`. Local scripts load `.env` automatically when present and never write its values into configs or logs.
If a real secret was ever tracked earlier, see `docs/SECURITY_RESPONSE.md`.

## Quickstart

Simulator smoke test:

```bash
python scripts/run_simulator.py --config configs/experiments/pilot.yaml --max-conditions 1 --max-episodes 1
```

Real-task harness smoke test:

```bash
python scripts/run_real_tasks.py --config configs/experiments/real_tasks.yaml
```

Bundled non-mock Layer B run on the frozen micro-task slice:

```bash
python scripts/run_real_tasks.py --config configs/experiments/real_tasks_gemini_nonmock_frozen.yaml
```

Expanded bundled non-mock Layer B run:

```bash
python scripts/validate_task_assets.py --manifest tasks/manifests/frozen_task_slice_v3.yaml
python scripts/run_real_tasks.py --config configs/experiments/real_tasks_gemini_nonmock_expanded.yaml
```

Compression-focused Layer B probe block:

```bash
python scripts/run_real_tasks.py --config configs/experiments/real_tasks_gemini_compression_probe.yaml
```

Reset-focused Layer B probe block:

```bash
python scripts/run_real_tasks.py --config configs/experiments/real_tasks_gemini_reset_probe.yaml
```

Local CPU model smoke test:

```bash
python scripts/run_real_tasks.py --config configs/experiments/real_tasks_local_cpu.yaml --max-tasks 1 --controllers C0
```

Gemini smoke test:

```bash
python scripts/run_real_tasks.py --config configs/experiments/real_tasks_gemini.yaml --max-tasks 1 --controllers C0
```

Analyze generated logs:

```bash
python scripts/analyze_results.py --input-dir artifacts --output-dir artifacts/analysis
```

Before zipping or publishing:

```bash
python scripts/release_clean.py --dry-run
python scripts/check_public_safety.py --mode release
```

Read the run status and result interpretation guide:

```bash
type result_summary.md
type docs/CURRENT_STATUS.md
```

Validate a design before main runs:

```bash
python scripts/check_experiment_design.py --layer layer_a --config configs/experiments/pilot_gemini.yaml
python scripts/check_experiment_design.py --layer layer_b --config configs/experiments/real_tasks_gemini.yaml
```

## Two-layer design

Layer A is the theory-faithful core. It includes:

- finite family sets and route instances
- a nonempty hidden adequate-family set
- delayed strong verification
- hard-cap budgets
- staleness, inertia, overlap burden, legacy contamination
- lossy compression with alias logging
- reset, branch, continue, retire, substitute, and tool actions
- exact recoverability and deterministic exact failure attribution

Layer B is a small-scope harness. It includes:

- a task manifest format for a fixed task slice
- deterministic family proxy construction
- an explicit proxy-construction layer separating task-authored, derived, and runtime proxies
- mock mode for offline validation
- a bundled public-safe frozen micro-task slice for non-mock runs
- explicit substitution, compression, and reset probe suites
- an expanded bundled eight-task frozen slice for stronger Layer B contrasts
- graceful behavior when external task assets are absent
- proxy-only instrumentation aligned to the theory

## Unified model adapters

The repository exposes a single adapter interface:

- `plan_step(context)`
- `compress_state(context)`
- `diagnose_failure(trace)`
- `choose_continue_branch_reset(context)`

Supported backbones:

- Gemini via config plus `GEMINI_API_KEY`
- a local CPU endpoint via Ollama-style or OpenAI-compatible HTTP APIs
- a deterministic mock adapter for offline tests and smoke checks

## Exact vs proxy note

Layer A logs exact simulator quantities. Layer B logs only proxies and task outcomes. The code and analysis pipeline keep these separate in field names, tables, figure titles, and documentation.

## Primary hypotheses

- `H1`: Success falls sharply once budget drops below a recoverability-supporting threshold.
- `H2`: Within-family substitution preserves success better than greedy deletion.
- `H3`: Lossy compression can create decision-relevant aliasing.
- `H4`: Compression harm grows when strong verification is delayed.
- `H5`: Reset-aware control can dominate stale continuation when contamination is high enough.
- `H6`: These effects are attributable to controller law under a fixed backbone, not only to backbone changes.

## Reproducibility note

Every run is driven by YAML config plus explicit seeds. Logs record:

- layer
- controller
- backbone model ID
- prompt version
- code revision
- run and episode identifiers
- structured trajectory events

Each run directory also includes a `run_manifest.json` with the resolved experiment config, model config, controller IDs, theory hypotheses, and a scientific-guardrail report.

If the repository is not inside a Git checkout, `code_revision` is logged as `unknown`.

## Directory map

- `configs/`: model, controller, and experiment YAML
- `prompts/`: versioned prompt templates
- `schemas/`: JSON Schemas for structured model outputs
- `simulator/`: Layer A generator, engine, scenarios, attribution
- `controllers/`: controller laws `C0` through `C6`
- `models/`: Gemini, local endpoint, and mock adapters
- `tasks/`: Layer B harness, proxy rule, and example manifest
- `logging/`: logging notes and field conventions
- `analysis/`: aggregation, statistics, and figure generation
- `scripts/`: runnable entry points
- `docs/`: build plan, implementation notes, and metric registry
- `result_summary.md`: top-level execution and interpretation summary
- `tests/`: unit tests, smoke checks, and offline pipeline tests

## Running a pilot simulator experiment

```bash
python scripts/check_experiment_design.py --layer layer_a --config configs/experiments/pilot.yaml
python scripts/run_simulator.py --config configs/experiments/pilot.yaml
python scripts/analyze_results.py --input-dir artifacts/pilot
```

Backbone-specific pilot configs are also provided:

- `configs/experiments/pilot_local_cpu.yaml`
- `configs/experiments/pilot_gemini.yaml`
- `configs/experiments/layer_a_identification_pilot_gemini.yaml`
- `configs/experiments/layer_a_h1_budget_threshold_gemini.yaml`
- `configs/experiments/layer_a_h2_substitution_gemini.yaml`
- `configs/experiments/layer_a_h3_h4_compression_gemini.yaml`
- `configs/experiments/layer_a_h5_reset_gemini.yaml`

This will generate logs and summary outputs from actual runs only. No figure is generated unless matching logs exist.

## How to read results correctly

- Use Layer A to make exact mechanism claims about reserve loss, compression aliasing, retirement, and reset behavior.
- Use Layer B to ask whether controller-law effects remain directionally visible under a fixed small task slice.
- Treat smoke runs as pipeline checks, not evidence for the theory.
- Treat mock-mode Layer B runs as instrumentation validation, not external-validity evidence.
- Report null or weak effects explicitly when they occur.

## Plugging in a real task slice later

1. Prepare a manifest following `tasks/README.md`.
2. Point `configs/experiments/real_tasks.yaml` at that manifest.
3. Keep backbone, prompt, turn budget, and tool permissions fixed within each comparison block.
4. Run the harness in non-mock mode only when the task assets are available and frozen.
5. Run `scripts/check_experiment_design.py` before main runs and keep the generated `run_manifest.json`.

Bundled non-mock assets are already provided for the shipped micro-task slice under `tasks/assets/`.
The larger frozen slice is `tasks/manifests/frozen_task_slice_v3.yaml`.

## Safety and privacy

- No secrets are hardcoded.
- Default configs use placeholders or mock backbones.
- No local absolute paths are shipped.
- The repository does not bundle external benchmark data.
- Run `python scripts/release_clean.py` and `python scripts/check_public_safety.py --mode release` before packaging a public zip.

## Limitations

- Layer B now ships a bundled frozen task slice, but it is still a small micro-task set rather than a benchmark-scale evaluation.
- The simulator is lightweight and theorem-aligned, not benchmark-realistic.
- Small smoke runs may produce unstable estimates or degenerate regressions; the analysis code preserves those outputs rather than hiding them.
- The paper discusses richer posterior-robust and theorem-local audit quantities than this lightweight implementation currently exposes online; those are documented as scoped simplifications rather than omitted silently.

## Citation

If you use this repository, cite the underlying theory preprint:

```text
Takahashi, K. (2026). Search Stability under Finite Context: A Minimal Theory of Adequacy Preservation, Compression, and Reset in Long-Running Agents. Zenodo. https://doi.org/10.5281/zenodo.18905242
```
