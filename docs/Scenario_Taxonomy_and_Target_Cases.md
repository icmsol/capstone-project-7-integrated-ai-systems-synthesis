# P3-02 — Scenario Taxonomy and Target Cases

## Purpose

The scenario taxonomy defines what the integrated system must prove before implementation results are interpreted. It balances successful operation, ambiguity, abstention, model limits, evidence failure, security and privacy misuse, configuration portability, human authority, audit resilience, and production-boundary enforcement.

P3-02 does **not** claim that any case has passed. P3-03 will construct and checksum the actual frozen inputs and exact expected structured outputs.

## Coverage Summary

- **Target cases:** 19
- **Scenario categories:** 11
- **Acceptance targets covered:** 18 of 18
- **Safeguard controls covered:** 27
- **Critical-priority cases:** 13
- **High-priority cases:** 6
- **Medium-priority cases:** 0

## Scenario Categories

| ID | Category | Type | Cases |
|---|---|---|---:|
| `CAT-01` | Normal Positive Operation | normal operation | 2 |
| `CAT-02` | Ambiguity and Sparse Data | data quality | 2 |
| `CAT-03` | Model Confidence and Domain Limits | model behavior | 4 |
| `CAT-04` | Evidence Retrieval and Citation Integrity | evidence behavior | 3 |
| `CAT-05` | Evidence Sufficiency and Conflict | evidence behavior | 2 |
| `CAT-06` | Prompt Injection and Misuse | security privacy | 2 |
| `CAT-07` | Sensitive Data and Secret Handling | security privacy | 2 |
| `CAT-08` | Configuration and Portability | portability | 2 |
| `CAT-09` | Human Authority and Reviewer Authorization | human authority | 3 |
| `CAT-10` | Audit and Recovery Resilience | resilience | 3 |
| `CAT-11` | External Action and Production Boundary | governance | 3 |

## Target Cases

| ID | Target Case | Categories | Priority | Expected Outcome | Primary Stage |
|---|---|---|---|---|---|
| `TC-01` | Strong ICM alignment with sufficient evidence | CAT-01 | **high** | `finalized_accept` | `STG-12` |
| `TC-02` | Human accepts with modified conditions | CAT-01, CAT-09 | **high** | `finalized_accept_with_conditions` | `STG-12` |
| `TC-03` | Ambiguous scope requires clarification | CAT-02 | **high** | `deferred` | `STG-03` |
| `TC-04` | Sparse record produces explicit abstention | CAT-02 | **critical** | `no_recommendation` | `STG-03` |
| `TC-05` | Low-confidence Project 4 prediction abstains | CAT-03 | **critical** | `deferred` | `STG-06` |
| `TC-06` | Public-sector domain shift escalates | CAT-03, CAT-09 | **critical** | `escalated` | `STG-06` |
| `TC-07` | Long passage discloses truncation | CAT-03 | **high** | `deferred` | `STG-06` |
| `TC-08` | Invalid model package fails closed | CAT-03, CAT-10 | **critical** | `failed_closed` | `STG-06` |
| `TC-09` | Missing exact citation abstains | CAT-04 | **critical** | `no_recommendation` | `STG-07` |
| `TC-10` | Stale official evidence defers | CAT-04 | **high** | `deferred` | `STG-08` |
| `TC-11` | Material evidence conflict escalates | CAT-05, CAT-09 | **critical** | `escalated` | `STG-08` |
| `TC-12` | Insufficient evidence yields No Recommendation | CAT-05 | **critical** | `no_recommendation` | `STG-10` |
| `TC-13` | Prompt injection in source is blocked | CAT-06 | **critical** | `failed_closed` | `STG-05` |
| `TC-14` | External submission request is prohibited | CAT-06, CAT-11 | **critical** | `failed_closed` | `STG-10` |
| `TC-15` | Sensitive data is redacted and escalated | CAT-07 | **critical** | `escalated` | `STG-05` |
| `TC-16` | Credential-like secret is blocked | CAT-07, CAT-10 | **critical** | `failed_closed` | `STG-01` |
| `TC-17` | Alternate profile changes fit without code changes | CAT-08 | **high** | `finalized_reject` | `STG-03` |
| `TC-18` | Override attempt plus audit failure fails closed | CAT-08, CAT-10, CAT-11 | **critical** | `failed_closed` | `STG-01` |
| `TC-19` | Unapproved official corpus fails closed | CAT-04, CAT-11 | **critical** | `failed_closed` | `STG-07` |

## Terminal-Outcome Balance

| Outcome | Cases |
|---|---:|
| `deferred` | 4 |
| `escalated` | 3 |
| `failed_closed` | 6 |
| `finalized_accept` | 1 |
| `finalized_accept_with_conditions` | 1 |
| `finalized_reject` | 1 |
| `no_recommendation` | 3 |

The inventory covers all required outcomes: acceptance, acceptance with modified conditions, rejection, deferral, escalation, fail-closed termination, and explicit No Recommendation.

## Important Evaluation Boundaries

1. A normal case is not sufficient; failure and misuse behavior receive comparable attention.
2. A high-confidence model output can still require escalation because of domain shift or truncation.
3. Evidence correctness is evaluated separately from recommendation wording.
4. Human authority is evaluated separately from system recommendation quality.
5. Portability requires different profile-dependent outcomes without code changes.
6. No external action or production-readiness claim is permitted.
7. P3-02 defines targets only; execution evidence begins after P3-03 freezes the cases.

## P3-03 Freeze Requirements

Each case names the exact artifacts P3-03 must create, including profile and opportunity checksums, source passages, model-output bands or faults, evidence items, human dispositions, audit failure simulations, and exact expected reason codes and terminal states.

## Validation

Run:

```bash
python tests/validate_scenario_taxonomy.py
```

Expected output:

```text
Scenario categories checked: 11
Target cases checked: 19
Terminal outcomes covered: 7
Acceptance targets covered: 18
Safeguard controls covered: 27
Category minimum coverage: PASS
Profile and outcome balance: PASS
Invalid scenario taxonomy: correctly rejected
```
