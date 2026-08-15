# Evaluation Outputs

This directory contains the Project 7 evaluation, refinement, acceptance, freeze evidence, and versioned post-freeze documentation/CI overlays.

## Evaluation Lineage

```text
p5_01/   Frozen 19-case evaluation execution
p5_02/   System-level metrics and case/category matrices
p5_03/   Failure analysis and refinement backlog
p5_04/   Refined evaluation and configuration-portability evidence
p5_05/   Final frozen evaluation baseline and evidence inventory
p5_06/   Acceptance-corrected baseline and versioned overlay evidence
p5_07/   CI manifest-verification correction evidence
p5_12/   Operator hardening findings and final submission-candidate freeze
p6_01/   Post-freeze documentation overlay
p6_02/   Post-freeze Markdown/system-design overlay
p6_03/   Post-freeze governance overlay
p6_04/   Post-freeze reproducibility overlay
p7_04/   Post-freeze synthesis-paper publication overlay
p8_04/   Post-freeze mentor-presentation publication overlay
```

## Frozen Final Metrics

The final evaluation baseline records:

- 19/19 cases passed
- 262/262 assertions passed
- 167/167 critical assertions passed
- 95/95 major assertions passed
- 0 regression cases
- 0 autonomous external actions

See [`p5_05/final_evaluation_baseline.json`](p5_05/final_evaluation_baseline.json).

## Final Submission Candidate

`PROJECT7-SUBMISSION-CANDIDATE-v1.0.0` is documented by:

- [`p5_12/final_submission_candidate_manifest.json`](p5_12/final_submission_candidate_manifest.json)
- [`p5_12/final_submission_candidate_strict_inventory.json`](p5_12/final_submission_candidate_strict_inventory.json)
- [`p5_12/final_submission_candidate_evidence_index.csv`](p5_12/final_submission_candidate_evidence_index.csv)
- [`p5_12/final_visual_regression_acceptance.json`](p5_12/final_visual_regression_acceptance.json)
- [`p5_12/operator_hardening_findings.json`](p5_12/operator_hardening_findings.json)

The P5-06 historical overlay remains preserved. Later P6-P8 reviewer-facing documentation/publication changes are explicitly versioned as post-freeze overlays and do not rewrite the frozen scenario history or technical/evaluation candidate.

The Covered California fresh-request retrieval count differed between exploratory runs (one insufficient item in P5-11 versus zero in the P5-12 visual regression); both remained 0/3 sufficient and escalated. That count is documented as exploratory rather than treated as a frozen benchmark metric.
