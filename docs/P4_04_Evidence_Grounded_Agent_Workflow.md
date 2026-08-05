# P4-04 — Evidence-Grounded Agent Workflow

## Status

**Implemented and locally validated.**

P4-04 adapts the Project 6 `plan → act → observe → validate → escalate` pattern into Project 7 as a deterministic, schema-valid evidence workflow. It connects registered evidence retrieval, exact citation handling, bounded semantic discovery, metadata validation, evidence sufficiency, stable reason codes, case-state persistence, human escalation, and append-only audit logging.

## Representative Result

| Request | Validated citation | Evidence score | Status | Route |
|---|---|---:|---|---|
| `REQ-P4-04-AUDIT` | FAR 52.215-2 Audit and Records-Negotiation (Jun 2020) | 1.00 | `escalated` | `qualified_human_review` |
| `REQ-P4-04-ASSIGNMENT` | FAR 52.232-23 Assignment of Claims (May 2014) | 1.00 | `escalated` | `qualified_human_review` |

The case advances to:

```text
escalated
```

with:

- 2 validated evidence items;
- 2 evidence-sufficiency assessments;
- audit events 7 through 9;
- qualified `Contracts or Legal Reviewer` routing; and
- zero external actions.

## Retrieval Rules

1. Exact clause requests use exact lookup only.
2. A missing exact citation is not silently replaced with a semantic candidate.
3. General evidence discovery may use deterministic TF-IDF cosine retrieval.
4. Every accepted item must pass corpus, snapshot, FAC, metadata, and citation checks.
5. Evidence sufficiency must meet the fixed `0.75` threshold.
6. Public-sector consequential use and Project 4 domain shift remain human-review triggers.

## Representative FAR Subset

The package includes a checksum-verified three-record subset:

- FAR 52.215-2 — Audit and Records-Negotiation;
- FAR 52.232-23 — Assignment of Claims; and
- FAR 52.203-3 — Gratuities.

The subset records Acquisition.gov metadata under FAC `2026-01`, effective `2026-03-13`. It is deliberately not represented as the full Project 6 FAR corpus or a live authoritative service.

## Controlled Validation

```text
test_assignment_title_mismatch_does_not_support_claim (tests.test_evidence_workflow.EvidenceWorkflowTests.test_assignment_title_mismatch_does_not_support_claim) ... ok
test_exact_audit_clause_is_validated_and_escalated (tests.test_evidence_workflow.EvidenceWorkflowTests.test_exact_audit_clause_is_validated_and_escalated) ... ok
test_missing_exact_clause_fails_closed_without_semantic_fallback (tests.test_evidence_workflow.EvidenceWorkflowTests.test_missing_exact_clause_fails_closed_without_semantic_fallback) ... ok
test_out_of_scope_authority_request_escalates (tests.test_evidence_workflow.EvidenceWorkflowTests.test_out_of_scope_authority_request_escalates) ... ok
test_prompt_injection_fails_closed_before_retrieval (tests.test_evidence_workflow.EvidenceWorkflowTests.test_prompt_injection_fails_closed_before_retrieval) ... ok
test_replay_is_deterministic (tests.test_evidence_workflow.EvidenceWorkflowTests.test_replay_is_deterministic) ... ok
test_result_is_schema_valid_and_performs_no_external_action (tests.test_evidence_workflow.EvidenceWorkflowTests.test_result_is_schema_valid_and_performs_no_external_action) ... ok
test_semantic_search_finds_audit_record_for_general_query (tests.test_evidence_workflow.EvidenceWorkflowTests.test_semantic_search_finds_audit_record_for_general_query) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.460s

OK
Representative requests executed: 2
Evidence items preserved: 2
Sufficient evidence assessments: 2
Exact citation semantic substitutions: 0
Updated case status: escalated
Audit events added: 3
Audit hash-chain continuation: PASS
Registered corpus and snapshot checksums: PASS
External actions performed: 0
```

The eight tests cover:

- exact supported retrieval;
- title mismatch;
- nonexistent exact citation;
- no exact-to-semantic substitution;
- bounded semantic retrieval;
- prompt injection;
- prohibited authority request;
- schema validity, deterministic replay, audit continuity, and zero external action.

## Project 6 Design Reuse

P4-04 carries forward the following Project 6 principles:

- exact and semantic retrieval remain distinct;
- unsupported citations are never accepted;
- title, version, and source metadata are validated deterministically;
- insufficient or conflicting evidence abstains, escalates, or fails closed;
- sensitive, authority-seeking, and injection-like requests are blocked;
- all consequential outputs require qualified human review;
- tool and routing events are auditable; and
- controlled success does not establish production readiness.

## Official Sources

- https://www.acquisition.gov/far/52.215-2
- https://www.acquisition.gov/far/52.232-23
- https://www.acquisition.gov/far/52.203-3

## Project 6 Source Design

- https://github.com/icmsol/capstone-project-6-agentic-contract-review
- https://raw.githubusercontent.com/icmsol/capstone-project-6-agentic-contract-review/main/config/reason_codes.json
- https://raw.githubusercontent.com/icmsol/capstone-project-6-agentic-contract-review/main/config/tool_contracts.json
- https://raw.githubusercontent.com/icmsol/capstone-project-6-agentic-contract-review/main/docs/RESPONSIBLE_USE.md

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.

The representative subset, deterministic retrieval, and controlled tests do not establish complete FAR coverage, legal correctness, production security, scalability, or unsupervised authority.
