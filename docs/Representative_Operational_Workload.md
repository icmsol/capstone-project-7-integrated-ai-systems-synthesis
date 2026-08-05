# P3-01 — Representative Operational Workload

## Workload

**ICM Public-Sector Opportunity-to-Contract Decision-Support Workload**

The representative unit of work is one approved organization profile applied to one frozen or authorized public-sector opportunity. The automated workflow ends with a complete evidence-grounded packet and nonbinding recommendation. The operational workflow ends only after an authorized human records a separate disposition or the case safely terminates as deferred, escalated, or failed closed.

## Business Purpose

ICM Solutions currently relies on fragmented procurement data, manual service-fit screening, separate historical analysis, human contract review, and individual judgment. The representative workload tests whether these activities can be integrated into one configurable, evidence-grounded, auditable, human-authorized decision-support process without overstating model or source capabilities.

## Primary User Story

As an authorized ICM pursuit lead, I need one evidence-grounded packet that explains opportunity alignment, historical context, clause-review priorities, authoritative evidence, risks, missing information, conditions, and required specialist reviews so that I—not the AI system—can make and justify the final pursuit disposition.

## Workload Boundary

- **Profiles per run:** 1
- **Opportunities per run:** 1
- **Source documents:** up to 3
- **Selected passages:** up to 5
- **Project 4 inference calls:** up to 5
- **Evidence candidates per claim:** up to 5
- **Claims per case:** up to 5
- **Human dispositions:** exactly 1
- **New model training:** no
- **GPU required:** no

The integrated workload can run on a Colab CPU. The already trained Project 4 model is reused for bounded inference; the Project 7 synthesis does not require T4 training.

## Actors

| ID | Actor | Type | Authority Boundary |
|---|---|---|---|
| `ACT-01` | Organization Profile Owner | human operator | May configure permitted business criteria but cannot weaken fixed safeguards, evidence requirements, audit logging, or human final authority. |
| `ACT-02` | Opportunity Analyst | human operator | May correct input and request further analysis but cannot finalize pursuit or contract decisions. |
| `ACT-03` | Business Development or Pursuit Lead | human reviewer | May make an authorized pursuit disposition only within organizational delegation and after mandatory specialist reviews. |
| `ACT-04` | Contract Analyst | human reviewer | May validate analysis and route issues but does not provide final legal authority unless separately qualified and authorized. |
| `ACT-05` | Qualified Specialist | human reviewer | Authority is limited to the specialist's qualified domain and delegated organizational role. |
| `ACT-06` | Executive Authority | human authority | Retains accountable human authority; the system cannot impersonate or replace this role. |
| `ACT-07` | Project 7 Integrated System | system | May analyze, recommend, abstain, defer, and route; may not make a final decision or perform an external action. |
| `ACT-08` | Evaluation and Audit Reviewer | evaluation observer | Observes and assesses the controlled workload but does not alter case outcomes during evaluation. |

## End-to-End Stages

| Seq. | ID | Stage | Component Contract | Human Interaction |
|---:|---|---|---|---|
| 1 | `STG-01` | Load and validate organization configuration | `profile_loader` | optional correction |
| 2 | `STG-02` | Create, normalize, and provenance-lock the opportunity | `case_intake_normalizer` | optional correction |
| 3 | `STG-03` | Assess organization service alignment | `service_alignment_engine` | none |
| 4 | `STG-04` | Attach descriptive historical procurement context | `historical_context_provider` | none |
| 5 | `STG-05` | Select relevant approved passages | `passage_selector` | optional correction |
| 6 | `STG-06` | Run bounded clause-theme triage | `clause_triage_model` | none |
| 7 | `STG-07` | Retrieve approved official evidence | `official_evidence_retriever` | mandatory review |
| 8 | `STG-08` | Validate citations, relevance, sufficiency, and conflict | `evidence_validator` | mandatory review |
| 9 | `STG-09` | Route risk and mandatory escalation | `risk_escalation_router` | mandatory review |
| 10 | `STG-10` | Create complete nonbinding recommendation | `recommendation_engine` | none |
| 11 | `STG-11` | Assemble the decision-support packet | `packet_assembler` | mandatory review |
| 12 | `STG-12` | Record authorized human disposition | `human_disposition_recorder` | mandatory disposition |

## Human Decision Points

| ID | Decision | Stage | Authorized Role |
|---|---|---|---|
| `DP-01` | Approve or correct the organization configuration | `STG-01` | Organization Profile Owner |
| `DP-02` | Approve source use or correct intake | `STG-02` | Opportunity Analyst or Data Reviewer |
| `DP-03` | Confirm passage and contract-review scope | `STG-05` | Opportunity or Contract Analyst |
| `DP-04` | Resolve evidence sufficiency or conflict | `STG-08` | Contract Analyst or Qualified Specialist |
| `DP-05` | Complete mandatory specialist review | `STG-09` | Qualified Specialist |
| `DP-06` | Make the final human pursuit disposition | `STG-12` | Business Development or Pursuit Lead, or Executive Authority |

The system may recommend, abstain, defer, or route. It cannot make or communicate a final organizational decision.

## Required Outputs

The workload produces:

1. validated organization context;
2. normalized opportunity and provenance;
3. service alignment assessment;
4. historical context or explicit limitation;
5. clause-theme triage or not-applicable result;
6. validated evidence inventory;
7. evidence sufficiency and conflict assessment;
8. risk and escalation route;
9. complete nonbinding recommendation;
10. decision-support packet;
11. authorized human disposition;
12. append-only case audit trail.

## Frozen Acceptance Targets

These are **targets**, not measured results. Measured outcomes will be populated only after the scenario suite and integrated implementation execute.

| ID | Category | Measure | Target |
|---|---|---|---|
| `AT-01` | functional | Required workflow stages reached or explicitly skipped under policy | **12 of 12 stages accounted for** |
| `AT-02` | data_quality | Required shared records passing JSON Schema | **100%** |
| `AT-03` | data_quality | Material sources with type, approval basis, checksum, and retrieval time | **100%** |
| `AT-04` | evidence | Material recommendation claims linked to recorded evidence or deterministic rule artifacts | **100%** |
| `AT-05` | evidence | Known material counterevidence disclosed | **100%** |
| `AT-06` | evidence | Invalid or missing exact citations handled safely | **100% abstain or fail closed** |
| `AT-07` | governance | Fixed safeguard override attempts blocked | **100%** |
| `AT-08` | governance | Prohibited external actions performed | **0 occurrences** |
| `AT-09` | governance | Required material state transitions with persisted audit event | **100%** |
| `AT-10` | governance | Secret, restricted, or private-reasoning values persisted | **0 occurrences** |
| `AT-11` | human_authority | Finalized cases with authorized human disposition and rationale | **100%** |
| `AT-12` | human_authority | Mandatory specialist triggers routed to configured qualified role | **100%** |
| `AT-13` | portability | Same executable workflow runs with ICM and fictional organization profiles | **2 profiles with no code change** |
| `AT-14` | performance | Automated single-case elapsed time excluding human wait and model-provider latency | **60 seconds or less on Colab CPU for the bounded workload** |
| `AT-15` | performance | Project 4 CPU inference package load and prediction | **Successful load and finite probability vector** |
| `AT-16` | reproducibility | Frozen workload rerun with identical configuration and source checksums | **Deterministic structured outputs except explicitly nondeterministic model-provider text** |
| `AT-17` | reproducibility | Repository validation scripts passing from a clean environment | **100%** |
| `AT-18` | functional | Complete human-readable decision-support packet | **100% of mandatory packet sections present** |

## Key Constraints

The workload intentionally accounts for:

- incomplete and non-predictive procurement history;
- Project 4 commercial-contract domain shift;
- unavailable or checksum-divergent Project 6 corpus artifacts;
- organization portability without safeguard configurability;
- Colab runtime disconnections;
- the 2,000-word paper limit, with diagrams included in the paper but not counted as prose;
- optional component unavailability;
- public-repository privacy and secret constraints;
- the difference between frozen targets and later measured results.

## Out of Scope

The workload does not perform autonomous external actions, legal advice, compliance certification, award-probability prediction, automatic pricing, staffing commitments, new model training, Project 3 runtime inference, Project 5 contract generation, restricted-data processing, or production deployment.

## Validation

Run:

```bash
python tests/validate_operational_workload.py
```

Expected output:

```text
Actors checked: 8
Approved inputs checked: 8
Workflow stages checked: 12
Human decision points checked: 6
Acceptance targets checked: 18
CPU and no-training boundary: PASS
Stage, actor, and decision integrity: PASS
Invalid operational workload: correctly rejected
```

## Completion Boundary

P3-01 is complete when the workload schema, canonical workload definition, actor and input inventory, 12-stage processing sequence, six human decision points, expected artifact inventory, frozen acceptance targets, constraints, exclusions, validation script, and manifest are committed and pass structural and semantic validation. Measured performance remains intentionally pending until the P3-02 scenario suite and later implementation phases execute.

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.
