# Audit Response Plan

## Immediate safety fixes

- remove the real `.env` from the working tree
- clean disposable local/runtime artifacts where safe
- tighten `.gitignore`
- add a security incident response note

## Scientific honesty and scope

- tighten README and result summaries around simulator-exact vs world-exact
- add explicit scope and interpretation notes
- preserve mixed and negative results, especially for `C5` and local structured-output fragility

## Reproducibility and inspectability

- add repo map, artifact manifest, reproducibility checklist, and current-status page
- add a simple entry point for smoke tests, aggregation, and figure generation
- add a public-safety check script

## Layer B value upgrade

- add at least one more mechanistic bundled micro-task family
- document bundled task design and proxy scope
- strengthen malformed-output accounting and analysis summaries

## Verification

- add lightweight tests for safety checks, report labeling, malformed-output accounting, and summary generation
- rerun lightweight validation (`pytest`, asset validation, design checks, public-safety scan)
