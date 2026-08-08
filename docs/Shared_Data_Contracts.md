# Shared Data Contracts and JSON Schemas — Final Reconciliation (P6-02)

> **Current-state document.** The original P2-02 foundation contained 11 principal runtime schemas. Implementation/evaluation expanded the repository to **34 JSON Schemas**, all validated by the current quality gate.

## Current Schema Inventory — 34

### Core runtime records

- `common_definitions.schema.json`
- `opportunity_record.schema.json`
- `service_alignment.schema.json`
- `historical_context.schema.json`
- `clause_prediction.schema.json`
- `evidence_item.schema.json`
- `evidence_assessment.schema.json`
- `recommendation.schema.json`
- `human_disposition.schema.json`
- `audit_event.schema.json`
- `integrated_case_state.schema.json`
- `decision_support_packet.schema.json`
- `evidence_workflow_request.schema.json`
- `evidence_workflow_result.schema.json`

### Configuration / orchestration / governance

- `organization_profile.schema.json`
- `component_contract.schema.json`
- `orchestration_policy.schema.json`
- `safeguard_policy.schema.json`
- `safeguard_reason_code_registry.schema.json`
- `prior_project_traceability.schema.json`
- `operational_workload.schema.json`
- `scenario_taxonomy.schema.json`

### Scenario / evaluation / freeze evidence

- `expected_case_outcome.schema.json`
- `frozen_case_manifest.schema.json`
- `frozen_evaluation_run_manifest.schema.json`
- `scenario_evaluation_result.schema.json`
- `system_metrics_report.schema.json`
- `failure_analysis_report.schema.json`
- `refined_evaluation_run_manifest.schema.json`
- `portability_test_report.schema.json`
- `final_evaluation_baseline.schema.json`
- `acceptance_corrected_baseline.schema.json`
- `reproducibility_manifest.schema.json`
- `human_disposition_fixture.schema.json`


## Core Rules

- Opportunity/evidence records preserve provenance and original source values.
- Organization-specific behavior is configuration-driven.
- Clause predictions preserve model identity, confidence, domain warning, routing, reason codes, and limitations.
- Evidence retrieval and evidence sufficiency are separate.
- Recommendations preserve nonbinding disclosure, evidence/gaps/conditions, reviewer routing, reason codes, and audit reference.
- Human disposition is a separate authorized record.
- Evaluation/freeze schemas preserve scenario lineage, metrics, failures, refinements, portability, reproducibility, and baseline history.

## Validation

```text
Schemas checked: 34
Valid integrated case: PASS
Valid audit event: PASS
Invalid integrated case: correctly rejected
```

## Production Boundary

Schema conformance is structural validation; it is not legal sufficiency, regulatory compliance, security authorization, production readiness, or organizational decision authority.
