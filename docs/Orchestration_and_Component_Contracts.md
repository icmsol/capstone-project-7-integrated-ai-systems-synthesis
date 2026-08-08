# Orchestration, Configuration, and Component Contracts — Final Reconciliation (P6-02)

> **Current-state document.** The P2-03 design was implemented and extended through operator-interface and acceptance work. The registry contains **14 executable component contracts** plus the registry artifact.

## Component Contract Registry

| Component ID | Final implementation |
|---|---|
| `profile_loader` | `src/project7/profile_loader.py` |
| `case_intake_normalizer` | `src/project7/opportunity_intake.py` |
| `service_alignment_engine` | `src/project7/service_alignment.py` |
| `historical_context_provider` | `src/project7/historical_context.py` |
| `passage_selector` | Operator-selected passage boundary represented by contract/operator workflow |
| `clause_triage_model` | `src/project7/clause_triage.py`; `src/project7/p4_03_pipeline.py` |
| `official_evidence_retriever` | `src/project7/evidence_retrieval.py` |
| `evidence_validator` | `src/project7/evidence_workflow.py` |
| `risk_escalation_router` | Safeguard/reason-code policy plus integrated routing |
| `recommendation_engine` | `src/project7/recommendation_engine.py` |
| `packet_assembler` | `src/project7/decision_support_packet.py`; `src/project7/p4_05_pipeline.py` |
| `human_disposition_recorder` | `src/project7/human_disposition.py` |
| `audit_writer` | `src/project7/audit_utils.py` |
| `workflow_orchestrator` | Stage pipelines plus `src/project7/operator_workflow.py` |

## Final Operator Orchestration

1. Stage/checksum the approved solicitation.
2. Confirm/validate structured opportunity intake.
3. Load/validate the organization profile.
4. Run service alignment and frozen historical context.
5. Accept operator-selected solicitation passages.
6. Execute bounded Project 4 clause-theme inference.
7. Build evidence requests from actual passages/predictions.
8. Retrieve and validate registered evidence.
9. Apply evidence-sufficiency and mandatory escalation controls.
10. Create a nonbinding recommendation or controlled abstention/escalation.
11. Assemble the decision-support packet.
12. Record an authorized human disposition when ready.
13. Persist audit/state artifacts.
14. Export/restore a checksum-inventoried case bundle when needed.

## Configuration Resolution Order

1. fixed framework safeguards;
2. schemas and component contracts;
3. validated organization profile;
4. authorized case-specific business preferences.

A lower layer cannot weaken a higher layer.

## Global Gates

Valid provenance, safeguards, privacy/security boundaries, schema-valid transitions, model/corpus integrity, evidence sufficiency, separate human disposition, audit persistence, and zero autonomous external writes are enforced.

## Operator-Controlled Passage Boundary

The interface does **not** claim automatic whole-document passage extraction. The `passage_selector` contract represents the bounded selection boundary; the operator identifies/pastes passages before triage.

## Fail-Closed, Abstention, and Escalation

Normal processing fails closed for integrity, authorization, schema, audit, or prohibited-action failures.

Analytical components abstain/escalate for insufficient information, low confidence, `MODEL_DOMAIN_SHIFT`, invalid/missing evidence, insufficient evidence, conflicts, or mandatory specialist review.

## Human Authority

The recommendation/packet components produce advisory output only. The human-disposition recorder validates reviewer authorization, stores the response separately, preserves the original recommendation, records rationale/conditions/escalation target, and performs no external action.

## Resumability and Reassessment

**Runtime resume:** an exported bundle may be restored as the same case after manifest/checksum validation.

**Analytical reassessment:** materially new source, configuration, evidence, or business facts should create an explicitly versioned reassessment instead of overwriting the prior evidence/recommendation chain.

## Validation

```text
Component contracts checked: 14
Contract registry integrity: PASS
Orchestration policy: PASS
Stage-to-contract referential integrity: PASS
Invalid component contract: correctly rejected
Invalid orchestration policy: correctly rejected
```

## Production Boundary

These contracts govern a controlled capstone prototype and do not grant production, legal, procurement, security, pricing, staffing, or contractual authority.
