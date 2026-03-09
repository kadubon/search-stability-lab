# Layer B Upgrade Plan

## Scope

This plan upgrades Layer B only. Layer A remains the main exact mechanism-validation layer.

## Planned changes

1. Add explicit Layer B probe blocks for substitution, compression, and reset under fixed backbones.
2. Split bundled tasks into suite manifests and document probe purpose, target hypotheses, and primary proxy metrics.
3. Refine bundled task metadata so compression and reset probes expose more informative proxy variation.
4. Add a clearer proxy-construction layer that separates task-authored metadata, derived proxy features, and runtime state proxies.
5. Improve the local adapter with bounded JSON repair and explicit logging of repaired versus unrecoverable outputs.
6. Add Layer B-focused analysis outputs, including controller comparisons, proxy summaries, and structured-output fragility summaries.
7. Add lightweight tests for the new manifests, proxy labeling, repair logic, and Layer B summary generation.

## Guardrails

- Do not treat bundled tasks as broad benchmark validation.
- Do not blur simulator-exact and task-harness proxy quantities.
- Preserve mixed and negative Layer B findings.
- Keep compute low and bundled assets fully local.
