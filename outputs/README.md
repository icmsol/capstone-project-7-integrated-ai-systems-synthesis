# Outputs

This directory contains committed implementation outputs, evaluation evidence, CI evidence, packet artifacts, and versioned post-freeze documentation overlays.

## Structure

```text
outputs/
  case_packets/   Curated representative packet location
  ci/             Quality-gate logs/metadata when generated
  evaluation/     P5 frozen evaluation plus P6-P8 post-freeze documentation/CI overlays
  p4_01/          Intake/provenance outputs
  p4_02/          Alignment and historical-context outputs
  p4_03/          Clause-triage outputs
  p4_04/          Evidence-workflow outputs
  p4_05/          Recommendation and decision-support packet outputs
  p4_06/          Audit/replay/reproducibility outputs
```

## Canonical Integrated Packet

The committed P4-05 example is:

- [`p4_05/decision_support_packet.md`](p4_05/decision_support_packet.md)
- [`p4_05/decision_support_packet.json`](p4_05/decision_support_packet.json)
- [`p4_05/recommendation.json`](p4_05/recommendation.json)
- [`p4_05/human_disposition_template.json`](p4_05/human_disposition_template.json)

Operator-interface case outputs are generated in the runtime workspace and can be preserved in resumable case bundles.

## Final Evaluation / Candidate Evidence

See [`evaluation/README.md`](evaluation/README.md).

The frozen candidate is anchored by:

- [`evaluation/p5_12/final_submission_candidate_manifest.json`](evaluation/p5_12/final_submission_candidate_manifest.json)
- [`evaluation/p5_12/final_submission_candidate_strict_inventory.json`](evaluation/p5_12/final_submission_candidate_strict_inventory.json)
- [`evaluation/p5_12/final_submission_candidate_evidence_index.csv`](evaluation/p5_12/final_submission_candidate_evidence_index.csv)
- [`evaluation/p5_12/final_visual_regression_acceptance.json`](evaluation/p5_12/final_visual_regression_acceptance.json)

Reviewer-facing post-freeze documentation changes are versioned under `evaluation/p6_*`, `evaluation/p7_04`, and `evaluation/p8_04` so later reports/presentation materials do not silently change the frozen technical/evaluation candidate.

Generated outputs are evidence artifacts; they do not replace source documents or authorized human decisions.

## P9-02 Final Submission QA Evidence

The committed P9-02 overlay is under [`evaluation/p9_02/`](evaluation/p9_02/). A successful hosted run additionally emits the non-committed run evidence under `outputs/ci/`:

- `p9_02_pip_freeze.txt`
- `p9_02_repository_inventory.csv`
- `p9_02_repository_inventory_summary.json`

These run-generated files document the final installed environment and repository inventory; they do not change the frozen candidate.
