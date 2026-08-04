# P2-03 — Orchestration, Configuration, and Component Contracts

## Purpose

This package converts the approved architecture and shared data schemas into explicit machine-validatable execution contracts. Each component contract specifies:

- required inputs and schemas;
- outputs and downstream consumers;
- configurable and fixed dependencies;
- preconditions and postconditions;
- allowed and prohibited side effects;
- fail-closed, abstention, warning, retry, deferral, and escalation behavior;
- audit events;
- idempotency and retry rules;
- required human checkpoints;
- the non-production boundary.

## Component Contract Registry

| Component ID | Component | Type | Boundary | Human Checkpoint |
|---|---|---|---|---|
| `profile_loader` | Organization Profile Loader and Validator | configuration_loader | hybrid | No |
| `case_intake_normalizer` | Opportunity Intake, Normalization, and Provenance | deterministic_transform | framework_controlled | No |
| `service_alignment_engine` | Configuration-Driven Service Alignment Engine | deterministic_rule_engine | hybrid | No |
| `historical_context_provider` | Frozen Historical Procurement Context Provider | historical_context_provider | framework_controlled | No |
| `passage_selector` | Relevant Passage Selector | deterministic_transform | hybrid | No |
| `clause_triage_model` | Project 4 Clause-Theme Triage | model_inference | framework_controlled | No |
| `official_evidence_retriever` | Official Evidence Retrieval Tool | retrieval_tool | framework_controlled | No |
| `evidence_validator` | Citation, Metadata, Sufficiency, and Conflict Validator | validation_tool | framework_controlled | No |
| `risk_escalation_router` | Risk and Escalation Router | risk_routing | hybrid | No |
| `recommendation_engine` | Evidence-Linked Nonbinding Recommendation Engine | recommendation_engine | hybrid | Yes |
| `packet_assembler` | Decision-Support Packet Assembler | packet_assembler | framework_controlled | Yes |
| `human_disposition_recorder` | Authorized Human Disposition Recorder | human_checkpoint | human_authority | Yes |
| `audit_writer` | Append-Only Audit Event Writer | audit_writer | framework_controlled | No |
| `workflow_orchestrator` | Integrated Case Workflow Orchestrator | stateful_orchestrator | framework_controlled | Yes |

## Orchestration Sequence

1. Load and validate the organization configuration.
2. Create, normalize, and provenance-lock the opportunity case.
3. Assess configured service alignment.
4. Attach frozen historical context when approved and comparable.
5. Select approved passages when text is available.
6. Run bounded Project 4 clause-theme triage when applicable.
7. Retrieve approved official evidence when required.
8. Validate citations, metadata, sufficiency, conflicts, and freshness.
9. Apply fixed mandatory escalation and configured reviewer routing.
10. Create a complete nonbinding recommendation or explicit No Recommendation outcome.
11. Assemble and validate the decision-support packet.
12. Record an authorized human disposition.

## Configuration Resolution Order

Configuration is resolved in descending precedence:

1. fixed framework safeguards;
2. schema and component-contract requirements;
3. validated organization profile;
4. authorized case-specific business preferences.

A lower-precedence layer cannot weaken a higher-precedence requirement. Any conflict is rejected or audited according to the higher-precedence control.

## Global Gates

The orchestration policy requires:

- audit availability before every stage;
- active fixed safeguards before every stage;
- approved source provenance before source processing;
- privacy and security screening before persistence;
- sufficient validated evidence before a directional recommendation;
- authorized human disposition before finalization;
- prohibition of all autonomous external write actions.

## Fail-Closed Boundary

The orchestrator stops normal processing when:

- configuration or contract validation fails;
- an unregistered component is requested;
- a required component violates its contract;
- a state transition is invalid;
- audit persistence fails;
- a prohibited source or external action is requested.

Optional analytical components may abstain or be skipped only when the limitation is explicit and the routing and recommendation stages account for the missing output.

## Resumability

A deferred or escalated case may be reassessed only as a new versioned run. Resumption requires:

- a schema-valid case state;
- a valid audit chain;
- original source checksums;
- preservation of any original recommendation;
- configuration revalidation;
- source-freshness revalidation.

## Concurrency

Different cases may run in parallel. The same case may not execute stages in parallel, and a state lock is required.

## Validation

Run:

```bash
python tests/validate_component_contracts.py
```

Expected output:

```text
Component contracts checked: 14
Contract registry integrity: PASS
Orchestration policy: PASS
Stage-to-contract referential integrity: PASS
Invalid component contract: correctly rejected
Invalid orchestration policy: correctly rejected
```

## Production Boundary

The contracts govern a controlled capstone prototype. They do not grant production authority, legal sufficiency, compliance approval, permission to process restricted data, or authority to execute organizational commitments.
