# Experiment Redesign

## Why a redesign was needed

The earlier pilot configuration ran correctly but was not sufficiently discriminative for H1-H5. Success rates were near ceiling, which made it hard to distinguish:

- budget-threshold effects
- substitution-first effects
- compression alias harm
- lag amplification
- reset rationality under stale legacy contamination

That is a scientific design problem, not a reason to overinterpret the pilot.

## What was changed

### Simulator mechanics

The Layer A simulator was tightened in theory-aligned ways:

- archived routes are no longer treated as broadly recoverable by default
- adequate families may be initially buried rather than always locally attractive
- non-adequate families may act as misleading lures
- verification potential is partly latent and only revealed through continued survival and evidence accumulation
- compression aliasing harms recoverability more persistently
- contamination reduces evidence gain more directly
- reset clears stale legacy state but now has to clear a more meaningful continuation penalty

These changes are meant to make the paper's mechanism claims visible, not to force theory-guided controllers to win by construction.

### Experiment structure

The repository now includes targeted Layer A experiment configs:

- `configs/experiments/layer_a_identification_pilot_gemini.yaml`
- `configs/experiments/layer_a_h1_budget_threshold_gemini.yaml`
- `configs/experiments/layer_a_h2_substitution_gemini.yaml`
- `configs/experiments/layer_a_h3_h4_compression_gemini.yaml`
- `configs/experiments/layer_a_h5_reset_gemini.yaml`

These separate hypothesis-identification from generic pilot execution.

## Intended use of each config

- `layer_a_identification_pilot_gemini.yaml`
  - broad discriminative pilot, useful before main runs
- `layer_a_h1_budget_threshold_gemini.yaml`
  - focused budget sweep for H1
- `layer_a_h2_substitution_gemini.yaml`
  - focused `C0` vs `C3` style substitution comparison for H2
- `layer_a_h3_h4_compression_gemini.yaml`
  - focused compression and lag sweep for H3 and H4
- `layer_a_h5_reset_gemini.yaml`
  - focused stale-legacy and reset-cost sweep for H5

## Calibration outcome

Small post-redesign calibration runs showed that the simulator is no longer at ceiling:

- H1-targeted runs showed zero success at low budget and nonzero success at high budget in a small sample
- H5-targeted runs showed at least one condition where `C4` exceeded `C0`
- H3/H4-targeted runs showed `compression_alias` failures under the summarize-heavy controller

These are calibration checks, not final study claims.

## Scientific stance

The redesign aims to make the theory falsifiable under more informative conditions. It does not guarantee that theory-guided controllers will dominate in the final study. Negative or mixed outcomes remain possible and must be reported honestly.
