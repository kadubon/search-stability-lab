# Layer B Status

Layer B is a low-compute, proxy-only mechanistic probe layer.

## Current strongest value

- The clearest completed Layer B result remains the substitution-first story: `C3 > C0`.
- This is visible on the bundled probe slice across both Gemini and local CPU runs.
- The reset probe now also shows directional support for reset-aware control (`C4` and `C5` over `C0`) on the authored reset suite.
- The compression probe now shows limited outcome-sensitive separation, with `C5` resolving the bundled compression tasks while `C0` and `C1` do not.

## Current limits

- Layer B is not broad external validation.
- Compression evidence remains the weakest completed positive Layer B result because it comes from only two authored probe tasks.
- Local CPU runs remain partly confounded by malformed structured output.
- Layer A remains the main source of exact mechanism evidence.

## What has been upgraded

- explicit substitution, compression, and reset probe manifests
- explicit controller blocks for `C0/C1/C5` and `C0/C4/C5`
- a clearer proxy-construction layer
- additional bundled compression and reset micro-tasks
- bounded local structured-output repair with explicit repair logging

## Completed probe blocks

- substitution:
  - Gemini `C0=0/2`, `C3=2/2`, `C5=0/2`
  - local CPU `C0=0/2`, `C3=2/2`, `C5=0/2`
- compression:
  - Gemini `C0=0/2`, `C1=0/2`, `C5=2/2`
  - local CPU `C0=0/2`, `C1=0/2`, `C5=2/2`
- reset:
  - Gemini `C0=0/4`, `C4=3/4`, `C5=3/4`
  - local CPU `C0=0/4`, `C4=3/4`, `C5=3/4`

Detailed report:

- `docs/LAYER_B_PROBE_REPORT_2026-03-09.md`

## Safe interpretation rule

Use Layer B to ask whether controller-law effects remain directionally visible on transparent probe tasks.
Use Layer A for main mechanism claims.
