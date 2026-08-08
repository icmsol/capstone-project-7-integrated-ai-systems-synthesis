# Integrated System Architecture — Final Implementation Reconciliation (P6-02)

> **Current-state document.** This file reconciles the original P2-01 architecture with the implementation accepted in `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`. Historical phase records remain preserved separately.

## 1. Architecture Decision

Project 7 implements a **configuration-first, evidence-grounded, human-authority decision-support architecture** for small public-sector consulting businesses.

ICM Solutions is the reference profile. A fictional small-business profile demonstrates configuration portability without Project 4 model retraining or source-code changes.

The final runtime integrates:

- **Project 1:** adapted opportunity-normalization, original-value preservation, and provenance/identity concepts;
- **Project 2:** frozen historical procurement context, configurable service alignment, and staffing-family context;
- **Project 4:** bounded ten-class clause-theme triage on CPU;
- **Project 6:** evidence retrieval/validation, safeguards, reason codes, auditability, escalation, and human-authority patterns.

Projects 3 and 5 remain bounded design/evaluation evidence and are not direct runtime models.

## 2. Reviewer-Facing Entry Point

The intended user entry point is `notebooks/Project_7_Operator_Interface.ipynb`.

The Colab interface exposes seven operator stages:

1. Opportunity Intake
2. Organization Alignment
3. Clause Triage
4. Evidence Review
5. Recommendation & Packet
6. Human Disposition
7. Save / Resume

The first six stages are the six major business/use-case functions. **Save / Resume is a cross-cutting persistence capability, not a seventh autonomous decision function.**

A reviewer is not expected to call internal Python modules or manually copy audit files.

## 3. System Boundary

The framework may:

- accept an approved public or explicitly authorized solicitation file;
- validate source bytes and provenance;
- accept and validate operator-confirmed opportunity metadata;
- load organization-specific services, rules, reviewer roles, staffing mappings, and thresholds;
- screen opportunity text against configured capabilities;
- attach descriptive frozen historical procurement context;
- classify operator-selected solicitation passages using the bounded Project 4 model;
- retrieve and validate records from the registered evidence corpus;
- expose missing information, limitations, conflicts, and mandatory reviewer routing;
- generate a **nonbinding** recommendation and decision-support packet;
- record a separate authorized human disposition;
- export and restore checksum-inventoried case bundles;
- maintain audit and reproducibility evidence.

The framework may not:

- claim complete semantic extraction of the uploaded PDF;
- claim that intake metadata has been independently semantically verified against the entire source;
- claim complete-document clause discovery;
- treat Project 4 confidence as legal or semantic correctness;
- treat evidence retrieval as proof of applicability or sufficiency;
- make or communicate a final bid/no-bid, legal, contractual, staffing, pricing, security, or compliance decision;
- submit a proposal or perform any autonomous external write action;
- claim production readiness.

## 4. Architectural Layers

### 4.1 Operator Interface and Case Workspace

`src/project7/operator_ui.py` provides the Colab/Jupyter interface.

`src/project7/operator_workflow.py` creates a case workspace outside the repository, invokes tested components in sequence, persists stage inputs/outputs/audit files, exports a checksum-inventoried case ZIP, and restores a prior case only after bundle integrity verification.

The operator layer contains presentation/orchestration logic, not independent pursuit or legal decision logic.

### 4.2 Opportunity Intake and Provenance

`src/project7/opportunity_intake.py` validates intake, preserves original values, verifies source checksum, creates deterministic identifiers, initializes case state, and writes audit events.

**Human control:** the operator confirms structured metadata against the solicitation before validating intake.

### 4.3 Configuration and Organization Alignment

Organization-specific behavior is externalized under `config/profiles/`.

`src/project7/profile_loader.py` validates profiles.  
`src/project7/service_alignment.py` performs exclusion-first capability matching.  
`src/project7/historical_context.py` attaches frozen descriptive Project 2 context.

Alignment is **screening evidence only** and does not establish eligibility, capacity, award probability, or final strategic fit.

### 4.4 Bounded Clause-Theme Triage

`src/project7/clause_triage.py` and `src/project7/p4_03_pipeline.py` execute the frozen Project 4 inference package.

The operator supplies selected solicitation passages. Public-sector consequential use activates `MODEL_DOMAIN_SHIFT`. **High confidence does not establish semantic or legal correctness.**

### 4.5 Evidence Review

`src/project7/evidence_retrieval.py` and `src/project7/evidence_workflow.py` use a bounded registered evidence corpus.

The final prototype uses a checksum-governed representative FAR subset. Retrieval and evidence sufficiency are separate controls; a retrieved item is not automatically support.

### 4.6 Recommendation and Packet

`src/project7/recommendation_engine.py` produces controlled nonbinding recommendation outcomes.

`src/project7/decision_support_packet.py` assembles opportunity, alignment, historical context, clause triage, evidence status, unresolved issues, recommendation, reviewer routing, missing information, conditions, disclosures, and audit references.

### 4.7 Human Authority

`src/project7/human_disposition.py` records the authorized human response separately from the system recommendation.

Allowed dispositions are accept, accept with modified conditions, reject, defer pending information, and escalate. The system recommendation remains immutable.

### 4.8 State, Audit, Evaluation, and Persistence

Case state/audit preserve source checksums, configuration versions, safeguard/reason-code versions, model/corpus provenance, stage results, recommendation inputs/outputs, human disposition, and verification evidence.

Audit failure is fail-closed. Case-bundle export/restore preserves runtime state across Colab loss without weakening state or human-authority controls.

## 5. Final End-to-End Flow

1. Upload/stage an approved solicitation.
2. Confirm structured metadata and validate intake/provenance.
3. Load the selected organization profile.
4. Run service alignment and attach historical context.
5. Paste/select relevant solicitation passages.
6. Run bounded clause-theme triage.
7. Generate evidence requests from actual predictions/passages.
8. Retrieve and validate registered evidence.
9. Apply safeguards, evidence sufficiency, and reviewer routing.
10. Produce the nonbinding recommendation.
11. Assemble the decision-support packet.
12. Record an authorized human disposition or escalation.
13. Preserve audit artifacts.
14. Optionally export/restore a checksum-validated case bundle.

## 6. Failure and Escalation Rules

| Condition | Required behavior |
|---|---|
| Invalid/incomplete profile | Reject configuration / fail closed |
| Fixed-safeguard override attempt | Reject and audit |
| Unverified source/provenance | Stop or require review |
| Sensitive/credential material | Block or route to privacy/security review |
| Model package integrity failure | Disable inference / fail closed |
| Low-confidence model result | Abstain / escalate |
| Public-sector consequential model use | Domain-shift warning + qualified review |
| Missing/invalid exact citation | No authoritative claim |
| Evidence below sufficiency threshold | Abstain / escalate |
| Material conflict | Display conflict + specialist review |
| Audit persistence failure | Stop workflow |
| Autonomous external-action request | Deny |
| Human disposition absent | Case cannot become a final organizational decision |

## 7. Deployment Topology

The final capstone prototype uses GitHub, Google Colab/Python 3.12, CPU execution for the frozen Project 4 model, and local/runtime artifacts. The frozen operator workflow requires no external model-provider credential and contains no proposal-submission, email, procurement, deployment, or other external-write connector.

A production implementation would require formal security, privacy, legal, records-management, authentication/authorization, monitoring, operational governance, and change control.

## 8. Architecture Decisions

| ADR | Final decision |
|---|---|
| ADR-01 | Organization portability is configuration-driven. |
| ADR-02 | Deterministic/testable components remain the default. |
| ADR-03 | System recommendation and human disposition remain separate. |
| ADR-04 | Exact citation requests are not silently substituted with semantic matches. |
| ADR-05 | Project 4 is triage only; domain shift requires qualified review. |
| ADR-06 | Audit/provenance are cross-cutting controls. |
| ADR-07 | Autonomous external actions are prohibited. |
| ADR-08 | CPU-first inference is sufficient for the frozen model package. |
| ADR-09 | Invalid configuration, insufficient evidence, and audit failure are fail-closed/abstention boundaries. |
| ADR-10 | Evidence sources are explicitly versioned/checksum-governed. |
| ADR-11 | Intake remains human-confirmed rather than overstating automatic PDF understanding. |
| ADR-12 | Save / Resume is integrity-checked persistence, not a relaxation of controls. |

## 9. Diagrams

P6-02 reconciled all twelve existing diagram sources and PNG/SVG renderings. No structural redraw was required because the six major business functions remain unchanged; Save / Resume is cross-cutting persistence represented by case-state/audit boundaries.

See `docs/P6_02_Diagram_Reconciliation.md`.

## 10. Final Validation State

- 19/19 cases passed
- 262/262 assertions passed
- 0 regression cases
- 0 unresolved critical/major operator-acceptance defects
- 0 autonomous external actions

The accepted technical/evaluation candidate remains `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`.

## Production Boundary

This is a controlled capstone prototype. It does not establish legal sufficiency, procurement authority, security authorization, compliance approval, or production readiness.
