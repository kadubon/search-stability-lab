# Task Manifest Format

Layer B does not bundle benchmark assets. Instead it consumes a task manifest that can point to a public-safe local slice later.

This repository now also ships bundled micro-task slices under `tasks/assets/` for reproducible non-mock harness runs. Those bundles are public-safe and frozen, but they are not benchmark data.

Required task fields:
- `task_id`
- `repository`
- `title`
- `issue_summary`

Optional fields:
- `target_files`
- `test_command`
- `task_assets_path`
- `proxy_family_hint`
- `resolving_family_keys`
- `suite`
- `probe_purpose`
- `target_hypotheses`
- `primary_proxy_metrics`
- `suitable_backbones`

Deterministic family proxy rule:
1. Use `proxy_family_hint` when present.
2. Otherwise use the sorted `target_files` joined by `|`.
3. If neither is available, use the normalized first sentence of `issue_summary`.

This rule is fixed by default for Layer B runs and should be frozen before main evaluation.

Bundled asset bundle requirements for non-mock runs:

- `README.md`
- `metadata.yaml`
- `workspace/`
- `evaluation/`

The harness validates those files before running in non-mock mode.

Recommended validation command:

```bash
python scripts/validate_task_assets.py --manifest tasks/manifests/frozen_task_slice_v3.yaml
```

Probe suite manifests:

- `tasks/manifests/substitution_probe_suite_v1.yaml`
- `tasks/manifests/compression_probe_suite_v1.yaml`
- `tasks/manifests/reset_probe_suite_v1.yaml`
