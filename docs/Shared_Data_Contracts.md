# P2-02 — Shared Data Contracts and JSON Schemas

## Purpose

The Project 7 data contracts define explicit, versioned handoffs between opportunity intake, organization configuration, structured analysis, clause triage, official evidence review, recommendation assembly, audit logging, and authorized human disposition.

The schemas use **JSON Schema Draft 2020-12** and reject undeclared fields through `additionalProperties: false` at the principal object boundaries.

## Schema Inventory

| Schema | Primary Producer | Primary Consumer | Purpose |
|---|---|---|---|
| `common_definitions.schema.json` | Framework | All components | Shared versions, IDs, hashes, source references, limitations, and human roles |
| `opportunity_record.schema.json` | Intake and normalization | Alignment, triage, audit | Preserves normalized and original opportunity values with provenance |
| `service_alignment.schema.json` | Alignment engine | Recommendation and packet assembly | Records capability matches, exclusions, score, label, staffing families, and limitations |
| `historical_context.schema.json` | Historical context component | Recommendation and reporting | Supplies descriptive counts and explicitly non-predictive interpretation |
| `clause_prediction.schema.json` | Project 4 inference component | Evidence workflow and reviewer routing | Provides bounded theme, confidence, abstention/escalation, model version, and limitations |
| `evidence_item.schema.json` | Evidence tools | Evidence assessment and recommendation | Stores validated citations, retrieval method, relevance, support/conflict, and freshness |
| `evidence_assessment.schema.json` | Evidence validator | Recommendation engine | Determines sufficiency, conflict, missing information, and required action |
| `recommendation.schema.json` | Recommendation engine | Human review | Defines the complete nonbinding recommendation contract |
| `human_disposition.schema.json` | Authorized human reviewer | Case state and audit | Separates final human judgment from the system recommendation |
| `audit_event.schema.json` | Every component | Audit log and evaluation | Records append-only, sanitized, chained events |
| `integrated_case_state.schema.json` | Orchestrator | All workflow components | Aggregates the complete case lifecycle |

## Core Design Rules

### Versioning

Every principal record contains a semantic schema version. Configuration, model, corpus, and safeguard versions are stored in the integrated case and audit events.

### Provenance

Opportunity and evidence records require source identifiers, source type, location, retrieval timestamp, SHA-256, and an explicit approved-for-use flag.

### Original Values

The normalized opportunity record retains source-provided values in `original_values`; normalization does not destroy the original representation.

### Recommendation Completeness

A recommendation cannot omit:

- nonbinding disclosure;
- strength or confidence;
- supporting evidence;
- counterevidence;
- missing information;
- conditions;
- limitations;
- required human reviewer;
- recommended next action;
- data freshness;
- reason codes;
- audit reference.

`Recommend Pursue with Conditions` requires at least one condition.

### Human Authority

A finalized case requires a separate `human_disposition`. The human record contains the reviewer role, selected disposition, rationale, modified conditions, escalation target when applicable, and decision time.

### Bounded Model Use

The clause-prediction schema stores model identity, package checksum, confidence, decision, reviewer routing, domain warning, truncation, reason codes, and limitations. Classification is not legal interpretation.

### Fail-Closed Errors

The integrated case stores component errors and whether each error caused fail-closed behavior. Audit persistence remains a prerequisite for normal workflow continuation.

### Portability

The integrated case uses organization IDs and configuration versions rather than hard-coded ICM service logic. The same schemas support both the ICM reference profile and the fictional portability profile.

## Validation Examples

The package includes:

- `valid_integrated_case.json`;
- `valid_audit_event.json`;
- `invalid_integrated_case.json`.

The invalid example attempts to mark a case finalized without a human disposition and weakens the recommendation disclosure. It must be rejected.

Run:

```bash
python tests/validate_shared_schemas.py
```

Expected output:

```text
Schemas checked: 11
Valid integrated case: PASS
Valid audit event: PASS
Invalid integrated case: correctly rejected with at least 1 validation error
```

## Production Boundary

These schemas support a controlled capstone prototype. They do not themselves establish legal sufficiency, regulatory compliance, security authorization, production readiness, or authority to make organizational commitments.
