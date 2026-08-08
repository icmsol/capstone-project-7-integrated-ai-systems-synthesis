# P2-05 — Prior-Project Traceability Matrix (P6-02 Reconciled)

> **Current-state reconciliation.** The 39-row P2-05 table remains below as design-time traceability evidence. Any `(planned)` or `(future)` destination is historical design intent, not the final repository path.

## Final Implementation Mapping

| Prior project | Final Project 7 use | Current implementation/evidence |
|---|---|---|
| Project 1 | Adapted intake/normalization/provenance concepts; hard-coded ICM screening replaced | `src/project7/opportunity_intake.py`; `config/schemas/opportunity_record.schema.json`; `config/profiles/` |
| Project 2 | Runtime historical context and configurable alignment | `data/reference/project2/`; `src/project7/service_alignment.py`; `src/project7/historical_context.py` |
| Project 3 | Evaluation-design evidence only; trained classifier excluded | frozen scenario/evaluation and failure-analysis methodology; no Project 3 runtime model |
| Project 4 | Direct bounded CPU clause-theme runtime contributor | `models/project4/`; `src/project7/clause_triage.py`; `src/project7/p4_03_pipeline.py`; `notebooks/P4_03_Bounded_Clause_Triage_Validation.ipynb` |
| Project 5 | Responsible-AI/corpus-governance evidence only; generator excluded | no generator runtime; lessons reflected in evidence sufficiency and accepted-limitations documentation |
| Project 6 | Governance/evidence/audit/human-authority patterns adapted into runtime | `config/contracts/`; `config/system/`; `src/project7/evidence_retrieval.py`; `src/project7/evidence_workflow.py`; `src/project7/audit_utils.py`; `src/project7/human_disposition.py` |

Projects **1, 2, 4, and 6** contribute runtime assets/methods. Projects **3 and 5** remain bounded design/evaluation evidence.

## Original P2-05 Detailed Traceability Record

## Approved Portfolio Integration Decision

Projects **1, 2, 4, and 6** are runtime contributors. Projects **3 and 5** are bounded design and evaluation evidence unless an asset is separately justified. The matrix makes each retain, adapt, reference, replace, and exclude decision explicit.

## Coverage Summary

- Traceability entries: **39**
- Prior projects covered: **6 of 6**
- Runtime contributor projects: **1, 2, 4, and 6**
- Bounded evidence projects: **3 and 5**

| Project | Entries | Project 7 Decision |
|---|---:|---|
| Project 1 | 5 | Adapt normalization, deadline, and deterministic-key lessons; replace the hard-coded ICM screen and use Project 2 as the stronger structured-data runtime foundation. |
| Project 2 | 8 | Primary structured-data runtime contributor: multi-source normalization, frozen historical assets, transparent classification, descriptive context, and staffing families. |
| Project 3 | 4 | Bounded design and evaluation evidence only. Reuse leakage controls, controlled model comparison, and grouped-split evaluation; exclude the trained classifier. |
| Project 4 | 7 | Direct runtime contributor through the exported CPU inference package, strictly limited to clause-theme triage and human reviewer routing. |
| Project 5 | 5 | Bounded design and evaluation evidence only. Reuse official-corpus governance and hallucination findings; exclude the causal generation checkpoint and generated contract language. |
| Project 6 | 10 | Primary governance and agentic-runtime foundation: contracts, state, reason codes, safeguards, retrieval design, audit, escalation, human authority, and scenario seeds. Rebuild rather than falsely recover the missing or checksum-divergent corpus. |

## Reuse Classification Summary

| Classification | Entries |
|---|---:|
| Executable reuse | 7 |
| Adapted runtime reuse | 14 |
| Design evidence | 6 |
| Evaluation evidence | 6 |
| Superseded/replaced | 2 |
| Excluded from runtime | 4 |

## Detailed Traceability

| ID | Prior project asset or method | Classification | Project 7 target or use | Decision |
|---|---|---|---|---|
| `TR-P1-01` | Project 1: [data_workflow.ipynb — reusable column and text standardization functions](https://github.com/icmsol/ai-programming-foundations-project/blob/main/data_workflow.ipynb) | Adapted runtime reuse | `src/intake/normalization.py (planned)` — Provide the initial reusable normalization patterns behind a source-adapter interface. | **adapt** |
| `TR-P1-02` | Project 1: [data_workflow.ipynb — deadline parsing and original-value retention](https://github.com/icmsol/ai-programming-foundations-project/blob/main/data_workflow.ipynb) | Adapted runtime reuse | `src/intake/normalization.py and opportunity_record.schema.json` — Preserve source values while creating normalized date-time fields and explicit parse limitations. | **adapt** |
| `TR-P1-03` | Project 1: [data_workflow.ipynb — composite record-key approach](https://github.com/icmsol/ai-programming-foundations-project/blob/main/data_workflow.ipynb) | Adapted runtime reuse | `src/intake/identity.py (planned)` — Generate deterministic record keys from source identity and stable normalized fields. | **adapt** |
| `TR-P1-04` | Project 1: [data/processed/caleprocure_bids_combined.csv](https://github.com/icmsol/ai-programming-foundations-project/blob/main/data/processed/caleprocure_bids_combined.csv) | Design evidence | `docs/Project_1_2_Reusable_Asset_Review.md` — Demonstrate the evolution from a single-source opportunity workflow to the Project 2 multi-source foundation. | **reference** |
| `TR-P1-05` | Project 1: [Hard-coded ICM opportunity-screening rules in data_workflow.ipynb](https://github.com/icmsol/ai-programming-foundations-project/blob/main/data_workflow.ipynb) | Superseded/replaced | `config/profiles/* plus service_alignment_engine.contract.json` — Replace hard-coded screening with organization-configurable services, exclusions, reason codes, and safeguards. | **replace** |
| `TR-P2-01` | Project 2: [analysis.ipynb — multi-source field standardization](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/analysis.ipynb) | Adapted runtime reuse | `src/intake/source_adapters/ and src/intake/normalization.py (planned)` — Provide the primary structured-data ingestion foundation for multiple public procurement sources. | **adapt** |
| `TR-P2-02` | Project 2: [data/processed/analysis_summary.json](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/data/processed/analysis_summary.json) | Executable reuse | `data/reference/project2/analysis_summary.json (planned frozen copy)` — Supply checksum-verified descriptive historical context and provenance. | **retain** |
| `TR-P2-03` | Project 2: [data/processed/data_dictionary.csv](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/data/processed/data_dictionary.csv) | Executable reuse | `data/reference/project2/data_dictionary.csv (planned frozen copy)` — Support field interpretation, mapping validation, and reviewer traceability. | **retain** |
| `TR-P2-04` | Project 2: [data/processed/classification_audit_sample.csv](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/data/processed/classification_audit_sample.csv) | Executable reuse | `data/reference/project2/classification_audit_sample.csv (planned frozen copy)` — Supply regression examples and transparent rule-audit evidence for the adapted alignment engine. | **retain** |
| `TR-P2-05` | Project 2: [data/processed/icm_relevant_historical_bids.csv](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/data/processed/icm_relevant_historical_bids.csv) | Adapted runtime reuse | `data/reference/project2/icm_relevant_historical_bids.csv (planned frozen copy)` — Provide descriptive service-category and staffing-family context for representative scenarios. | **adapt** |
| `TR-P2-06` | Project 2: [Deterministic service-category and staffing-demand-family classification](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/analysis.ipynb) | Adapted runtime reuse | `src/analysis/service_alignment.py and src/analysis/historical_context.py (planned)` — Seed the transparent alignment and staffing-family logic under organization-specific configuration. | **adapt** |
| `TR-P2-07` | Project 2: [Five-year fiscal-period normalization and descriptive statistics](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/analysis.ipynb) | Adapted runtime reuse | `src/analysis/historical_context.py (planned)` — Attach bounded source-period, service-category, and staffing-family counts to an opportunity case. | **adapt** |
| `TR-P2-08` | Project 2: [Chi-square test and Cramér's V result](https://github.com/icmsol/Capstone-project-2-statistical-analysis/blob/main/Statistical_Analysis_Report.pdf) | Evaluation evidence | `reports/Integrated_AI_Systems_Synthesis_Report.pdf (future)` — Demonstrate prior statistical rigor and explain why quarter-specific staffing recommendations are unsupported. | **reference** |
| `TR-P3-01` | Project 3: [modeling.ipynb — train/validation/test and supplier-grouped robustness design](https://github.com/icmsol/capstone-project-3-applied-machine-learning/blob/main/modeling.ipynb) | Evaluation evidence | `tests/evaluation/ and reports/Integrated_AI_Systems_Synthesis_Report.pdf (future)` — Inform leakage-aware integrated evaluation and separation of tuning from final assessment. | **reference** |
| `TR-P3-02` | Project 3: [Feature-exclusion and leakage-control design](https://github.com/icmsol/capstone-project-3-applied-machine-learning/blob/main/modeling.ipynb) | Design evidence | `docs/Safeguards_and_Fail_Closed_Behavior.md and evaluation design` — Support privacy, leakage, and proxy-feature controls in integrated evaluation. | **reference** |
| `TR-P3-03` | Project 3: [Class-balanced versus standard logistic-regression comparison](https://github.com/icmsol/capstone-project-3-applied-machine-learning/blob/main/modeling.ipynb) | Design evidence | `tests/evaluation/model_and_policy_comparisons.py (future)` — Support controlled configuration comparisons and explicit selection criteria. | **reference** |
| `TR-P3-04` | Project 3: [Final fitted small-business participation classifier](https://github.com/icmsol/capstone-project-3-applied-machine-learning) | Excluded from runtime | `No Project 7 runtime target` — Explicitly excluded because its outcome, features, and business question do not match Project 7. | **exclude** |
| `TR-P4-01` | Project 4: [selected_clause_classifier.pt](https://github.com/icmsol/capstone-project-4-deep-learning-systems) | Executable reuse | `models/project4/selected_clause_classifier.pt` — Provide bounded ten-class clause-theme triage on CPU. | **retain** |
| `TR-P4-02` | Project 4: [token_to_index.json and index_to_token.json](https://github.com/icmsol/capstone-project-4-deep-learning-systems) | Executable reuse | `models/project4/token_to_index.json and models/project4/index_to_token.json` — Reproduce the exact tokenization and input IDs expected by the checkpoint. | **retain** |
| `TR-P4-03` | Project 4: [model_config.json, tokenizer_config.json, and label_id_to_category.json](https://github.com/icmsol/capstone-project-4-deep-learning-systems) | Executable reuse | `models/project4/` — Reconstruct the classifier and interpret output labels deterministically. | **retain** |
| `TR-P4-04` | Project 4: [validation_selection_metrics.json](https://github.com/icmsol/capstone-project-4-deep-learning-systems) | Evaluation evidence | `models/project4/validation_selection_metrics.json` — Document why the baseline dropout 0.10 checkpoint was selected for Project 7. | **reference** |
| `TR-P4-05` | Project 4: [audit/project4_cpu_smoke_test.json and project4_inference_manifest.json](https://github.com/icmsol/capstone-project-4-deep-learning-systems/blob/main/deep_learning.ipynb) | Executable reuse | `audit/project4_cpu_smoke_test.json and audit/project4_inference_manifest.json` — Provide package provenance, checksums, output-shape evidence, and CPU viability. | **retain** |
| `TR-P4-06` | Project 4: [CUAD grouped-split and controlled-dropout experiment](https://github.com/icmsol/capstone-project-4-deep-learning-systems/blob/main/deep_learning.ipynb) | Evaluation evidence | `reports/Integrated_AI_Systems_Synthesis_Report.pdf (future)` — Support the synthesis discussion of model selection, overfitting, and bounded reuse. | **reference** |
| `TR-P4-07` | Project 4: [Project 4 classifier output as legal or procurement authority](https://github.com/icmsol/capstone-project-4-deep-learning-systems) | Excluded from runtime | `No authoritative decision component` — Prevent clause-theme prediction from being treated as legal interpretation or approval. | **exclude** |
| `TR-P5-01` | Project 5: [Official FAR Part 52.2 acquisition and boundary-validation method](https://github.com/icmsol/capstone-project-5-generative-ai-applications/blob/main/generative_ai.ipynb) | Design evidence | `src/evidence/corpus_builder.py and audit/corpus_manifest.json (planned)` — Guide deterministic rebuilding and validation of the Project 7 official evidence corpus. | **adapt** |
| `TR-P5-02` | Project 5: [Complete-clause train/validation/test partitioning](https://github.com/icmsol/capstone-project-5-generative-ai-applications/blob/main/generative_ai.ipynb) | Design evidence | `tests/evaluation/frozen_scenario_split_manifest.json (future)` — Inform case- and source-group separation in integrated evaluation. | **reference** |
| `TR-P5-03` | Project 5: [Controlled generation and decoding comparison](https://github.com/icmsol/capstone-project-5-generative-ai-applications/blob/main/generative_ai.ipynb) | Evaluation evidence | `reports/Integrated_AI_Systems_Synthesis_Report.pdf (future)` — Provide empirical evidence about repetition, corruption, and authoritative-sounding hallucinations. | **reference** |
| `TR-P5-04` | Project 5: [checkpoints/phase5/selected_model_inference.pt](https://github.com/icmsol/capstone-project-5-generative-ai-applications/blob/main/checkpoints/phase5/selected_model_inference.pt) | Excluded from runtime | `No Project 7 runtime target` — Explicitly excluded from the evidence or recommendation workflow. | **exclude** |
| `TR-P5-05` | Project 5: [Generated FAR-style language as proposed contract content](https://github.com/icmsol/capstone-project-5-generative-ai-applications) | Excluded from runtime | `No drafting or clause-generation component` — Prevent the integrated system from drafting authoritative contract language. | **exclude** |
| `TR-P6-01` | Project 6: [config/tool_contracts.json](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/tool_contracts.json) | Adapted runtime reuse | `config/contracts/*.contract.json` — Seed Project 7's 14 machine-validatable component contracts and deterministic tool obligations. | **adapt** |
| `TR-P6-02` | Project 6: [config/state_schema.json](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/state_schema.json) | Adapted runtime reuse | `config/schemas/integrated_case_state.schema.json` — Provide the foundation for the opportunity-to-contract case lifecycle. | **adapt** |
| `TR-P6-03` | Project 6: [config/reason_codes.json](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/reason_codes.json) | Adapted runtime reuse | `config/system/safeguard_reason_codes.json` — Support fixed, auditable explanations across the integrated workflow. | **adapt** |
| `TR-P6-04` | Project 6: [config/safeguard_matrix.md](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/safeguard_matrix.md) | Adapted runtime reuse | `config/system/safeguard_policy.json and docs/P2_04_Risk_Control_Matrix.*` — Provide the starting point for Project 7's fixed cross-domain safeguard policy. | **adapt** |
| `TR-P6-05` | Project 6: [Exact citation lookup and hybrid semantic retrieval design](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/agentic_system.ipynb) | Adapted runtime reuse | `src/evidence/retrieval.py and data/processed/far/ (planned)` — Provide authoritative evidence retrieval with exact-citation precedence. | **adapt** |
| `TR-P6-06` | Project 6: [Fail-closed audit logging and persistent case-state pattern](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/agentic_system.ipynb) | Adapted runtime reuse | `src/governance/audit.py and src/orchestration/workflow.py (planned)` — Provide append-only audit events, valid transitions, reason codes, and workflow termination controls. | **adapt** |
| `TR-P6-07` | Project 6: [Pydantic AI bounded agent orchestration pattern](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/agentic_system.ipynb) | Adapted runtime reuse | `src/orchestration/agent.py (planned optional bounded layer)` — Coordinate evidence requests and structured recommendation assembly without granting external authority. | **adapt** |
| `TR-P6-08` | Project 6: [config/phase7_scenario_matrix.json and phase7 evaluation results](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/phase7_scenario_matrix.json) | Evaluation evidence | `tests/scenarios/project6_seed_scenarios.json (planned)` — Seed the Project 7 integrated scenario suite and preserve prior failure-mode coverage. | **adapt** |
| `TR-P6-09` | Project 6: [Official FAR raw and processed corpus artifacts](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/data/audit/file_manifest.json) | Superseded/replaced | `data/raw/far/ and data/processed/far/ (planned rebuilt corpus)` — Replace unavailable or checksum-divergent artifacts with a new versioned, validated candidate. | **replace** |
| `TR-P6-10` | Project 6: [Agentic AI reports, traceability matrix, reproducibility validation, and closeout evidence](https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/reports/Agentic_AI_Analysis_Report.pdf) | Design evidence | `reports/Integrated_AI_Systems_Synthesis_Report.pdf and final presentation (future)` — Support the synthesis narrative, governance rationale, and honest production-readiness boundary. | **reference** |

## Integrity Rules

- Every prior project has at least one traceability entry.
- Projects 1, 2, 4, and 6 have executable or adapted runtime entries.
- Projects 3 and 5 have no runtime entries.
- Every runtime entry has a named Project 7 destination and validation evidence.
- Every excluded asset has an explicit mismatch, risk, or responsible-use rationale.
- Every row identifies fixed Project 7 safeguards that constrain its reuse.
- Prior performance results are not carried forward as Project 7 results.

## Key Exclusion Decisions

1. The Project 3 classifier is excluded because its target is recorded SB/MB participation, not pursuit fit or contract risk.
2. The Project 5 generator and generated FAR-style text are excluded because the project demonstrated authoritative-sounding hallucinations.
3. Project 4 predictions are excluded from legal or procurement authority and retained only for bounded triage.
4. Project 1 hard-coded ICM screening is replaced by profile configuration.
5. The Project 6 corpus is rebuilt and newly versioned rather than misrepresented as byte-for-byte recovered.

## Validation

Run:

```bash
python tests/validate_prior_project_traceability.py
```

Expected output:

```text
Traceability entries checked: 39
Prior projects covered: 6
Runtime contributor rule: PASS
Bounded evidence rule for Projects 3 and 5: PASS
Runtime target and exclusion integrity: PASS
Invalid traceability matrix: correctly rejected
```
