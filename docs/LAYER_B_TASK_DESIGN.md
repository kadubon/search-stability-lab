# Layer B Task Design

## Why bundled tasks exist

The bundled Layer B tasks are lightweight mechanistic probe tasks.

They exist to:

- make proxy mechanics visible
- exercise controller-law contrasts under frozen conditions
- avoid heavyweight benchmark dependencies

They do not exist to prove broad real-world validity.

## Probe suites

- substitution suite
  tasks: `task-001`, `task-005`
  target hypothesis: `H2`
  primary proxies: represented family count, recoverable candidate count, avoidable retirement
- compression suite
  tasks: `task-003`, `task-007`
  target hypotheses: `H3/H4`
  primary proxies: compression collision, represented family count, recoverable candidate count
- reset suite
  tasks: `task-002`, `task-004`, `task-006`, `task-008`
  target hypothesis: `H5`
  primary proxies: reset helpfulness, stale continuation, post-reset resolution improvement

## Current bundled tasks

- `task-001` parser fallback
  probes substitution and avoidable-retirement behavior
  speaks most directly to `H2`
- `task-002` auth refresh
  probes stale continuation versus a resolving family under contamination
  speaks to `H5`, but only through proxies
- `task-003` summary cache
  probes compression-related proxy risk and family preservation
  speaks to `H3/H4`, but only through proxies
- `task-004` checkpoint resume
  probes reset-helpfulness under stale checkpoint contamination
  speaks to `H5`
- `task-005` serializer defaults
  probes same-family substitution and preservation of cheaper adequate branches
  speaks most directly to `H2`
- `task-006` planner reset
  probes stale planner continuation versus a replan family
  speaks to `H5`
- `task-007` digest routing
  probes alias-heavy summary collapse across multiple recoverable branches
  speaks to `H3/H4`
- `task-008` worker reset
  probes reset helpfulness when stale lease continuation dominates
  speaks to `H5`

## Proxy-only quantities

The following Layer B quantities remain proxies:

- `represented_candidate_family_count_proxy`
- `recoverable_candidate_count_proxy`
- `compression_collision_proxy`
- `avoidable_retirement_proxy`
- `reset_helpfulness_proxy`
- `failure_channel_proxy`

## What remains missing

- no latent world-exact adequate-family truth
- no benchmark-scale task diversity
- no broad external benchmark governance
- local structured-output reliability is still imperfect

## Safe interpretation

Read these tasks as transparent mechanistic probes that complement Layer A.
Do not read them as broad external validation.
