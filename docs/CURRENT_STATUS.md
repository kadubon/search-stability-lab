# Current Status

## What currently works

- Layer A exact simulator suite is complete and remains the strongest evidence source.
- Layer B bundled expanded slice runs end-to-end on Gemini and on the local CPU endpoint.
- Public-safety and reproducibility checks are automated enough to rerun safely.

## Strongest evidence

- Layer A most strongly supports the substitution-first story and the compression-alias mechanism.
- Layer B most clearly supports `C3 > C0` across both backbones on the bundled task slice.
- Layer B reset probes now provide directional support for reset-aware control over `C0`.
- Layer B compression probes now provide limited outcome-sensitive support for `C5` over `C0/C1` on the authored compression suite.

## Weakest evidence

- Layer B compression remains the weakest positive Layer B result because it is based on only two authored tasks.
- `C5` remains mixed and should not be presented as dominant.

## Known confounds

- Layer A exactness is simulator-exact, not world-exact.
- Layer B remains proxy-limited and based on bundled mechanistic probe tasks.
- Local CPU runs remain confounded by structured-output failures.

## Hypothesis table

- `H1`: `partial_support`. High budget improved pooled success, but the pattern was not uniformly monotone by controller.
- `H2`: `supported`. C3 beat C0 and removed exact avoidable-retirement failures in the Layer A suite.
- `H3`: `supported`. C1 showed exact compression-alias failures and lower success than C0/C5.
- `H4`: `partial_support`. For C1, long lag raised exact alias rates relative to short lag across sampled compression levels.
- `H5`: `partial_support`. C4 outperformed C0 in the targeted regime, but stale-legacy failures were not directly realized.

## Layer B controller summary

- `gemini-2.5-flash-lite`:
  `C0` success rate = `0.0000` (task_outcome)
  `C3` success rate = `0.5000` (task_outcome)
  `C5` success rate = `0.3333` (task_outcome)
- `gemma3:1b`:
  `C0` success rate = `0.0000` (task_outcome)
  `C3` success rate = `0.5000` (task_outcome)
  `C5` success rate = `0.0000` (task_outcome)

## Structured-output fragility

- `gemini-2.5-flash-lite` / `C0` / `invalid_json`: `1` task endings
- `gemma3:1b` / `C0` / `invalid_json`: `5` task endings
- `gemma3:1b` / `C0` / `timeout`: `1` task endings
- `gemma3:1b` / `C3` / `invalid_json`: `5` task endings
- `gemma3:1b` / `C3` / `timeout`: `1` task endings
- `gemma3:1b` / `C5` / `invalid_json`: `5` task endings
- `gemma3:1b` / `C5` / `timeout`: `1` task endings

## What to run next

- Use Layer A for main mechanism claims.
- Use the bundled Layer B slice for probe-style controller comparisons only.
- If stronger Layer B compression evidence is needed, expand the compression suite or increase the frozen slice before making stronger claims.
