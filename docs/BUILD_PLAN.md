# Build Plan

## Purpose
Turn this repository into a public-safe, implementation-ready experiment codebase for the "Search Stability under Finite Context" theory, following `EXPERIMENT_SPEC.md` as the implementation contract and the paper `.tex` file as the terminology reference.

## Guiding constraints
- Preserve exact-vs-proxy separation.
- Keep the backbone fixed within each comparison block while varying controller law.
- Prefer lightweight, CPU-first, deterministic implementations.
- Do not fabricate empirical results or imply universal validation.
- Keep all defaults public-safe: no secrets, no local paths, no bundled private assets.

## Milestone sequence
1. Repository scaffold and safety defaults
   - Add packaging, dependency, config, docs, prompts, schemas, scripts, and test directories.
   - Add `.gitignore`, `.env.example`, Apache 2.0 `LICENSE`, and safe default configs.
2. Shared runtime infrastructure
   - Implement YAML config loading, deterministic seeding, prompt loading, schema validation, structured exceptions, and JSONL event logging.
   - Implement a unified model adapter interface with Gemini, local endpoint, and mock adapters.
3. Layer A simulator
   - Implement finite family/route state, nonempty adequate-family sampling, lagged verification, compression aliasing, contamination, reset/branch/continue dynamics, and deterministic failure attribution.
   - Implement controllers `C0` through `C6`.
   - Add a simulator runner and an end-to-end smoke path.
4. Layer B harness
   - Implement a safe task-manifest driven harness with mock mode and placeholder SWE-Bench-Lite-style task integration points.
   - Preserve theory-aligned proxy diagnostics and deterministic family proxy rules.
5. Analysis and reporting
   - Aggregate JSONL logs, validate schema consistency, compute summary tables, Wilson intervals, preregistered contrasts, and a mixed-effects or fallback regression path.
   - Generate required figures with exact/proxy labeling.
6. Documentation and verification
   - Write `README.md`, `docs/implementation_notes.md`, and `docs/metric_registry.csv`.
   - Add unit tests, smoke tests, mock-model tests, malformed-output handling tests, and a lightweight GitHub Actions workflow.

## Intended implementation choices
- Python 3.11+ with `pydantic`, `numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`, `PyYAML`, `jsonschema`, and `pytest`.
- YAML for experiment, controller, and model configuration.
- JSON Schema files under `schemas/` with runtime validation for model outputs.
- JSONL event logs under a configurable output directory, with enough metadata to reconstruct runs.

## Known planned simplifications
- Layer B ships without benchmark assets and defaults to mock mode or explicit graceful failure when task assets are absent.
- The local model adapter targets an OpenAI-compatible local endpoint surface so it can work with Ollama or `llama.cpp`-style servers without bundling model weights.
- The simulator remains intentionally lightweight and theorem-aligned rather than benchmark-realistic.

## Paper/spec alignment notes to verify during implementation
- If naming or emphasis differs between the paper and `EXPERIMENT_SPEC.md`, implementation behavior follows the spec and the mismatch will be recorded in `docs/implementation_notes.md`.
- The simulator will implement a deterministic dominant failure-channel rule plus auxiliary multi-label flags to preserve failure ambiguity without collapsing exact labels into vague narratives.
