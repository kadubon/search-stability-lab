# Scientific Checklist

Use this checklist before treating a run as theory-relevant evidence.

## Design

- Backbone model fixed within the comparison block
- Prompt version fixed within the comparison block
- Controller law is the main manipulated variable
- Seeds explicitly set
- Task slice or simulator grid frozen before main runs

## Measurement

- Layer A exact quantities reported as exact
- Layer B quantities labeled as proxy or task outcome
- Negative results preserved
- Failure channels inspected rather than collapsed away

## Interpretation

- Claims are regime-bounded
- Real-task mock runs are not presented as external-validity evidence
- Controller comparisons do not silently change backbone, budget, or tool settings
- Figures and tables state whether the quantity is exact or proxy

## Repository hygiene

- `.env` not committed
- No API keys in logs, docs, or configs
- No local absolute paths in public docs or manifests
- Run manifests saved with code revision, model ID, controller IDs, and prompt version
