# Final Audit

## Audit target

This audit checks whether the repository is experiment-ready with respect to:

- `EXPERIMENT_SPEC.md`
- the theory preprint `Search Stability under Finite Context.tex`
- public-repo safety
- scientific non-arbitrariness
- clear interpretation by AI engineers and AI agents

## Overall judgment

The repository is experiment-ready for:

- Layer A theory-aligned simulator experiments
- Layer B mock-safe harness experiments
- local CPU and Gemini-backed controller instrumentation
- structured logging, aggregation, and figure generation

with the scoped limitations listed below.

## What was checked

### Scientific alignment

- The repo preserves the theory's main object: finite-context search stability under delayed verification.
- Layer A uses exact hidden adequate-family structure and exact failure-channel attribution.
- Layer B uses deterministic proxies and does not claim latent truth.
- The README and guidance now explicitly frame the repository as a diagnostic and falsification-oriented layer, not a universal controller theory.

### Anti-arbitrariness safeguards

- Comparison blocks are defined by a single model config.
- `scripts/check_experiment_design.py` checks fixed-backbone and scope conditions before runs.
- `run_manifest.json` records the resolved config, hypotheses, backbone, controller set, and guardrail warnings.
- Negative or null results are preserved by design in tables and figures.

### Public safety

- `.env` is ignored.
- `.env.example` uses placeholders or safe local defaults.
- No API keys are embedded in configs or docs.
- Public text files were checked for local absolute paths and cleaned.

### Analysis honesty

- Skipped Layer B tasks caused by missing assets are now explicitly logged as skipped and excluded from outcome analysis.
- Summary tables mark whether the success metric is `exact` or `task_outcome`.
- Layer A figure titles now include backbone labels to reduce ambiguity.

## Important scientific strengths

- The repository distinguishes raw-model failure from ecological failure modes rather than collapsing everything into accuracy.
- The theory's main mechanisms are inspectable:
  - reserve loss
  - substitution before deletion
  - compression aliasing
  - lag amplification
  - reset under stale legacy contamination
- The repo is usable by both humans and AI agents because interpretation rules, invalid-claim examples, and experiment checklists are written down explicitly.

## Remaining scoped limitations

These are deliberate scope limits, not silent deviations.

1. Layer B remains a small-slice harness and defaults to mock mode.
2. The simulator is lightweight and does not implement the full posterior-robust audit machinery discussed in the paper appendix.
3. Layer A backbones are represented through calibrated profile parameters rather than live API calls. This is acceptable for the simulator's role but should be described as a controlled surrogate for backbone differences in simulator space.
4. Real benchmark assets are not bundled, and absent assets no longer produce pseudo-evaluation.

## Practical conclusion

For a public scientific repository, the current state is suitable for:

- publishing the codebase
- running pilot simulator studies
- running mock-safe real-task pipeline checks
- preparing a frozen small real-task slice
- auditing controller-law experiments with explicit scope limits

It is not suitable for:

- claiming full empirical validation of the theory
- presenting mock Layer B runs as real benchmark evidence
- treating Layer B proxies as exact theory quantities
