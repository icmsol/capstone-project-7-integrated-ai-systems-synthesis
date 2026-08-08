# Documentation

This directory contains the architecture, data contracts, component contracts, safeguards, traceability, implementation evidence, evaluation evidence, acceptance findings, CI documentation, and final-candidate governance records for Project 7.

## Architecture and Core Design

- [Integrated System Architecture](Integrated_System_Architecture.md)
- [Orchestration and Component Contracts](Orchestration_and_Component_Contracts.md)
- [Shared Data Contracts](Shared_Data_Contracts.md)
- [Safeguards and Fail-Closed Behavior](Safeguards_and_Fail_Closed_Behavior.md)
- [Representative Operational Workload](Representative_Operational_Workload.md)
- [Scenario Taxonomy and Target Cases](Scenario_Taxonomy_and_Target_Cases.md)
- [Prior-Project Traceability Matrix](Prior_Project_Traceability_Matrix.md)

Diagram source files are in [`diagram_sources/`](diagram_sources/); rendered PNG/SVG versions are in [`../figures/`](../figures/).

## Scenario and Evaluation Design

Key scenario/evaluator documents include:

- [Frozen Scenario Set and Evaluator Guide](Frozen_Scenario_Set_and_Evaluator_Guide.md)
- [P3-04 Scenario Quality Review](P3_04_Scenario_Quality_Review.md)
- [P3-04 v1.0.1 Correction and Evaluator Guide](P3_04_v1_0_1_Correction_and_Evaluator_Guide.md)

## Implementation Evidence

P4 documents record the integrated implementation:

- [P4-01 Opportunity Intake and Provenance](P4_01_Opportunity_Intake_and_Provenance.md)
- [P4-02 Configurable Alignment and Historical Context](P4_02_Configurable_Alignment_and_Historical_Context.md)
- [P4-03 Bounded Clause-Theme Inference](P4_03_Bounded_Clause_Theme_Inference.md)
- [P4-04 Evidence-Grounded Agent Workflow](P4_04_Evidence_Grounded_Agent_Workflow.md)
- [P4-05 Integrated Decision-Support Packet](P4_05_Integrated_Decision_Support_Packet.md)
- [P4-06 Audit and Reproducibility](P4_06_Audit_and_Reproducibility.md)

Each P4 activity also has an implementation manifest, requirements matrix, and validation-evidence artifact in this directory.

## Evaluation, Acceptance, and Hardening

- [P5-01 Frozen Evaluation Run](P5_01_Frozen_Evaluation_Run.md)
- [P5-02 System-Level Metrics](P5_02_System_Level_Metrics.md)
- [P5-03 Failure and Unexpected-Behavior Analysis](P5_03_Failure_and_Unexpected_Behavior_Analysis.md)
- [P5-04 Refinement, Configuration Portability, and CI](P5_04_Refinement_Configuration_Portability_and_CI.md)
- [P5-04 CI Quality Gate](P5_04_CI_Quality_Gate.md)
- [P5-05 Final Evaluation Freeze](P5_05_Final_Evaluation_Freeze.md)
- [P5-05 Final CI Quality Gate](P5_05_Final_CI_Quality_Gate.md)
- [P5-06 Manual Operator Acceptance and Correction](P5_06_Manual_Operator_Acceptance_and_Correction.md)
- [P5-07 CI Manifest Verification Correction](P5_07_CI_Manifest_Verification_Correction.md)
- [P5-08 Human Disposition Recorder](P5_08_Human_Disposition_Recorder.md)
- [P5-09 Operator Interface](P5_09_Operator_Interface.md)
- [P5-12 Operator Acceptance Findings and Hardening](P5_12_Operator_Acceptance_Findings_and_Hardening.md)
- [P5-12 Final Accepted Limitations and Boundaries](P5_12_Final_Accepted_Limitations_and_Boundaries.md)
- [P5-12 Final Submission-Candidate Freeze](P5_12_Final_Submission_Candidate_Freeze.md)

## CI Reference

The live workflow is [`../.github/workflows/project7-quality-gate.yml`](../.github/workflows/project7-quality-gate.yml).

[`ci/project7-quality-gate.yml`](ci/project7-quality-gate.yml) is maintained as a documentation copy and should match the live workflow when P6-01 is committed.

## Final Candidate Evidence

The frozen technical/evaluation candidate is `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`.

Primary machine-readable evidence:

- [Final submission-candidate manifest](../outputs/evaluation/p5_12/final_submission_candidate_manifest.json)
- [Strict checksum inventory](../outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json)
- [Final evidence index](../outputs/evaluation/p5_12/final_submission_candidate_evidence_index.csv)
- [Final visual-regression acceptance](../outputs/evaluation/p5_12/final_visual_regression_acceptance.json)
- [Operator hardening findings](../outputs/evaluation/p5_12/operator_hardening_findings.json)

Phase 6 may add/update reviewer documentation in `docs/` without silently changing frozen technical/evaluation artifacts.

## P6-02 System Design and Markdown Reconciliation

- [P6-02 Documentation Reconciliation](P6_02_System_Design_and_Markdown_Reconciliation.md)
- [P6-02 Diagram Reconciliation](P6_02_Diagram_Reconciliation.md)
- [P6-02 Markdown Audit](P6_02_Non_README_Markdown_Audit.csv)

## P6-03 Governance, Ethics, Risk, and Responsible Deployment

- [Governance, Ethics, and Risk Framework](P6_03_Governance_Ethics_and_Risk_Framework.md)
- [Governance Risk Register](P6_03_Risk_Register.md)
- [Risk Register CSV](P6_03_Risk_Register.csv)
- [Safeguard Matrix CSV](P6_03_Safeguard_Matrix.csv)
- [Human Oversight and Accountability](P6_03_Human_Oversight_and_Accountability.md)
- [Records, Audit, and Retention Expectations](P6_03_Records_Audit_and_Retention_Expectations.md)
- [Records Expectations CSV](P6_03_Records_Expectations.csv)
- [Production-Readiness Boundary](P6_03_Production_Readiness_Boundary.md)
- [Production-Readiness Gates CSV](P6_03_Production_Readiness_Gates.csv)
