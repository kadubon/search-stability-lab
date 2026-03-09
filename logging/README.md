# Logging Notes

Runs are logged as JSONL with one event per line.

Common fields are emitted for both layers, including:

- `run_id`
- `episode_id`
- `task_id`
- `seed`
- `layer`
- `backbone_model_id`
- `controller_id`
- `time_step`
- `event_type`
- `budget_used`
- `budget_remaining`
- `active_route_ids`
- `active_family_ids`
- `represented_family_count`
- `decision_type`
- `prompt_version`
- `code_revision`

Layer A also logs exact simulator-only fields, including true adequate-family IDs, recoverable-family IDs, exact failure channel, alias events, and avoidable retirements.

Layer B logs only proxy diagnostics and task outcomes. It does not log hidden adequate-family truth.

