# Theory Validation Guide

## Purpose

This guide is for AI engineers and AI agents who need to run experiments from this repository in a way that is scientifically aligned with the theory preprint rather than merely operationally convenient.

The governing preprint is:

Takahashi, K. (2026). *Search Stability under Finite Context: A Minimal Theory of Adequacy Preservation, Compression, and Reset in Long-Running Agents*. Zenodo. [https://doi.org/10.5281/zenodo.18905242](https://doi.org/10.5281/zenodo.18905242)

## What the theory is about

The paper is not a generic claim that "better memory helps agents." Its object is narrower and more useful:

- long-running agents with finite active context
- delayed strong verification
- multiple partially plausible route families alive at once
- path-dependent contamination, staleness, and inertia
- lossy compression and reset decisions

The main empirical value of the repository is to help distinguish:

- raw model weakness
- premature family extinction
- compression-driven aliasing
- stale-legacy continuation
- mixed ecological failures

## What counts as a scientifically correct experiment here

The minimum rules are:

1. Hold the backbone fixed inside a comparison block.
2. Vary controller law, not several major design dimensions at once, when testing controller claims.
3. Keep exact Layer A quantities separate from Layer B proxies.
4. Preserve negative results rather than filtering them out.
5. Interpret outcomes as support or non-support under the tested regime, not universal proof.

## Which claims map to which experiments

The repository operationalizes the predeclared claims from `EXPERIMENT_SPEC.md`.

- H1 `Budget-threshold`: sweep budget in Layer A and inspect `final_success_rate`, `adequate_family_survival_rate`, and `family_extinction_rate`.
- H2 `Substitution-first`: compare `C0` vs `C3`, holding backbone fixed.
- H3 `Compression-alias`: sweep compression strength and inspect exact alias outcomes in Layer A.
- H4 `Lag-amplification`: repeat compression sweeps across lag settings and check whether harm grows under longer lag.
- H5 `Reset-rationality`: compare `C0` vs `C4` or `C5` under elevated contamination and reset cost sweeps.
- H6 `Controller-not-model`: verify that the directional controller effect appears when only controller law changes and the backbone stays fixed.

## Layer A: what it can validate

Layer A is where exact theory objects live. Use it for falsifiable checks of the paper's mesoscopic claims.

Exact claims available in Layer A:

- at least one adequate family survived to verification
- how many adequate families remained recoverable
- whether compression aliasing occurred
- whether a retirement was avoidable under the exact simulator rule
- which dominant failure channel was assigned

Recommended first checks, matching the paper's simulator appendix:

1. Diversity-floor test
2. Recoverability-preserving substitution test
3. Compression-alias test
4. Reset-threshold test
5. Breadth-depth test

This repository currently supports those checks through the core grid and summary figures, with lightweight rather than theorem-maximal instrumentation.

## Layer B: what it can and cannot validate

Layer B is a limited external-validity probe, not a latent-truth oracle.

It can support:

- whether controller-law effects remain directionally visible on a small frozen task slice
- whether branch-family proxies, retirements, resets, and compression events can be audited consistently

It cannot support:

- claims about exact adequate-family truth
- claims that a proxy equals a latent theory quantity
- leaderboard-style conclusions

If Layer B is in mock mode, it is only a pipeline or instrumentation check.

## How to explain the theory's practical benefits

The theory is useful if it helps practitioners reason about failure structure better than a single "model got it wrong" explanation.

The practical benefits to emphasize are:

- separating ecology failures from raw model failures
- making branch preservation and family reserve explicit
- showing when compression is safe enough and when it is hazardous
- clarifying when reset should be evaluated as a value comparison, not a panic button
- making negative or null effects interpretable rather than embarrassing

Avoid describing the benefit as guaranteed performance gain. The paper does not claim that.

## How to avoid invalid conclusions

Do not claim:

- universal validation of the theory
- exact recovery of latent families in Layer B
- that a stronger backbone alone validates the controller law
- that one successful smoke test is evidence for a hypothesis

Do claim, when justified by logs:

- support or non-support for a hypothesis under the tested regime
- exact Layer A evidence for a mechanism
- proxy-based Layer B evidence with explicit uncertainty and scope limits

## Minimal recommended workflow

1. Run `python scripts/check_experiment_design.py --layer layer_a --config ...`
2. Run a Layer A smoke test
3. Run a Layer A pilot grid under one backbone
4. Analyze logs and inspect exact figures
5. Run `python scripts/check_experiment_design.py --layer layer_b --config ...`
6. Run a Layer B smoke test
7. Run a small fixed task slice only after the task manifest is frozen

## Audit checklist for AI agents

Before reporting results, verify all of the following:

- The comparison block used one backbone model ID only.
- Prompt version was fixed.
- Controller IDs were logged.
- Seeds were logged.
- Exact and proxy fields were not mixed in one claim.
- Failed conditions were preserved in the output tables.
- The report language says "support", "non-support", or "directional evidence", not "proof".

