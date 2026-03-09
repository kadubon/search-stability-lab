# Layer A Suite Report (2026-03-09)

## Scope

This report summarizes the completed post-redesign Layer A runs for H1-H5 using one fixed backbone:

- backbone: `gemini-2.5-flash-lite`
- suite manifest: `artifacts/layer_a_suite_2026-03-09/manifest.json`
- measurement scope: exact simulator quantities only

These are simulator results. They do not establish external validity on real tasks.

## Reproduction

Generate the suite summary from the saved analyzed runs:

```bash
python scripts/summarize_layer_a_suite.py --manifest artifacts/layer_a_suite_2026-03-09/manifest.json --output-dir artifacts/layer_a_suite_2026-03-09
```

Each run can also be reanalyzed directly with `scripts/analyze_results.py`.

## Run set

- H1: `configs/experiments/layer_a_h1_budget_threshold_gemini.yaml`
- H2: `configs/experiments/layer_a_h2_substitution_gemini.yaml`
- H3/H4: `configs/experiments/layer_a_h3_h4_compression_gemini.yaml`
- H5: `configs/experiments/layer_a_h5_reset_gemini.yaml`

## Findings

### H1: Budget threshold

Result: partial support.

- pooled success by budget:
  - `high`: `10/60 = 0.1667`
  - `low`: `4/60 = 0.0667`
  - `medium`: `4/60 = 0.0667`
- by controller:
  - `C0`: `high 0.20`, `low 0.05`, `medium 0.00`
  - `C2`: `high 0.25`, `low 0.15`, `medium 0.10`
  - `C5`: `high 0.05`, `low 0.00`, `medium 0.10`

Interpretation:

- the redesign succeeded in breaking the old ceiling effect
- high budget produced more exact successes in the pooled sample
- the pattern is not uniformly monotone for every controller, so this is not a clean universal threshold law

### H2: Within-family substitution

Result: support against the naive baseline, not universal dominance.

- pooled success:
  - `C0`: `2/80 = 0.0250`
  - `C3`: `8/80 = 0.1000`
  - `C5`: `6/80 = 0.0750`
- exact avoidable-retirement rate:
  - `C0`: `7/80 = 0.0875`
  - `C3`: `0/80 = 0.0000`
  - `C5`: `0/80 = 0.0000`

Interpretation:

- `C3` outperformed `C0` and eliminated exact `avoidable_retirement` failures in this suite
- `C5` also eliminated `avoidable_retirement`, so the key signal is not unique to one controller law
- this supports the theory claim that preserving family-level optionality can matter, but does not show that `C3` is best overall

### H3: Compression harm

Result: support.

- pooled exact success:
  - `C0`: `24/480 = 0.0500`
  - `C1`: `4/480 = 0.0083`
  - `C5`: `37/480 = 0.0771`
- exact `compression_alias` rate:
  - `C0`: `0/480 = 0.0000`
  - `C1`: `66/480 = 0.1375`
  - `C5`: `0/480 = 0.0000`

Interpretation:

- the summarize-heavy controller `C1` exhibited substantial exact alias failures and near-zero success
- the harm is mechanism-visible in the exact failure labels, not just in aggregate success

### H4: Lag amplification

Result: partial support within the compression-heavy controller.

For `C1`, exact `compression_alias` was higher under long lag than short lag at every compression setting:

- `none`: `0.0750` vs `0.0375`
- `mild`: `0.2375` vs `0.1000`
- `strong`: `0.2250` vs `0.1500`

Interpretation:

- long lag amplifies alias risk for the controller that relies on compression
- the effect is visible in exact failure channels
- the suite does not show a clean monotone increase from `mild` to `strong` compression inside `C1`, so the strongest safe claim is lag amplification, not a strict dose-response law

### H5: Reset under contamination

Result: directional support, not full mechanistic confirmation.

In the intended high-contamination, low-reset-cost conditions:

- `C0`:
  - `none`: `1/20 = 0.05`
  - `strong`: `1/20 = 0.05`
- `C4`:
  - `none`: `3/20 = 0.15`
  - `strong`: `4/20 = 0.20`
- `C5`:
  - `none`: `0/20 = 0.00`
  - `strong`: `0/20 = 0.00`

Mean reset count over the full H5 run:

- `C0`: `0.0000`
- `C4`: `0.7813`
- `C5`: `2.5250`

Interpretation:

- a calibrated reset policy (`C4`) outperformed both no-reset (`C0`) and over-resetting (`C5`) in the targeted conditions
- however, exact `stale_legacy_continuation` failures were not observed in this run set
- the safe conclusion is directional support for reset helpfulness under the designed contamination regime, not direct confirmation of the stale-legacy channel as the dominant realized failure mode

## Overall judgment

The redesign made H1-H5 more identifiable than the earlier ceilinged pilot. The strongest findings in this suite are:

- H2 support against the naive baseline through elimination of exact avoidable retirement
- H3 support through substantial exact compression-alias failures in the summarize-heavy controller
- H4 partial support through higher exact alias rates under longer lag
- H5 directional support for calibrated resets in the targeted regime

The weakest point remains H1, which shows a pooled budget effect but not a controller-uniform threshold pattern.

## What is still not established

- no Layer B non-mock evidence is available yet because frozen task assets are still absent
- no claim about universal controller superiority is warranted
- no claim about external validity or production agents is warranted from these runs alone

## Next scientifically sound step

Keep this Layer A suite as the exact mechanism benchmark, then add a frozen Layer B task slice with real assets and repeat only the preregistered controller contrasts using proxy labels.
