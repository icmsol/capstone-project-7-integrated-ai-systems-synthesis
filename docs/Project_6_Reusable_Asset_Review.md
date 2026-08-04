# P1-04 — Project 6 Agentic Workflow Asset Review

## Decision

Project 6 is the primary runtime-governance foundation for Project 7.

Project 7 will reuse the bounded single-agent design, typed deterministic tools, evidence validation, per-case state, stable reason codes, fail-closed safeguards, audit logging, and representative evaluation structure. The Project 6 notebook will not be copied wholesale. Its reusable implementation will be extracted into tested modules and extended for organization configuration, opportunity analysis, Project 4 clause triage, nonbinding recommendations, counterevidence, conditions, and final human disposition.

## Runtime Assets to Reuse

### Architecture Pattern

- bounded plan-act-observe-validate-escalate workflow;
- single agent with deterministic tools;
- limited per-case memory;
- no cross-case personal memory;
- exact citation lookup before semantic retrieval when an identifier is supplied;
- explicit respond, abstain, fail-closed, or escalate outcomes;
- mandatory human authority for consequential decisions.

### Tool Contracts

- `search_official_corpus`
- `retrieve_exact_clause`
- `validate_clause_metadata`
- `assess_evidence_sufficiency`
- `classify_risk_and_escalation`
- `write_audit_event`

These will become typed Project 7 modules rather than remaining notebook-only functions.

### Case State

The prior state model will be extended with:

- active organization and profile version;
- normalized opportunity record;
- service-alignment evidence;
- historical procurement context;
- Project 4 clause-theme output;
- supporting and counterevidence;
- missing information;
- conditions;
- nonbinding recommendation;
- required human reviewer;
- human acceptance, modification, rejection, deferral, or escalation;
- final human rationale.

### Reason Codes and Safeguards

Existing codes and meanings will be preserved where applicable. Project 7 will add configuration-validation, service-alignment, stale-data, classifier-abstention, recommendation-condition, and human-disposition codes.

The safeguard layer will remain framework-controlled and will include:

- scope and privacy gates;
- approved-source requirement;
- exact citation validation;
- evidence sufficiency;
- conflict detection;
- confidence and abstention;
- prompt-injection handling;
- fail-closed tool behavior;
- audit-write requirement;
- mandatory human review;
- configuration-override rejection;
- nonbinding recommendation disclosure;
- counterevidence and missing-information disclosure;
- Project 4 domain-shift handling;
- no autonomous external action.

## Critical Corpus Gap

The public Project 6 repository does not contain the actual frozen FAR source files or processed retrieval corpus. The `data/raw` and `data/processed` folders contain only README files. The reconstructed closeout manifest states that the original Phase 4 manifest was unavailable and that the FAR Part 52.2 source reference was not found.

During P1-05, the Project 7 notebook will:

1. attempt controlled recovery from the executed Project 6 notebook or checksum-verified archives;
2. validate recovered file names, source metadata, row counts, and checksums;
3. otherwise reacquire the same official source snapshot;
4. record URL, version, effective date, retrieval date, and SHA-256;
5. rebuild the normalized corpus and retrieval index deterministically;
6. run exact-lookup, semantic-search, nonexistent-citation, and tool-failure smoke tests.

The corpus will not be represented as recovered unless the evidence supports that claim.

## Evaluation Reuse

The original 16 scenarios are design evidence, not Project 7 results. Selected cases will seed the new scenario matrix:

- valid exact citation;
- nonexistent citation;
- empty retrieval;
- tool exception;
- out-of-scope authority request;
- prompt injection;
- privacy-sensitive input;
- evidence conflict;
- low confidence;
- mandatory escalation.

Project 7 will add configuration portability, organization mismatch, Project 4 domain shift, recommendation completeness, counterevidence, conditions, and human override cases.

## Planned Project 7 Targets

```text
src/workflow_orchestrator.py
src/evidence_index.py
src/evidence_tools.py
src/risk_routing.py
src/audit.py
src/schemas.py
config/system/agent_runtime.json
config/system/reason_codes.json
config/schemas/integrated_case_state.schema.json
prompts/integrated_system_prompt.txt
data/frozen_scenarios/project7_scenario_matrix.json
audit/p1_05_smoke_test.json
```

## Sources

- https://github.com/icmsol/capstone-project-6-agentic-contract-review
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/agent_architecture.md
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/agent_config.json
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/tool_contracts.json
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/state_schema.json
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/reason_codes.json
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/config/safeguard_matrix.md
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/data/audit/file_manifest.json
- https://github.com/icmsol/capstone-project-6-agentic-contract-review/blob/main/data/audit/phase6_smoke_test_validation.json
