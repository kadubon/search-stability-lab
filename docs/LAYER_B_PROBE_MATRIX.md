# Layer B Probe Matrix

| task_id | suite | intended mechanism | target hypotheses | primary proxies | major confounds | suitable backbones |
| --- | --- | --- | --- | --- | --- | --- |
| `task-001` | substitution | same-family substitution under lure pressure | `H2` | `represented_candidate_family_count_proxy`, `recoverable_candidate_count_proxy`, `avoidable_retirement_proxy` | authored cost gaps, local formatting failures | Gemini, local CPU |
| `task-005` | substitution | preserve cheaper same-family adequate branch | `H2` | `represented_candidate_family_count_proxy`, `recoverable_candidate_count_proxy`, `avoidable_retirement_proxy` | authored cost gaps, bounded turn budget | Gemini, local CPU |
| `task-003` | compression | alias-prone summarization under compression pressure | `H3`, `H4` | `compression_collision_proxy`, `represented_candidate_family_count_proxy`, `recoverable_candidate_count_proxy` | proxy collision is authored, not latent truth | Gemini, local CPU |
| `task-007` | compression | digest-route collapse under summary compression | `H3`, `H4` | `compression_collision_proxy`, `represented_candidate_family_count_proxy`, `recoverable_candidate_count_proxy` | limited task realism, small task size | Gemini, local CPU |
| `task-002` | reset | stale continuation versus auth-refresh recovery | `H5` | `reset_helpfulness_proxy`, `stale_continuation_proxy`, `post_reset_resolution_improvement_proxy` | authored reset bonus, bounded turns | Gemini, local CPU |
| `task-004` | reset | stale checkpoint lineage versus clean resume | `H5` | `reset_helpfulness_proxy`, `stale_continuation_proxy`, `post_reset_resolution_improvement_proxy` | authored contamination regime | Gemini, local CPU |
| `task-006` | reset | stale planner continuation versus replan recovery | `H5` | `reset_helpfulness_proxy`, `stale_continuation_proxy`, `post_reset_resolution_improvement_proxy` | local malformed output can obscure controller effect | Gemini, local CPU |
| `task-008` | reset | stale worker lease versus fresh reset branch | `H5` | `reset_helpfulness_proxy`, `stale_continuation_proxy`, `post_reset_resolution_improvement_proxy` | authored reset bonus, small slice | Gemini, local CPU |

Compression note:

- compression tasks now aim to produce both proxy and task-outcome sensitivity by requiring delayed preservation of multiple resolving routes
- current evidence is still small-scale: outcome-level separation is visible for `C5` versus `C0/C1`, but the suite remains only two authored probe tasks
