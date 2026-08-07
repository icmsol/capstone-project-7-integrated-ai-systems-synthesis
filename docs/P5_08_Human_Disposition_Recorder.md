# P5-08 — Authorized Human Disposition Recorder

## Purpose

The P5-08 manual acceptance test confirmed that the corrected Project 7 backend can process RFO 3485A through P4-05 and stop safely at `awaiting_human_review` with recommendation `R-05 — Escalate — Specialized Review Required`, zero accepted evidence items, three insufficient evidence assessments, and zero external actions.

The repository already defined both `human_disposition.schema.json` and the `human_disposition_recorder` component contract, but no executable recorder existed in `src/project7`. This package implements that previously specified human-authority boundary without changing the original recommendation or allowing the system to act externally.

## Implementation

`src/project7/human_disposition.py` adds `record_human_disposition(...)`.

The recorder:

- accepts only cases in `awaiting_human_review`;
- requires a non-empty human reviewer identity;
- validates the selected reviewer role against the configured organization reviewer-role registry;
- validates the disposition against the committed `human_disposition.schema.json`;
- requires a rationale of at least 20 characters;
- verifies the case and recommendation identifiers;
- requires an authorized escalation target when disposition is `escalate`;
- preserves the original nonbinding recommendation byte-for-byte at the logical JSON level;
- records a separate human disposition artifact;
- appends a `human_disposition_recorded` audit event with `actor_type = human`;
- continues the prior P4-05 audit hash chain;
- performs zero external actions.

Case-state mapping is deliberately simple:

- `defer_pending_information` -> `deferred`
- `escalate` -> `escalated`
- `accept`, `accept_with_modified_conditions`, or `reject` -> `finalized`

`finalized` means the Project 7 decision-support case has a recorded authorized human disposition. It does **not** make the AI recommendation itself an organizational decision and does not transmit, submit, approve, price, staff, or otherwise act externally.

## Test Coverage

`tests/test_human_disposition_recorder.py` verifies:

1. an authorized defer disposition is recorded separately from the recommendation;
2. the recommendation remains unchanged;
3. the audit event is explicitly human-authored and continues the hash chain;
4. an accepted human response finalizes the decision-support case;
5. unauthorized reviewer roles fail closed;
6. inadequate rationale defers rather than silently finalizing;
7. recommendation-ID mismatches fail closed;
8. escalation targets must map to configured authorized roles;
9. human disposition and final case state remain schema-valid;
10. external actions remain zero.

## Acceptance Boundary

This implementation closes the backend gap identified as MAF-06 during the manual RFO 3485A test. The operator-facing interface remains a later activity. The frontend must call this recorder only after a real human selects a disposition and supplies identity, authorized role, rationale, and any required conditions or escalation target.
