# Configurable Small-Business Opportunity-to-Contract Intelligence and Assurance Framework

**ICM Solutions Reference Implementation — Capstone Project 7: Industry Integrated AI Systems Synthesis**

[![Project 7 Quality Gate](https://github.com/icmsol/capstone-project-7-integrated-ai-systems-synthesis/actions/workflows/project7-quality-gate.yml/badge.svg)](https://github.com/icmsol/capstone-project-7-integrated-ai-systems-synthesis/actions/workflows/project7-quality-gate.yml)
[![Open Operator Interface in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/icmsol/capstone-project-7-integrated-ai-systems-synthesis/blob/main/notebooks/Project_7_Operator_Interface.ipynb)

This repository contains a configurable, evidence-grounded AI decision-support prototype for small public-sector consulting businesses. It integrates opportunity intake, organization-fit screening, historical procurement context, bounded clause-theme triage, evidence validation, nonbinding recommendations, auditability, resumable case state, and explicit human disposition.

ICM Solutions is the reference organization profile. A fictional second profile is included to demonstrate configuration portability.

## Current Project State

The technical/evaluation candidate is frozen as **`PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`**. The final candidate was accepted after hosted CI and operator-interface acceptance testing.

Current frozen evidence includes:

- **19/19 evaluation cases passed**
- **262/262 assertions passed**
- **167/167 critical assertions passed**
- **95/95 major assertions passed**
- **0 regression cases**
- **0 unresolved critical or major acceptance defects**
- **0 autonomous external actions**
- **44 strict technical/evaluation artifacts checksum-governed**
- same-request operator acceptance with human `accept` disposition and successful bundle restore
- fresh-request operator acceptance with human `escalate` disposition and successful bundle restore
- targeted visual regression confirming the final operator hardening changes

See the [final submission-candidate manifest](outputs/evaluation/p5_12/final_submission_candidate_manifest.json), [strict inventory](outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json), [final evidence index](outputs/evaluation/p5_12/final_submission_candidate_evidence_index.csv), and [freeze documentation](docs/P5_12_Final_Submission_Candidate_Freeze.md).

Phase 6 reviewer documentation, reports, presentation materials, and defense visuals remain intentionally mutable under the documented freeze boundary.

## Fastest Reviewer Path

A reviewer does **not** need to call internal Python modules manually.

1. Open the [Project 7 Operator Interface in Colab](https://colab.research.google.com/github/icmsol/capstone-project-7-integrated-ai-systems-synthesis/blob/main/notebooks/Project_7_Operator_Interface.ipynb).
2. Choose **Runtime → Run all**.
3. Use the seven operator stages:
   1. Opportunity Intake
   2. Organization Alignment
   3. Clause Triage
   4. Evidence Review
   5. Recommendation & Packet
   6. Human Disposition
   7. Save / Resume
4. Upload a public or explicitly approved solicitation.
5. Confirm the structured intake fields against the source before validating intake.
6. Supply the solicitation passages to be triaged; the prototype does not independently extract the complete solicitation into clause passages.
7. Review the nonbinding recommendation and unresolved issues.
8. Record an authorized human disposition.
9. Export a resumable case bundle when persistence outside the current Colab runtime is needed.

The operator interface is the intended reviewer-facing entry point. Internal modules, validation scripts, frozen fixtures, and stage-specific notebooks exist for reproducibility and evidence, not as the primary user workflow.

## What the System Does

The integrated workflow supports an authorized human reviewer by:

1. validating normalized opportunity metadata and source provenance;
2. comparing opportunity text with a configured organization's service capabilities;
3. attaching descriptive historical procurement context;
4. applying the frozen Project 4 clause-theme classifier to operator-selected passages;
5. retrieving and validating bounded authoritative evidence;
6. assembling a nonbinding recommendation and decision-support packet;
7. routing unresolved or consequential issues to qualified human reviewers;
8. recording a separate authorized human disposition;
9. maintaining audit events and resumable case state.

The system may recommend. It may **not** autonomously approve, decline, submit, purchase, sign, communicate externally, or represent its recommendation as the organization's final decision.

## Important Operator Controls and Limitations

- **Intake metadata is human-confirmed.** The current prototype does not independently extract and semantically verify every structured intake field against the uploaded PDF.
- **Clause passages are operator supplied.** The system does not claim complete-document clause discovery.
- **Project 4 is bounded triage, not legal interpretation.** The classifier was trained on CUAD commercial-contract language and can be out of domain on public-sector solicitations.
- **`MODEL_DOMAIN_SHIFT` overrides apparent confidence for consequential interpretation.** High model confidence does not establish semantic or legal correctness.
- **Evidence retrieval is bounded.** Retrieval does not equal support; evidence must pass validation/sufficiency controls.
- **Organization alignment is screening evidence.** It is not proof of eligibility, staffing capacity, award probability, strategic fit, or financial feasibility.
- **Human authority is mandatory.** The AI recommendation remains separate and immutable when the human disposition is recorded.
- **No autonomous external action is permitted.**

See [P5-12 Final Accepted Limitations and Boundaries](docs/P5_12_Final_Accepted_Limitations_and_Boundaries.md).

## Configuration and Portability

Organization-specific business logic is externalized from source code.

Reference profiles:

- [ICM Solutions profile](config/profiles/icm_solutions.json)
- [ICM service catalog](config/profiles/icm_service_catalog.csv)
- [Fictional Redwood Civic Analytics profile](config/profiles/fictional_small_business.json)
- [Fictional service catalog](config/profiles/fictional_service_catalog.csv)

Blank tailoring templates are in [`config/templates/`](config/templates/).

A different small business can tailor:

- organization identity, markets, and geographies;
- service families and capabilities;
- positive and exclusion terms;
- opportunity-screening rules;
- staffing-family mappings;
- reviewer roles;
- recommendation thresholds.

Fixed safeguards are framework controlled and are not ordinary profile settings. See [`config/system/fixed_safeguards.json`](config/system/fixed_safeguards.json) and [`config/system/safeguard_policy.json`](config/system/safeguard_policy.json).

For configuration details, see [Configuration README](config/README.md).

## Prior-Capstone Integration

The final system intentionally distinguishes executable reuse from bounded design evidence.

- **Project 1:** opportunity intake, normalization, and provenance concepts
- **Project 2:** historical procurement context and service-category evidence
- **Project 4:** executable bounded clause-theme classifier
- **Project 6:** evidence-grounded workflow, safeguards, auditability, and escalation patterns
- **Projects 3 and 5:** bounded design/evaluation evidence rather than direct runtime dependencies

See the [Prior-Project Traceability Matrix](docs/Prior_Project_Traceability_Matrix.md).

## Repository Structure

```text
.github/
  workflows/
    project7-quality-gate.yml       Hosted read-only regression/verification workflow

audit/                              Committed audit ledgers, checksums, and traceability records

config/
  contracts/                        14 component contracts + contract registry
  profiles/                         ICM and fictional organization configuration artifacts
  schemas/                          JSON Schemas for shared and evaluation artifacts
  system/                           Fixed policies, safeguards, registries, and freeze controls
  templates/                        Blank organization-tailoring templates

data/
  frozen_scenarios/                 Legacy/frozen scenario navigation
  implementation/                   Controlled implementation fixtures by activity
  processed/                        Generated normalized/derived data
  raw/                              Preserved approved/public source inputs
  reference/                        Frozen FAR and Project 2 reference assets
  scenarios/
    frozen/                         Versioned executable frozen scenario sets

docs/
  ci/                               Documentation copy of the current quality-gate workflow
  diagram_sources/                  DOT sources for architecture/use-case diagrams
  *.md / *.json / *.csv             Architecture, contracts, safeguards, evaluation, acceptance,
                                    traceability, manifests, and freeze evidence

figures/                             PNG/SVG architecture and UML-style use-case diagrams

models/
  project4/                          Frozen Project 4 inference package and model assets

notebooks/
  Project_7_Operator_Interface.ipynb
  P4_03_Bounded_Clause_Triage_Validation.ipynb

outputs/
  case_packets/                      Curated packet location; canonical P4-05 packet is under outputs/p4_05
  ci/                                Local/hosted quality-gate logs and metadata when generated
  evaluation/
    p5_01/ ... p5_12/                Frozen evaluation, metrics, failure, acceptance, and final-candidate evidence
  p4_01/ ... p4_06/                  Stage-level implementation outputs

presentation/                        Phase 6 presentation/defense materials
reports/                             Phase 6 synthesis paper and supporting report artifacts
scripts/                             Validation, verification, CI, and evidence-generation scripts
src/
  project7/                          Reusable integrated-system Python modules
tests/                               Schemas, contracts, safeguards, component, regression, and freeze tests

requirements_p4_01.txt ...           Historical stage-specific dependency snapshots
requirements_p5_09.txt               Operator-interface dependency entry point
```

Each major repository area has its own README where one exists:

- [Audit](audit/README.md)
- [Configuration](config/README.md)
- [Data](data/README.md)
- [Documentation](docs/README.md)
- [Figures](figures/README.md)
- [Notebooks](notebooks/README.md)
- [Outputs](outputs/README.md)
- [Presentation](presentation/README.md)
- [Reports](reports/README.md)
- [Source](src/README.md)
- [Tests](tests/README.md)

## Key Reviewer Evidence

### Architecture and design

- [Integrated System Architecture](docs/Integrated_System_Architecture.md)
- [Orchestration and Component Contracts](docs/Orchestration_and_Component_Contracts.md)
- [Shared Data Contracts](docs/Shared_Data_Contracts.md)
- [Safeguards and Fail-Closed Behavior](docs/Safeguards_and_Fail_Closed_Behavior.md)
- [Prior-Project Traceability Matrix](docs/Prior_Project_Traceability_Matrix.md)

### Evaluation and acceptance

- [P5-02 System-Level Metrics](docs/P5_02_System_Level_Metrics.md)
- [P5-03 Failure and Unexpected-Behavior Analysis](docs/P5_03_Failure_and_Unexpected_Behavior_Analysis.md)
- [P5-04 Refinement, Configuration Portability, and CI](docs/P5_04_Refinement_Configuration_Portability_and_CI.md)
- [P5-05 Final Evaluation Freeze](docs/P5_05_Final_Evaluation_Freeze.md)
- [P5-06 Manual Operator Acceptance and Correction](docs/P5_06_Manual_Operator_Acceptance_and_Correction.md)
- [P5-08 Human Disposition Recorder](docs/P5_08_Human_Disposition_Recorder.md)
- [P5-09 Operator Interface](docs/P5_09_Operator_Interface.md)
- [P5-12 Operator Acceptance Findings and Hardening](docs/P5_12_Operator_Acceptance_Findings_and_Hardening.md)
- [P5-12 Final Submission-Candidate Freeze](docs/P5_12_Final_Submission_Candidate_Freeze.md)

### Diagrams

See [Figures README](figures/README.md) for architecture, provenance, failure/escalation, recommendation/human-decision, portability, and six major-function use-case diagrams.

## Reproducibility and CI

The live GitHub Actions workflow is:

[` .github/workflows/project7-quality-gate.yml`](.github/workflows/project7-quality-gate.yml)

It runs repository-integrity checks, schema/contract/safeguard validation, frozen evaluation verification, P5-12 hardening checks, the final submission-candidate verifier, and regression/unit tests. The workflow uses read-only repository permissions and contains no deployment/publishing step.

The current workflow status is available on the [Project 7 Actions page](https://github.com/icmsol/capstone-project-7-integrated-ai-systems-synthesis/actions).

The frozen candidate can also be verified with:

```bash
python scripts/verify_p5_12_final_submission_candidate.py
python -m unittest tests.test_p5_12_final_submission_candidate -v
```

## Production Boundary

This repository is a **controlled capstone prototype**, not a production procurement, legal, compliance, security, staffing, pricing, financial, or contract-approval system.

Recommendations are nonbinding. Final authority remains human.
