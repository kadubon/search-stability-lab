# EXPERIMENT_SPEC.md

# Search Stability under Finite Context
## Experiment Specification for Reproducible, Low-Resource Validation

Version: 1.0  
Status: Implementation-ready  
Primary artifact type: Markdown specification for coding agents and human researchers  
Intended implementer: Codex or equivalent coding agent  
Primary language: English  

---

## 0. Purpose

This document specifies a reproducible experimental program for testing the empirical relevance of the theory introduced in:

**Takahashi, K. (2026). _Search Stability under Finite Context: A Minimal Theory of Adequacy Preservation, Compression, and Reset in Long-Running Agents_. Zenodo. https://doi.org/10.5281/zenodo.18905242**

The implementation MUST test the theory **scientifically and honestly** under modest compute.

The implementation MUST NOT claim to “prove the theory” empirically.

The implementation MUST instead test whether the theory’s **predicted failure modes, threshold behavior, and controller interventions** appear in:

1. a controlled simulator, where theory-level latent variables are known by construction; and
2. a lightweight real-task setting, where only operational proxies are observable.

This specification is designed for:

- one fixed Gemini API backbone model;
- one lightweight local CPU-runnable LLM baseline;
- full trace logging;
- reproducible evaluation;
- explicit separation of exact quantities vs proxies;
- publication-grade scientific honesty.

---

## 1. Non-negotiable scientific principles

The implementation MUST satisfy all of the following.

### 1.1 Fixed-backbone principle
Within a comparison block, the base model MUST remain fixed.

Interpretation:
- if comparing controller laws, do not change the backbone model;
- changing the model creates a separate experimental series.

### 1.2 Exact-vs-proxy separation
The codebase MUST distinguish:
- **exact theory-level quantities** available only in the simulator;
- **operational proxies** available in real tasks.

The analysis MUST NEVER present a proxy as if it were an exact latent variable.

### 1.3 Predeclared hypotheses
All primary hypotheses and contrasts MUST be declared before running the main evaluation.

### 1.4 Negative-result policy
The implementation and report MUST preserve negative results.

The project MUST NOT hide conditions in which:
- greedy controllers perform competitively;
- reserve-aware or reset-aware controllers fail;
- compression control gives no benefit;
- theory-guided interventions matter little.

### 1.5 Full trace reproducibility
Every run MUST be reproducible from:
- config,
- seed,
- backbone model ID,
- controller ID,
- task ID or simulator episode seed,
- code revision,
- prompt version.

### 1.6 Scope honesty
The final report MUST interpret results as support or non-support for **empirical relevance** under the tested regime.

The final report MUST NOT claim universal validation.

---

## 2. Research question

### 2.1 Main question
Do long-horizon agent outcomes depend materially on finite-context controller laws governing:
- candidate retention,
- family diversity preservation,
- compression,
- retirement,
- branching,
- and reset,

when backbone model quality is held fixed?

### 2.2 Secondary question
Can these effects be observed with modest compute, using:
- a controlled CPU-feasible simulator; and
- a small real-task slice evaluated with one Gemini API model and one local CPU baseline model?

---

## 3. Claims under test

The implementation MUST operationalize the following empirical claims.

### H1. Budget-threshold hypothesis
As active-context budget decreases, success eventually drops sharply because recoverability of at least one adequate family collapses.

### H2. Substitution-first hypothesis
Within-family substitution before cross-family deletion preserves success better than greedy deletion under matched or lower context cost.

### H3. Compression-alias hypothesis
Lossy compression can merge decision-relevantly different states into the same compressed representation, producing persistent downstream loss.

### H4. Lag-amplification hypothesis
The harmful effect of compression aliasing increases as strong verification is delayed.

### H5. Reset-rationality hypothesis
In stale-legacy conditions, reset-aware control can outperform continuation after accounting for reset cost.

### H6. Controller-not-model hypothesis
These effects remain visible when the backbone model is held fixed and only the controller law changes.

---

## 4. Overall experimental architecture

The project MUST have two evaluation layers.

### Layer A: Controlled simulator
Purpose:
- exact theory-aligned measurement;
- direct test of threshold, alias, reserve, retirement, and reset effects.

Properties:
- latent adequate-family structure known by construction;
- exact failure-channel attribution available;
- CPU-first implementation.

### Layer B: Lightweight real-task evaluation
Purpose:
- limited external-validity check;
- same controller laws tested in real delayed-feedback tasks.

Properties:
- exact latent adequacy unknown;
- only proxies available;
- small fixed task slice;
- no leaderboard ambition.

Layer A is primary. Layer B is supportive.

---

## 5. Model stack

## 5.1 Backbone A: Gemini API model
Use one fixed Gemini API model as the main backbone.

The repository MUST centralize all Gemini settings in one config file.

The following MUST be recorded:
- exact model ID;
- SDK version;
- endpoint family;
- temperature;
- top_p if used;
- max output tokens;
- tool-calling mode;
- structured-output mode;
- retry policy;
- timeout policy.

The exact model ID MUST be frozen before main runs.

## 5.2 Backbone B: local CPU LLM
Use one small local LLM as a lightweight robustness baseline.

Recommended target class:
- Gemma 3 1B quantized; or
- Gemma 3n E2B/E4B quantized.

The local model MUST be runnable on CPU via one of:
- llama.cpp server;
- Ollama.

The local model is not expected to match Gemini capability.
Its role is to test whether controller-law effects remain directionally visible under a weaker backbone.

## 5.3 Unified model adapter
The codebase MUST expose both models behind the same abstract interface.

Required methods:
- `plan_step(context) -> structured decision`
- `compress_state(context) -> structured compression result`
- `diagnose_failure(trace) -> structured attribution`
- `choose_continue_branch_reset(context) -> structured decision`

All methods MUST support schema-constrained JSON output.

---

## 6. Controlled simulator specification

## 6.1 Simulator purpose
The simulator is not meant to imitate a public benchmark in detail.
It is meant to instantiate the paper’s causal structure with enough fidelity to test the theory’s central predictions.

## 6.2 State objects
Each episode MUST include the following latent and observable objects.

### Latent objects
- finite family set `F = {F_1, ..., F_K}`;
- nonempty adequate-family set `V ⊆ F`;
- hidden environment parameters;
- family-specific dynamics and rewards;
- strong verification trigger(s).

### Observable objects
- partial evidence about route quality;
- noisy local scores;
- intermediate checks;
- active context contents;
- compressed summaries if compression has occurred;
- current budget usage;
- step index.

## 6.3 Route-family structure
Each family MUST be represented by one or more route instances.

Each route instance MUST carry at least:
- route ID;
- family ID;
- local promise score;
- retention cost;
- overlap burden;
- staleness;
- inertia;
- compression sensitivity;
- partial evidence vector.

## 6.4 Adequacy semantics in simulator
The simulator MUST implement a hidden adequate-family set `V` that is nonempty by construction.

Episode success MUST be defined as:
- at the first strongly discriminating verification stage, at least one adequate family remains operationally recoverable.

Operational recoverability in the simulator MUST be exact, not proxied.

## 6.5 Budget model
A finite active-context budget `B` MUST be enforced.

The implementation MUST support both:
- hard-cap budget;
- soft budget with penalty.

At minimum, the main experiments MUST use hard-cap budget.

## 6.6 Verification lag
The simulator MUST support delayed strong verification.

There MUST be at least three lag regimes:
- short;
- medium;
- long.

## 6.7 Legacy contamination
The simulator MUST support stale or contaminating legacy context.

Contamination SHOULD affect one or more of:
- routing bias;
- score distortion;
- summary pollution;
- increased cost of continuation;
- resistance to switching families.

## 6.8 Compression mechanism
The simulator MUST implement lossy compression that can map distinct pre-compression states into the same compressed control representation.

Compression MUST have a tunable strength parameter.

The simulator MUST explicitly log whether compression caused aliasing between decision-relevantly distinct states.

## 6.9 Allowed controller actions
At each step, the controller MUST be able to choose among:
- keep;
- retire;
- substitute-within-family;
- compress;
- branch;
- reset;
- request evidence/tool.

Action names MUST be standardized and logged as enumerated values.

## 6.10 Episode termination
An episode ends when one of the following occurs:
- success at verification;
- failure at verification;
- budget collapse;
- no recoverable route remains;
- step limit reached.

---

## 7. Controller families

The codebase MUST implement the following controller families.

### C0. Greedy single-route controller
Retains the currently highest-scoring route or smallest top subset.

### C1. Greedy summarize controller
Aggressively compresses history and retains compact summaries.

### C2. Reserve-aware controller
Preserves a minimum family-diversity reserve under budget pressure.

### C3. Substitution-first controller
Prefers within-family substitution before deleting a route from another family.

### C4. Reset-aware controller
Approximates continue/branch/reset values and resets when reset is predicted to dominate.

### C5. Full theory controller
Combines:
- reserve awareness,
- substitution-first rule,
- compression caution,
- reset awareness.

### C6. Random budget-matched controller
Randomized keep/retire/compress control under matched average budget usage.

All controllers MUST be implemented under the same adapter contract.

---

## 8. Independent variables

The simulator MUST support the following factors.

### 8.1 Active-context budget
Discrete levels:
- low;
- medium;
- high.

### 8.2 Verification lag
Discrete levels:
- short;
- medium;
- long.

### 8.3 Family overlap burden
Discrete levels:
- low;
- medium;
- high.

### 8.4 Compression strength
Discrete levels:
- none;
- mild;
- strong.

### 8.5 Legacy contamination
Discrete levels:
- low;
- medium;
- high.

### 8.6 Reset cost
Discrete levels:
- low;
- medium;
- high.

### 8.7 Backbone model
Levels:
- Gemini backbone;
- local CPU backbone.

---

## 9. Primary simulator outcomes

The simulator MUST compute the following primary metrics.

1. `final_success_rate`
2. `adequate_family_survival_rate`
3. `recoverable_family_count_at_verification`
4. `family_extinction_rate`

These are primary metrics and MUST appear in the main tables/figures.

---

## 10. Secondary simulator outcomes

The simulator SHOULD compute the following.

1. `active_set_size_over_time`
2. `represented_family_count_over_time`
3. `compression_alias_collision_count`
4. `post_compression_action_disagreement_rate`
5. `avoidable_retirement_count`
6. `reset_frequency`
7. `post_reset_improvement_rate`
8. `branch_usefulness_rate`
9. `cost_normalized_success`

---

## 11. Exact failure-channel attribution in simulator

The simulator MUST assign one exact failure channel to every failed episode.

Allowed labels:
- `missed_adequate_family`
- `compression_alias`
- `avoidable_retirement`
- `stale_legacy_continuation`
- `raw_model_failure`
- `mixed_failure`

Attribution rules MUST be deterministic and documented.

If multiple channels apply, use:
- a dominant-channel rule; and
- an optional multi-label auxiliary field.

---

## 12. Lightweight real-task layer

## 12.1 Purpose
Layer B exists only to test whether controller-law effects appear in small real tasks.

It MUST NOT be framed as a leaderboard effort.

## 12.2 Default task family
Use a small fixed subset of SWE-Bench Lite, unless the implementer explicitly switches to another task family in a separately labeled config.

## 12.3 Default task count
Target:
- 20 to 30 tasks.

## 12.4 Task selection rules
Tasks MUST be frozen before the first main run.

Selection rules:
- local evaluation reproducible;
- self-contained enough for small-scale study;
- balanced if possible across repositories;
- no post hoc task removal except for clearly documented environment breakage.

## 12.5 Fixed evaluation conditions
For a given comparison block, keep fixed:
- backbone model;
- max turns;
- token budget;
- tool permissions;
- timeout;
- prompt template;
- temperature.

Only the controller law should vary.

## 12.6 Layer B outcomes
### Primary
- `resolved`

### Secondary
- `time_to_first_plausible_patch`
- `time_to_first_test_passing_patch`
- `candidate_branch_count`
- `reset_count`
- `compression_count`
- `retired_branch_count`
- `patch_revision_count`

## 12.7 Proxy diagnostics
Since latent adequate-family truth is unavailable, Layer B MUST log proxies instead.

Required proxy fields:
- `represented_candidate_family_count_proxy`
- `recoverable_candidate_count_proxy`
- `compression_collision_proxy`
- `avoidable_retirement_proxy`
- `reset_helpfulness_proxy`

The repository SHOULD support optional human audit of a stratified subset of failed runs.

---

## 13. Exact-vs-proxy table

The repository MUST include a machine-readable table mapping every metric to one of:
- `exact_theory_quantity`
- `proxy`
- `task_outcome`
- `diagnostic_annotation`

Suggested file:
- `docs/metric_registry.csv`

Minimum columns:
- `metric_name`
- `metric_class`
- `layer`
- `definition_short`
- `used_in_primary_analysis`

---

## 14. Structured output contract

All model decisions MUST be returned in schema-constrained JSON.

The implementation MUST reject malformed outputs and either:
- retry with the same prompt; or
- emit a structured failure event.

## 14.1 Step decision schema
Suggested required fields:

```json
{
  "step_id": "string",
  "decision_type": "keep|retire|substitute|compress|branch|reset|tool",
  "target_ids": ["string"],
  "family_ids": ["string"],
  "confidence": 0.0,
  "rationale_short": "string",
  "predicted_risk": {
    "adequacy_loss": 0.0,
    "alias_risk": 0.0,
    "staleness_risk": 0.0
  },
  "estimated_budget_after": 0.0
}
```

## 14.2 Compression schema

```json
{
  "compression_id": "string",
  "source_route_ids": ["string"],
  "source_family_ids": ["string"],
  "summary_text": "string",
  "summary_state": {
    "open_questions": ["string"],
    "assumptions": ["string"],
    "critical_discriminators": ["string"]
  },
  "estimated_information_loss": 0.0
}
```

## 14.3 Continue/branch/reset schema

```json
{
  "decision": "continue|branch|reset",
  "estimated_continue_value": 0.0,
  "estimated_branch_value": 0.0,
  "estimated_reset_value": 0.0,
  "estimated_reset_cost": 0.0,
  "justification_short": "string"
}
```

## 14.4 Failure attribution schema

```json
{
  "run_id": "string",
  "success": true,
  "failure_channel": "miss|alias|retirement|legacy|raw_model|mixed",
  "confidence": 0.0,
  "notes": "string"
}
```

---

## 15. Logging requirements

All runs MUST be logged as JSONL.

One line MUST correspond to one event.

The codebase MUST support reconstruction of the full trajectory from logs alone.

## 15.1 Required common fields
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
- `compression_event`
- `retirement_event`
- `reset_event`
- `tool_calls`
- `verification_signal`
- `success_final`
- `prompt_version`
- `code_revision`

## 15.2 Layer A exact fields
- `adequate_family_ids_true`
- `recoverable_family_ids_true`
- `failure_channel_true`
- `alias_event_true`
- `avoidable_retirement_true`

## 15.3 Layer B proxy fields
- `failure_channel_proxy`
- `human_audit_label`
- `proxy_confidence`

---

## 16. Prompting policy

The codebase MUST version prompts.

Suggested location:
- `prompts/`

Required properties:
- prompts MUST be deterministic templates;
- prompts MUST be frozen for each comparison block;
- prompt revisions MUST increment a visible version string;
- the version string MUST be logged in every run.

Prompt tuning on evaluation tasks after inspecting main results is prohibited unless it starts a clearly separate series.

---

## 17. Statistical analysis plan

## 17.1 Main comparisons
At minimum, perform these pairwise controller comparisons per backbone.

- C0 vs C2
- C0 vs C3
- C0 vs C4
- C0 vs C5
- C2 vs C5

## 17.2 Primary tests
Use:
- Wilson intervals for success rates;
- mixed-effects logistic regression for binary success;
- permutation tests when sample size is small.

## 17.3 Suggested regression form
Primary binary outcome model:
- outcome: success
- fixed effects:
  - controller
  - budget
  - lag
  - compression
  - contamination
  - backbone
- random effects:
  - episode seed for Layer A;
  - task ID for Layer B.

## 17.4 Time-to-event analysis
For real tasks, optionally compute:
- time to first plausible patch;
- time to first passing patch.

Use survival-style plots if sample size permits.

## 17.5 Multiple testing policy
Primary hypotheses do not require aggressive multiplicity adjustment beyond clear preregistration.
Secondary analyses SHOULD use false-discovery-rate control.

---

## 18. Minimum experimental grid

## 18.1 Pilot grid
The codebase MUST support a small pilot mode.

Recommended pilot:
- 20 simulator conditions × 50 episodes each;
- 1 backbone model first;
- then replicate a reduced grid with the second backbone.

## 18.2 Main simulator grid
Recommended main grid:
- 8 to 12 key conditions;
- 300 episodes per condition if feasible.

## 18.3 Real-task grid
Recommended Layer B grid:
- 20 to 30 tasks;
- 3 controller families minimum;
- 1 to 2 runs per task/controller pair for initial paper.

---

## 19. Acceptance criteria for the repository

The repository is implementation-complete only if all of the following exist.

### 19.1 Required files
- `EXPERIMENT_SPEC.md`
- `README.md`
- `configs/`
- `prompts/`
- `schemas/`
- `simulator/`
- `controllers/`
- `models/`
- `analysis/`
- `logging/`
- `docs/metric_registry.csv`
- `scripts/run_simulator.py`
- `scripts/run_real_tasks.py`
- `scripts/analyze_results.py`

### 19.2 Required capabilities
- run Layer A end-to-end;
- run Layer B on a fixed small task slice;
- produce JSONL logs;
- produce summary tables;
- produce at least 4 publication-ready figures;
- reproduce a run from seed + config.

### 19.3 Required figures
At minimum:
1. success vs budget by controller;
2. success vs compression strength under multiple lag settings;
3. reset benefit vs legacy contamination and reset cost;
4. failure-channel composition by controller.

---

## 20. Figure and table requirements

The report generator MUST output tables/figures with transparent labels.

Every figure legend MUST specify:
- layer;
- backbone model;
- controller family;
- whether the quantity is exact or proxy.

Every summary table MUST include:
- sample count;
- mean or rate;
- interval estimate;
- compute cost summary if available.

---

## 21. Implementation details Codex must follow

## 21.1 Language and toolchain
Preferred:
- Python 3.11+
- pandas
- numpy
- scipy
- statsmodels
- matplotlib
- pydantic or dataclasses
- JSON Schema validation
- Docker support for Layer B

## 21.2 Configuration
All experiment settings MUST be specified in YAML.

Suggested layout:
- `configs/models/*.yaml`
- `configs/controllers/*.yaml`
- `configs/experiments/*.yaml`

## 21.3 Determinism
Where randomness is used, seeds MUST be explicit and logged.

## 21.4 Failure handling
Malformed model outputs MUST be handled explicitly.

Allowed behaviors:
- schema retry;
- bounded retry count;
- structured abort event.

Silent failure is prohibited.

## 21.5 Cost accounting
The implementation SHOULD log:
- wall-clock time;
- token counts if available;
- API cost estimate if available.

---

## 22. Real-task controller instrumentation

For Layer B, controller instrumentation MUST preserve the theory’s core objects as far as possible.

Each run SHOULD maintain explicit internal records of:
- candidate branches;
- branch-to-family clustering proxy;
- summarized context blocks;
- retired branches;
- reopen events;
- reset events.

### 22.1 Family proxy construction
Because exact family structure is unavailable, the codebase MUST define a deterministic branch-family proxy rule.

Suggested proxy options:
- shared issue hypothesis label;
- shared file cluster;
- shared root-cause hypothesis string;
- shared patch-intent category.

The selected proxy rule MUST be documented and fixed before main runs.

---

## 23. Human audit protocol

The repository SHOULD support optional human audit.

Recommended scope:
- audit 30 to 50 failed Layer B runs.

Each audited run SHOULD receive:
- one dominant failure-channel label;
- optional secondary label;
- short free-text note.

Audit labels MUST be stored separately from model-produced diagnostics.

---

## 24. Interpretation rules

The final report MUST follow these interpretation constraints.

### 24.1 Strongest defensible claim
A defensible conclusion is:

> Under fixed backbone models, controller laws motivated by search-stability theory materially affect long-horizon success, especially in bounded-context and delayed-verification regimes.

### 24.2 Forbidden overclaim
The final report MUST NOT claim:

> The theory is universally validated for all agents and all long-horizon tasks.

### 24.3 Simulator vs real-task language
If Layer A succeeds and Layer B is mixed, the report MUST say that:
- the theory is strongly supported in controlled conditions;
- external validity remains partial or task-dependent.

If Layer B shows effects but Layer A does not, this is a specification problem and MUST trigger review before publication.

---

## 25. Recommended repository layout

```text
.
├── EXPERIMENT_SPEC.md
├── README.md
├── configs/
│   ├── controllers/
│   ├── experiments/
│   └── models/
├── prompts/
├── schemas/
├── simulator/
├── controllers/
├── models/
├── logging/
├── analysis/
├── tasks/
│   └── swe_bench_lite_slice/
├── scripts/
│   ├── run_simulator.py
│   ├── run_real_tasks.py
│   └── analyze_results.py
└── docs/
    └── metric_registry.csv
```

---

## 26. Minimal milestone plan

### Milestone 1
Implement simulator, controller interface, schemas, and logging.

Success condition:
- one full simulator episode runs and logs correctly.

### Milestone 2
Implement all controller families and pilot grid.

Success condition:
- pilot simulator results generated and plotted.

### Milestone 3
Implement Layer B runner on fixed small task slice.

Success condition:
- at least one controller runs end-to-end on all selected tasks.

### Milestone 4
Run main experiments and analysis.

Success condition:
- all primary tables and figures generated reproducibly.

---

## 27. Machine-readable deliverables Codex should generate

Codex SHOULD create at least the following additional files.

### 27.1 `docs/metric_registry.csv`
Columns:
- `metric_name`
- `metric_class`
- `layer`
- `definition_short`
- `primary_or_secondary`

### 27.2 `schemas/*.json`
Separate JSON schema files for:
- step decision;
- compression output;
- continue/branch/reset decision;
- failure attribution.

### 27.3 `configs/experiments/pilot.yaml`
A ready-to-run pilot config.

### 27.4 `configs/experiments/main.yaml`
A main simulator config.

### 27.5 `configs/experiments/real_tasks.yaml`
A small Layer B config.

---

## 28. Final instruction to implementer

Implement the project so that a reviewer can answer all of the following from the repository alone:

1. What exact hypotheses were tested?  
2. Which quantities are exact and which are proxies?  
3. Which controller changed, and which model stayed fixed?  
4. Can the experiment be rerun from config and seed?  
5. Are the failure cases visible?  
6. Are the conclusions narrower than the data?  

If the answer to any of these is “no,” the implementation is incomplete.

