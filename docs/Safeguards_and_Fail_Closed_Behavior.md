# P2-04 — Safeguards and Fail-Closed Behavior

## Purpose

The Project 7 safeguard policy converts ethical and responsible-deployment boundaries into fixed, versioned, machine-validatable controls. Organization profiles may tailor services, business screening rules, staffing families, reviewer mappings, and permitted recommendation thresholds. They may not disable or weaken the controls in this package.

## Baseline Results

- **Safeguard controls:** 30
- **Risk statements mapped:** 30
- **Reason codes:** 35
- **Trigger scenarios:** 30
- **Safeguard categories:** 14
- **Invalid policy:** correctly rejected

## Fixed Thresholds

| Threshold | Baseline | Change Authority |
|---|---:|---|
| Project 4 classify minimum | 0.80 | Framework-level versioned change only |
| Evidence-item relevance minimum | 0.60 | Framework-level versioned change only |
| Directional-recommendation evidence minimum | 0.70 | Framework-level versioned change only |
| Maximum retry attempts | 1 | Framework-level versioned change only |

These are conservative capstone baselines, not industry standards. They may be adjusted only through a new policy version, documented risk review, and regression testing. They may not be changed by an ordinary organization profile.

## Control Coverage

| Category | Controls |
|---|---:|
| `audit_traceability` | 2 |
| `configuration_governance` | 3 |
| `evidence_sufficiency` | 3 |
| `external_action` | 1 |
| `failure_recovery` | 1 |
| `human_authority` | 2 |
| `model_inference` | 4 |
| `official_evidence` | 3 |
| `privacy_security` | 2 |
| `production_boundary` | 1 |
| `prompt_injection` | 1 |
| `recommendation` | 3 |
| `source_provenance` | 2 |
| `structured_analysis` | 2 |

## Fail-Closed Conditions

Normal workflow processing stops when:

- the safeguard policy is invalid or missing;
- an organization profile attempts a fixed-safeguard override;
- required configuration is missing or inconsistent;
- a material source is unauthorized or lacks reproducible provenance;
- a secret or prohibited sensitive value is detected;
- prompt injection attempts to change system authority or source rules;
- the Project 4 model package fails integrity checks;
- the official evidence corpus is not approved;
- citation validation fails;
- recommendation completeness or evidence linkage fails;
- reviewer authorization fails;
- audit schema, sanitization, chain, or persistence fails;
- retry limits are exceeded;
- an external action or production-readiness claim is requested.

## Abstention Conditions

The system produces no directional output when:

- structured opportunity information is insufficient;
- model confidence is below 0.80;
- an exact requested citation cannot be found;
- evidence relevance or sufficiency is below the fixed minimum;
- validated evidence cannot support the requested claim.

Abstention is an explicit controlled result, not an error hidden from the reviewer.

## Mandatory Escalation

Specialist or executive review is mandatory for:

- legal interpretation or contract enforceability;
- privacy or restricted personal data;
- cybersecurity or credential exposure;
- pricing, financial commitment, or payment terms;
- staffing commitment or named-person availability;
- contract acceptance, rejection, or modification;
- material conflicting evidence;
- low-confidence or out-of-domain model output;
- unverified or stale official sources;
- conflicts of interest or ethical concerns;
- external communication, submission, or transactions;
- production deployment or production-readiness claims.

## Prompt-Injection Boundary

Opportunity records, contracts, solicitations, and retrieved documents are untrusted data. Embedded instructions cannot:

- change the system prompt or policy;
- select new tools or external sources;
- reveal credentials or private reasoning;
- disable safeguards;
- authorize a decision;
- trigger an external action.

Detected injection text is blocked, recorded, and routed for security review when material.

## Recommendation Boundary

Every recommendation must:

- remain explicitly nonbinding;
- link material claims to recorded evidence, rules, model artifacts, or validated source records;
- show supporting evidence and counterevidence;
- disclose missing information, conditions, limitations, and freshness;
- name the required human reviewer and next action;
- preserve an audit reference.

A recommendation that fails these requirements is rejected, not partially displayed as a valid result.

## Human Authority

A case cannot be finalized without:

- an authorized reviewer role;
- one of the permitted human dispositions;
- substantive rationale;
- separate preservation of the original system recommendation;
- a valid audit event.

## Risk-to-Control Traceability

`docs/P2_04_Risk_Control_Matrix.csv` and `.json` map each risk to:

- its consequence;
- one fixed safeguard control;
- control type;
- trigger;
- required action;
- human route;
- frozen test scenario.

## Validation

Run:

```bash
python tests/validate_safeguards.py
```

Expected output:

```text
Safeguard controls checked: 30
Reason codes checked: 35
Trigger scenarios checked: 30
Policy schema validation: PASS
Control and reason-code integrity: PASS
Control-to-scenario coverage: PASS
Invalid safeguard policy: correctly rejected
```

## Production Boundary

Controlled capstone prototype; no autonomous external action; nonbinding recommendation only; final human authority required.
