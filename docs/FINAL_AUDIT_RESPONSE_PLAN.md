# Final Audit Response Plan

## Scope

This plan responds to the latest release-oriented audit findings without changing Layer A claims.

## Planned work

1. Add a conservative release-clean workflow with a dry-run path and documentation.
2. Split public-safety scanning into development and release modes so release scans include `artifacts/`.
3. Strengthen compression probe task design so outcome-level separation is more likely while staying mechanistic and low-compute.
4. Extend Layer B compression analysis so proxy-level versus outcome-level evidence is stated explicitly.
5. Improve local structured-output handling and classification with clearer repaired-versus-unrecoverable reporting.
6. Update release-facing docs and checklists to reflect the current evidence hierarchy.
7. Add lightweight tests for cleanup, release scans, compression probe summaries, and local repair behavior.

## Guardrails

- Preserve negative and mixed findings.
- Keep Layer B probe-scale and proxy-only.
- Treat Layer A as the main exact mechanism-validation layer.
- Do not delete scientifically meaningful artifacts by default.
