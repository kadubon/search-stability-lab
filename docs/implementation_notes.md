# Implementation Notes

## Mapping theory objects into code

The implementation follows `EXPERIMENT_SPEC.md` for executable behavior and uses the paper `.tex` file for terminology and causal alignment.

Layer A maps the paper's objects into lightweight simulator state:

- Family set `F`: `simulator/generator.py` samples a finite family set per episode.
- Hidden adequate-family set `V`: sampled nonempty by construction in `generate_episode`.
- Route instances within families: `RouteState` in `simulator/types.py`.
- Finite active-context budget: `SimulatorCondition.budget_cap`, enforced in `simulator/engine.py`.
- Delayed strong verification: `verification_step`, derived from the lag level.
- Retention cost, overlap burden, staleness, inertia, compression sensitivity: explicit route fields.
- Lossy compression: `compress` action reduces retention cost and may set `alias_flag`.
- Reset / branch / continue actions: implemented as `reset`, `branch`, and `keep` or `tool`.
- Exact recoverability: a family is exactly recoverable when at least one non-aliased adequate route remains recoverable at verification.

Layer B maps theory objects to deterministic proxies:

- Candidate branches are the Layer B analogue of routes.
- Branch-family clustering uses the documented deterministic family proxy rule in `tasks/proxy.py`.
- Summaries and reopenable state are tracked as compressed or recoverable branches.
- Exact adequate-family truth is not available and is never logged for Layer B.

## Where exact quantities are available

Exact quantities are only available in Layer A and are logged as exact fields:

- `adequate_family_ids_true`
- `recoverable_family_ids_true`
- `failure_channel_true`
- `alias_event_true`
- `avoidable_retirement_true`

The main exact primary outcomes are:

- `final_success_rate`
- `adequate_family_survival_rate`
- `recoverable_family_count_at_verification`
- `family_extinction_rate`

## Where only proxies are available

Layer B only exposes proxies or task outcomes:

- `represented_candidate_family_count_proxy`
- `recoverable_candidate_count_proxy`
- `compression_collision_proxy`
- `avoidable_retirement_proxy`
- `reset_helpfulness_proxy`
- `failure_channel_proxy`

These are instrumentation aids for small real-task runs. They are not treated as exact theory quantities.

## Deterministic failure attribution rule

Layer A assigns one exact dominant failure channel to every failed episode using deterministic boolean triggers:

1. `compression_alias`
2. `avoidable_retirement`
3. `stale_legacy_continuation`
4. `missed_adequate_family`
5. `raw_model_failure`

If more than one structural trigger among alias, retirement, legacy, and miss is active, the episode is labeled `mixed_failure`. Otherwise the first active trigger in the list above is used. This is conservative: when multiple structural channels co-occur, the implementation does not pretend a single exact cause is uniquely identifiable.

## Family proxy rule for Layer B

The default deterministic family proxy rule is:

1. Use `proxy_family_hint` from the manifest when present.
2. Otherwise use the sorted target-file list joined by `|`.
3. Otherwise use the normalized first sentence of the issue summary.

Derived alternative candidate families are generated from the proxy key plus a small deterministic set of file stems and summary tokens. This supports stable, reviewable branch clustering without claiming access to latent true family structure.

## Deviations and simplifications

The repository intentionally implements a lightweight simulator rather than the paper's richest posterior-robust construction.

- The paper discusses richer posterior ambiguity sets, local safety certificates, and theorem-local audit estimators. This implementation logs simpler exact state variables and a deterministic attribution rule to stay CPU-first and reproducible.
- The spec's step-decision schema example uses `substitute`, while the allowed-action section uses `substitute-within-family`. The implementation standardizes on `substitute-within-family` and records this mismatch here.
- Layer B is architecture-ready and runnable in mock mode, but does not bundle SWE-Bench Lite assets or claim benchmark evaluation when those assets are absent.
- The local endpoint adapter supports Ollama-style and OpenAI-compatible local servers, but does not ship model weights.

## Scientific scope

This repository is scoped to test whether controller-law differences are observable under a controlled simulator and a small, explicitly limited real-task harness. It does not claim universal validation of the theory, broad benchmark superiority, or proof of empirical necessity beyond the implemented conditions and logged evidence.

