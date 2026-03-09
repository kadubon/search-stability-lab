# Layer B Probe Report (2026-03-09)

## Scope

This report summarizes the completed Layer B probe blocks added for:

- substitution: `C0`, `C3`, `C5`
- compression: `C0`, `C1`, `C5`
- reset: `C0`, `C4`, `C5`

All quantities reported here are `proxy (task harness)` or task-outcome quantities. They are not exact latent-family truth.

Probe suite manifest:

- `artifacts/layer_b_probe_suite_2026-03-09/manifest.json`

## Substitution suite

Bundled tasks:

- `task-001`
- `task-005`

Results:

- Gemini:
  - `C0`: `0/2`
  - `C3`: `2/2`
  - `C5`: `0/2`
- local CPU:
  - `C0`: `0/2`
  - `C3`: `2/2`
  - `C5`: `0/2`

Interpretation:

- `C3 > C0` is reproduced cleanly on both backbones.
- In this suite, `C5` does not improve on the substitution-first controller.
- This is the clearest completed Layer B result.

Important confound:

- Gemini logged backend-output errors on these tasks.
- local CPU logged unrecoverable invalid JSON on these tasks.
- The task outcome contrast is still visible, but it should be read as controller-law evidence under model-output confounds.

## Compression suite

Bundled tasks:

- `task-003`
- `task-007`

Results:

- Gemini:
  - `C0`: `0/2`
  - `C1`: `0/2`
  - `C5`: `2/2`
- local CPU:
  - `C0`: `0/2`
  - `C1`: `0/2`
  - `C5`: `2/2`

Proxy pattern:

- `C1` produced `compression_collision_proxy = 5.0` on both backbones.
- `C0` and `C5` stayed at `0.0`.
- `C5` resolved both tasks on both backbones after preserving the delayed discriminating routes needed at verification.

Interpretation:

- The compression probe now exposes both proxy variation and a limited outcome-level contrast.
- The safe read is that compression-heavy control (`C1`) looks harmful on this bundled suite, while the fuller controller (`C5`) preserves enough route structure to resolve the task.
- This remains a small authored probe suite, so it should be described as limited outcome-sensitive evidence, not broad validation.

## Reset suite

Bundled tasks:

- `task-002`
- `task-004`
- `task-006`
- `task-008`

Results:

- Gemini:
  - `C0`: `0/4`
  - `C4`: `3/4`
  - `C5`: `3/4`
- local CPU:
  - `C0`: `0/4`
  - `C4`: `3/4`
  - `C5`: `3/4`

Proxy pattern:

- `C4` and `C5` both showed `reset_helpfulness_proxy = 1.0` on resolved tasks.
- mean `stale_continuation_proxy` dropped from `1.6463` for `C0` to `0.5519` for `C4` and `0.6988` for `C5`.
- mean `post_reset_resolution_improvement_proxy` was `0.26` for both `C4` and `C5`.

Interpretation:

- The reset probe now makes a reset-oriented controller contrast visible in Layer B.
- The safe read is directional support for reset-aware control on this bundled probe suite.
- It is still not broad validation, and `C4` versus `C5` is not separated here.

Important confound:

- local CPU still logged invalid JSON on every final task record in this suite.
- Gemini had some structured-output or backend-output failures for `C0` and `C4`, but `C5` completed without final invalidity.

## Overall conservative read

- Layer B still most strongly supports the substitution-first story.
- Layer B now also provides directional reset-probe evidence, because `C4` and `C5` both beat `C0` on the reset suite and improved reset-related proxies.
- Layer B compression evidence is now limited but outcome-sensitive on the bundled compression suite, while still relying on very small probe tasks.
- Layer A remains the main mechanism-validation layer for exact claims.

## What remains limited

- all Layer B quantities remain proxy or task-outcome quantities
- the bundled tasks are mechanistic probes, not a benchmark
- compression support in Layer B is still proxy-centric
- local CPU results remain materially confounded by structured-output invalidity
