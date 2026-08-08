# P6-03 — Records, Audit, and Retention Expectations

## Purpose

Project 7 is designed so a reviewer can reconstruct **what source was used, what configuration and model were applied, what evidence was accepted or rejected, what recommendation was produced, and what an authorized human decided**.

The detailed record-class inventory is in [`P6_03_Records_Expectations.csv`](P6_03_Records_Expectations.csv).

## Minimum Record Chain

A defensible case record should include:

1. approved solicitation/source snapshot and checksum;
2. operator-confirmed opportunity intake;
3. organization profile/configuration versions;
4. model package provenance;
5. selected passages actually analyzed;
6. evidence retrieval and sufficiency results;
7. original system recommendation and decision-support packet;
8. authorized human disposition;
9. complete audit event chain;
10. case-bundle manifest/checksums when exported/restored;
11. relevant CI/evaluation/release evidence for the software baseline;
12. governance/risk evidence applicable to the release.

## Integrity Expectations

- Material source artifacts are checksum-addressed.
- Historical evaluation/freeze manifests are not rewritten after later documentation changes.
- Post-freeze documentation changes are governed through explicit overlays.
- Audit records include event identity, actor type, timestamp, stage outcome, reason codes, and integrity linkage.
- Audit persistence failure is fail-closed.
- Case restore requires checksum/manifest validation.

## Privacy and Data Minimization

The repository and case workflow should not become a general document archive.

- Use only approved/public/authorized sources.
- Do not commit credentials, secrets, restricted personal information, or other prohibited data.
- Store only the information needed to support the review and audit purpose.
- Redact/escalate sensitive information where the fixed safeguards require it.

## Retention Periods

**The capstone intentionally does not prescribe a numeric retention period.**

A production retention period depends on organizational policy, contract requirements, legal obligations, litigation holds, privacy requirements, procurement rules, and the record classification.

Before production, ICM must establish:

- authoritative record owner;
- classification;
- minimum/maximum retention;
- legal-hold procedure;
- secure disposal;
- access control;
- backup/restore expectations;
- rules for superseded case versions and reassessments.

Inventing a generic number in the capstone would create false legal/records assurance.

## Case Resume vs. Record Revision

Restoring a saved case bundle after runtime loss continues the **same controlled case** after integrity verification.

A materially new solicitation amendment, source, organization profile, evidence set, or business fact should be treated as a **versioned reassessment**, not an invisible overwrite of prior evidence.

## Production Boundary

Prototype auditability demonstrates the intended evidence chain, but it is not a production records-management system, legal-hold system, immutable enterprise log platform, or authorized retention schedule.
