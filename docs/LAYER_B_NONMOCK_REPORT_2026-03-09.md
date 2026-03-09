# Layer B Non-Mock Report (2026-03-09)

## Scope

This report summarizes completed Layer B non-mock runs on the expanded bundled frozen micro-task slice:

- task manifest: `tasks/manifests/frozen_task_slice_v2.yaml`
- suite manifest: `artifacts/layer_b_nonmock_expanded_suite_2026-03-09/manifest.json`
- task bundles: `tasks/assets/task-001` through `tasks/assets/task-006`

These are Layer B task-outcome and proxy results. They are not exact latent-family evidence and they are not benchmark claims.

## Bundled task slice

The expanded non-mock slice contains six public-safe bundled micro-repositories:

- `task-001`: parser fallback preservation
- `task-002`: auth refresh path preservation under stale legacy pressure
- `task-003`: summary-cache collision avoidance
- `task-004`: checkpoint resume recovery under stale checkpoint contamination
- `task-005`: serializer default preservation
- `task-006`: planner reset recovery under stale planner continuation

Each task bundle includes frozen metadata, a minimal workspace, and a fixed test command.

## Gemini block

Backbone:

- `gemini-2.5-flash-lite`

Run:

- `artifacts/real_tasks_gemini_nonmock_expanded/real-gemini-nonmock-expanded-20260309T011314Z-b3d4732e`

Controller-level task outcomes:

- `C0`: `0/6`
- `C3`: `3/6`
- `C5`: `2/6`

Task-level outcomes:

- `C0` failed all six tasks
- `C3` resolved `task-001`, `task-003`, and `task-005`
- `C5` resolved `task-001` and `task-005`

Proxy notes:

- `C0` showed `avoidable_retirement_proxy=1` on `task-001` and `task-003`
- `C5` issued one reset on `task-002`, `task-003`, `task-004`, and `task-006`, but those tasks did not resolve
- the reset-oriented tasks therefore produced a negative Layer B result for `C5` on this slice

Interpretation:

- on this expanded bundled slice, substitution-first control (`C3`) again outperformed the greedy baseline (`C0`)
- `C5` remained mixed rather than dominant, even on tasks designed to exercise reset pressure
- the safest Layer B claim is directional support for within-family preservation, plus an honest negative result for reset dominance in this micro-task set

## Local CPU block

Backbone:

- `gemma3:1b`

Runs:

- `artifacts/real_tasks_local_cpu_nonmock_expanded_suite_2026-03-09`

Controller-level task outcomes:

- `C0`: `0/6`
- `C3`: `3/6`
- `C5`: `0/6`

Task-level outcomes:

- `C0` failed all six tasks
- `C3` resolved `task-001`, `task-003`, and `task-005`
- `C5` failed all six tasks

Important runtime note:

- every local CPU run recorded repeated structured-output failures, including invalid JSON and occasional timeouts

Interpretation:

- the local endpoint completed the expanded task harness, but it did not reliably satisfy the structured-output contract on this non-mock slice
- because the controller fallback remained active, the task outcomes are still usable as harness evidence
- however, the local block should be read as task-outcome evidence under repeated model-output failures, not as a clean structured-generation success

## Cross-backbone reading

Shared directional pattern:

- `C3` beat `C0` on both backbones

Backbone-specific difference:

- `C5` achieved `2/6` on Gemini but `0/6` on the local CPU block

Safe claim:

- the expanded bundled Layer B slice preserves at least one controller-law contrast across both backbones

Unsafe claim:

- that these three micro-tasks establish general real-world validity

## Scientific limits

- sample size is only six tasks per backbone
- the task slice is bundled and public-safe, not benchmark-derived
- Layer B remains proxy-limited by design
- the local CPU block experienced repeated structured-output failures

## Next step if stronger Layer B evidence is needed

Expand the frozen slice beyond six bundled micro-tasks, while keeping:

- the backbone fixed within each comparison block
- the task manifest frozen
- the proxy rule fixed
- all negative and malformed-output cases logged
