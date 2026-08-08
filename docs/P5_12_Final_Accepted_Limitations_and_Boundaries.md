# P5-12 Final Accepted Limitations and Boundaries

## FR-02 — bounded-model limitation
The frozen Project 4 classifier was trained on commercial-contract language and can produce a semantically incorrect, high-confidence classification on public-sector solicitation language. The final operator experience explicitly states that `MODEL_DOMAIN_SHIFT` means confidence does not establish semantic correctness. Consequential use is escalated to a qualified human reviewer.

## FR-03 — bounded evidence limitation
The registered evidence corpus is bounded, and retrieval alone never establishes support. An evidence item must pass configured validation/sufficiency controls or the system abstains/escalates. In the exploratory Covered California test, P5-11 retrieved one item that remained insufficient, while the later P5-12 visual regression retrieved zero items; both runs remained 0/3 sufficient and escalated. The exact retrieval count for this non-frozen fresh request is therefore treated as an exploratory retrieval outcome, not a frozen benchmark metric.

## Corrected findings
- **FR-01:** generic RFP/RFQ format terminology no longer independently drives the RFP/RFQ Preparation capability match.
- **FR-04:** operator packet presentation is table-free in Colab.
- **FR-05:** structured monetary values render as human-readable currency.

## Authority boundary
The system can produce a nonbinding recommendation only. It cannot record the organization's final decision without an authorized human disposition, and it performs no autonomous external action.
