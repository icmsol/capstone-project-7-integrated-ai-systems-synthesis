# Audit

This directory contains committed audit, checksum, traceability, and run-evidence artifacts used to demonstrate deterministic execution and reproducibility.

## Current Contents

Key committed records include:

- `starter_file_manifest.json` — initial scaffold inventory.
- `icm_service_source_registry.json` — provenance for the ICM service configuration source material.
- `p4_01_intake_events.jsonl` — intake/provenance audit events.
- `p4_02_alignment_history_events.jsonl` — configuration/alignment/history events.
- `p4_04_evidence_workflow_events.jsonl` and `p4_04_tool_trace.jsonl` — evidence workflow and deterministic tool traces.
- `p4_05_packet_events.jsonl` — recommendation/packet assembly events.
- `p4_06_consolidated_case_ledger.jsonl` — consolidated case-level audit chain.
- `p4_06_artifact_checksums.csv` and `p4_06_reproducibility_events.jsonl` — reproducibility evidence.
- `p5_01_frozen_evaluation_ledger.jsonl` through `p5_05_final_freeze_event.jsonl` — evaluation, metrics, refinement, portability, and freeze events.
- `P3_04_Validation_Evidence.json` and `P3_04_v1_0_1_Validation_Evidence.json` — scenario-quality validation evidence.

## Runtime Operator Evidence

The reviewer-facing operator workflow writes case-specific audit events into its runtime workspace and includes them in resumable case bundles. Those runtime bundles are not automatically committed to this directory.

See:

- [P4-06 Audit and Reproducibility](../docs/P4_06_Audit_and_Reproducibility.md)
- [P5-09 Operator Interface](../docs/P5_09_Operator_Interface.md)
- [P5-12 Final Submission-Candidate Freeze](../docs/P5_12_Final_Submission_Candidate_Freeze.md)

Audit records are evidence of execution and control flow; they do not convert AI recommendations into final human decisions.
