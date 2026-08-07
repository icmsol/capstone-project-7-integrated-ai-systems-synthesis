# P5-12 — Operator Acceptance Findings and Hardening

## Purpose

P5-12 hardens the submission candidate using findings from two manual operator acceptance runs: RFO 3485A and the previously unseen Covered California RFP 2026-01. The hardening intentionally preserves the frozen Project 4 model and prior evaluation history.

## Finding dispositions

### FR-01 — Alignment precision — corrected

The fresh request showed that generic procurement-format metadata (`Request for Proposal`) could contribute to the ICM `RFP and RFQ Preparation` capability even when writing an RFP was not part of the requested scope. The ICM configuration now removes generic `request for proposal` / `request for quotation` positive keywords from that capability and retains substantive preparation/development terms. This is a configuration precision correction, not a hard-coded Covered California rule.

Regression intent:
- an unrelated security-services RFP must not match `ICM-PRC-004` merely because its procurement method is an RFP;
- an opportunity that actually requests RFP preparation, solicitation development, or evaluation-criteria development must still match strongly.

### FR-02 — High-confidence public-sector semantic misclassification — bounded and documented

A verification-rights passage was labeled `Ip Ownership Assignment` at approximately 0.9946 confidence. The frozen Project 4 model is **not retrained**, and the earlier evaluation history is **not rewritten**. The observed error is retained as evidence of the model's bounded domain. The operator interface now states explicitly that a `MODEL_DOMAIN_SHIFT` warning overrides confidence for consequential interpretation and that original language requires qualified review.

This is acceptable for the capstone because the safeguard behaved correctly: the case escalated, the model output was not treated as legal interpretation, and no autonomous external action occurred.

### FR-03 — Retrieved but insufficient evidence — accepted safe behavior

The evidence workflow retrieved one FAR record, but the assessment remained insufficient and none of the three claims became sufficiently supported. This is retained as a positive safeguard example: retrieval is not equivalent to evidentiary support.

### FR-04 — Colab Markdown table rendering — corrected in operator view

The canonical packet JSON and Markdown remain evidence artifacts. The operator-facing interface now renders a separate table-free reviewer view because Colab can collapse Markdown table headers. The operator view uses section headings and bullets for stable readability.

### FR-05 — Estimated-value presentation — corrected in operator view

Structured monetary data remains unchanged in JSON. The operator presentation converts values such as `{"amount": 12500000.0, "currency": "USD"}` to `$12,500,000 USD`.

## Versioning and integrity

The original P5-06 overlay v1.0.1 is preserved as `outputs/evaluation/p5_06/versioned_overlay_manifest_v1.0.1.json`. The active overlay advances to v1.0.2 solely to govern the intentionally changed historical ICM service-catalog configuration while leaving P5-05 and P5-06 evaluation evidence intact.

## Acceptance boundary

This hardening does not authorize autonomous submission, procurement action, legal interpretation, pricing commitment, staffing commitment, or final pursuit decisions. Final human authority and zero autonomous external actions remain mandatory.
