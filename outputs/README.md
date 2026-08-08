# Outputs

This directory contains committed implementation outputs, evaluation evidence, CI evidence, and packet artifacts.

## Structure

```text
outputs/
  case_packets/   Curated representative packet location
  ci/             Quality-gate logs/metadata when generated
  evaluation/     P5 frozen evaluation, metrics, failures, acceptance, and final candidate
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

The final candidate is anchored by:

- [`evaluation/p5_12/final_submission_candidate_manifest.json`](evaluation/p5_12/final_submission_candidate_manifest.json)
- [`evaluation/p5_12/final_submission_candidate_strict_inventory.json`](evaluation/p5_12/final_submission_candidate_strict_inventory.json)
- [`evaluation/p5_12/final_submission_candidate_evidence_index.csv`](evaluation/p5_12/final_submission_candidate_evidence_index.csv)
- [`evaluation/p5_12/final_visual_regression_acceptance.json`](evaluation/p5_12/final_visual_regression_acceptance.json)

Generated outputs are evidence artifacts; they do not replace source documents or authorized human decisions.
