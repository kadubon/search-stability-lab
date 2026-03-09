# Run Report 2026-03-09

## Scope

This report records the first post-audit execution sequence requested for this repository:

1. run a Layer A pilot
2. then attempt a frozen-slice Layer B non-mock run

The report is factual and does not convert repository-readiness checks into empirical support claims.

## Layer A pilot

### Configuration

- config: `configs/experiments/pilot_gemini.yaml`
- output directory: `artifacts/pilot_gemini/pilot-gemini-20260308T231202Z-0512a4a1`
- backbone: `gemini-2.5-flash-lite` simulator profile
- controllers: `C0`, `C2`, `C3`, `C5`
- design check: passed

### Observed exact outcomes

From `analysis/final_outcomes.csv` and `analysis/summary_tables.csv`:

- `C0`: success rate `1.0000`
- `C2`: success rate `1.0000`
- `C3`: success rate `1.0000`
- `C5`: success rate `0.9896`

Observed failed episodes:

- one failed episode under `C5`
- dominant exact failure channel: `stale_legacy_continuation`

Pairwise pilot contrasts:

- `C0 vs C2`: no observed difference in this pilot
- `C0 vs C3`: no observed difference in this pilot
- `C0 vs C5`: very small observed difference, with no meaningful pilot evidence of separation
- `C2 vs C5`: very small observed difference, with no meaningful pilot evidence of separation

### Scientific interpretation

This pilot does **not** provide strong evidence for the main controller-law hypotheses. The exact outcomes are near ceiling, so the current pilot setting appears too easy or too weakly discriminative for a strong theory test.

What can be said honestly:

- the simulator pipeline ran end to end
- exact quantities were logged and analyzed correctly
- one exact stale-legacy failure was observed

What cannot be said honestly from this pilot:

- that the theory-guided controllers outperform greedy control
- that H1 through H5 received empirical support
- that the absence of differences means the theory is wrong

The appropriate conclusion is that this pilot is operationally successful but scientifically underpowered for hypothesis discrimination.

## Layer B non-mock attempt

### Configuration

- config: `configs/experiments/real_tasks_gemini_nonmock_frozen.yaml`
- frozen manifest: `tasks/manifests/frozen_task_slice_v1.yaml`
- backbone: `gemini-2.5-flash-lite`
- mode: `mock_mode: false`
- strict assets: `true`
- design check: passed

### Outcome

The run failed immediately with:

`MissingAssetError: Task assets missing for task-001 and strict_assets=True.`

### Scientific interpretation

This is the correct behavior.

The repository did **not** fabricate a Layer B evaluation in the absence of frozen local task assets. That failure preserves scientific honesty.

What can be said honestly:

- the frozen manifest and non-mock configuration are in place
- the harness correctly refuses to proceed without required assets

What cannot be said honestly:

- that a non-mock Layer B evaluation has been completed
- that any real-task evidence has been obtained yet

## Bottom line

At this point:

- Layer A is execution-ready and analyzable, but the current pilot grid is too easy to be strongly informative
- Layer B non-mock is configuration-ready, but blocked pending frozen local task assets

## Recommended next step

1. make the Layer A pilot more discriminative or move to a harsher main grid
2. populate `tasks/assets/task-001`, `task-002`, and `task-003` with the frozen local task slice
3. rerun `configs/experiments/real_tasks_gemini_nonmock_frozen.yaml`
