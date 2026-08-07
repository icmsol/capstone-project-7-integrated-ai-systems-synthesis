# P5-06 — Manual Operator Acceptance Test and Versioned Correction

## Purpose

P5-06 tests the actual GitHub solution as an operator would use it on a real, previously unseen public-sector solicitation before final documentation is written. The public source document was staged outside the repository; the repository itself remained clean throughout the test.

## Observed end-to-end behavior

- Repository integrity at commit `61edbdc`: PASS.
- Opportunity intake: provenance and checksum PASS; corrected case `CASE-22E46661B5CFB3D8` reached `intake_validated`.
- ICM alignment: `strong_alignment`, score `0.8633`, four matched capabilities, 108 descriptive historical matches.
- Project 4 clause triage on three real RFO passages: Anti-Assignment `0.999391`, Insurance `0.999922`, IP Ownership Assignment `0.972807`. All three correctly escalated because of public-sector domain shift.
- Evidence workflow: three requests, zero accepted evidence items, three insufficient assessments, three human-review routes, zero external actions. This was safe fail-closed behavior for the intentionally bounded three-record FAR corpus.
- Initial P4-05 packet assembly: failed with `PACKET_COMPONENT_MISSING` because `evidence_items=[]` was treated as an unexecuted component.

## Findings

### MAF-01 — Structured-input semantic consistency

The intake component validates provenance, checksums, schemas, and required fields but does not independently parse or cross-check operator-entered metadata against the PDF. This is retained as a documented operator responsibility and prototype limitation.

### MAF-02 — Predecessor audit path coupling

P4-02 through P4-05 originally read predecessor audit ledgers only from fixed repository-relative paths. Each wrapper now accepts an optional `prior_audit_path` while preserving the original default for backward compatibility.

### MAF-03 — Evidence corpus coverage

The registered evidence corpus is intentionally representative rather than complete. No evidence item meeting threshold is a valid outcome and must remain an abstention/escalation condition rather than being forced into a citation. This remains a documented prototype limitation.

### MAF-04 — Zero-evidence packet integration defect

A completed evidence workflow with non-empty `evidence_assessments` and a valid empty `evidence_items` list was incorrectly rejected as a missing component. Recommendation and packet completeness checks now distinguish `evidence_items` being absent from a valid zero-result list.

### MAF-05 — Case-specific packet narrative

The original P4-05 packet contained static statements tied to the controlled demonstration case, including named predicted themes, a truncation statement, and specific FAR citations. The executive summary, evidence statement, model warnings, unresolved issues, and evidence limitations are now derived from the actual case state.

## Regression evidence

The complete frozen v1.0.1 suite was rerun after the correction: **19/19 cases PASS and 262/262 assertions PASS**, with zero frozen-input changes and zero external actions. The original controlled P4-05 packet tests remain valid, and new tests confirm that a legitimate zero-evidence result can proceed to a nonbinding human-review packet.

## Versioning

The P5-05 baseline `PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.0` remains historical evidence. The corrected code is tracked as `PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.1`. P5-05 inventory verification skips only paths explicitly listed in the P5-06 versioned overlay; P5-06 independently verifies the replacement files by SHA-256.

## Completion gate

P5-06 remains open until the versioned correction is committed to `main`, the hosted Project 7 Quality Gate passes, and the manual RFO test is resumed from P4-05 to confirm that a packet is produced with a nonbinding specialized-review recommendation and no final decision.
