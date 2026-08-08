# Safeguards and Fail-Closed Behavior — Final Reconciliation (P6-02)

> **Current-state document.** The P2-04 fixed safeguard baseline remained active through the final evaluation and operator acceptance.

## Fixed Baseline

- Safeguard controls: **30**
- Reason codes: **35**
- Trigger scenarios: **30**
- Safeguard categories: **14**

## Fixed Thresholds

| Threshold | Baseline |
|---|---:|
| Project 4 classification minimum | 0.80 |
| Evidence-item relevance minimum | 0.60 |
| Directional-recommendation evidence minimum | 0.70 |
| Maximum retry attempts | 1 |

These are controlled capstone baselines, not industry standards.

## Final Operator Controls

1. Intake metadata is operator-confirmed.
2. Clause passages are operator-supplied.
3. `MODEL_DOMAIN_SHIFT` makes confidence non-authoritative for public-sector consequential use.
4. Evidence retrieval is distinct from evidence sufficiency.
5. Missing/insufficient evidence cannot be treated as favorable evidence.
6. System recommendation is nonbinding and separate from human disposition.
7. Autonomous external actions are prohibited.

## Fail-Closed / Abstention / Escalation

Integrity, authorization, schema, audit, source, model/corpus, citation, reviewer, retry, and prohibited-action failures are fail-closed.

Insufficient information, low confidence, domain shift, missing/invalid evidence, insufficient evidence, conflict, and mandatory specialist review trigger abstention/escalation rather than unsupported conclusions.

## Final Evaluation

- 19/19 cases PASS
- 262/262 assertions PASS
- 0 regressions
- 0 unresolved critical/major acceptance defects
- 0 autonomous external actions

## Production Boundary

These safeguards reduce risk in a controlled prototype but are not a production security authorization, legal opinion, compliance certification, or substitute for organizational governance.
