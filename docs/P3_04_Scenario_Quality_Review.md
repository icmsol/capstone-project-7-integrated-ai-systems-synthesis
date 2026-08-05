# P3-04 — Scenario Quality Review

## Review Verdict

**Corrections are required before Phase 3 can be closed.**

The P3-03 scenario set is strong in breadth, safeguards, checksum discipline, privacy boundaries, and intellectual integrity. However, the review identified **9 open findings: 5 Critical, 3 Major, and 1 Minor**. The critical findings prevent the frozen cases from serving as executable evaluation inputs in their current form.

The correct change-control action is to preserve `v1.0.0` as the reviewed baseline and create a corrected **`v1.0.1`** freeze. Editing `v1.0.0` in place would conflict with the evaluator guide's own freeze rules.

## Review Scope

The review assessed:

- file and checksum completeness;
- bundled validator execution;
- alignment with the shared data contracts and orchestration policy;
- scenario realism and independence from expected outcomes;
- human-decision and terminal-state coherence;
- evidence, misuse, privacy, portability, and audit-failure coverage;
- secret and credential leakage;
- readiness to implement the evaluator and close Phase 3;
- the Project 7 requirement to evaluate realistic system behavior, failures, risks, tradeoffs, and responsible use.

## Positive Results

| ID | Review Check | Result | Evidence |
|---|---|---|---|
| `P-001` | P3-02 taxonomy validation | **PASS** | 11 categories, 19 target cases, all seven intended outcome types, all 18 acceptance targets, and 27 safeguard controls validated. |
| `P-002` | P3-01 operational workload validation | **PASS** | 8 actors, 8 approved inputs, 12 stages, 6 human decision points, and 18 acceptance targets validated. |
| `P-003` | P2-04 safeguard validation | **PASS** | 30 controls, 35 reason codes, 30 trigger scenarios, and control-to-scenario integrity passed. |
| `P-004` | P2-03 component-contract validation | **PASS** | 14 component contracts, orchestration policy, and stage-to-contract referential integrity passed. |
| `P-005` | P2-02 shared-schema validation | **PASS** | 11 schemas and the valid/invalid integrated-case examples passed their bundled validation. |
| `P-006` | Case-level checksum integrity | **PASS** | All required files listed by the 19 case manifests matched their stored SHA-256 values and byte counts. |
| `P-007` | Privacy and credential scan | **PASS** | No OpenAI keys, GitHub tokens, AWS access keys, or private-key blocks were detected in the P3-03 package. |
| `P-008` | Intellectual-integrity boundary | **PASS** | All case definitions, manifests, and expected outcomes remain labeled not_executed_target_only. |
| `P-009` | Identifier uniqueness | **PASS** | All 19 case IDs and all 192 assertion IDs are unique. |

## Open Findings

| ID | Severity | Category | Finding |
|---|---|---|---|
| `F-001` | **Critical** | Executable validation | The committed frozen-set validator cannot run because it points to data/scenarios/frozen/1.0.0 while the package stores cases under v1.0.0. |
| `F-002` | **Major** | Checksum integrity | The package checksum inventory is incomplete and was generated before later documentation and validation files. |
| `F-004` | **Critical** | Shared data-contract compliance | All 19 opportunity.json fixtures fail the committed shared schema, so the frozen inputs cannot be passed directly to the registered components. |
| `F-005` | **Critical** | Shared data-contract compliance | All 19 human_disposition.json fixtures fail the committed shared schema, so the frozen inputs cannot be passed directly to the registered components. |
| `F-006` | **Critical** | Expected-outcome coherence | Several frozen human decisions contradict the exact expected terminal outcomes. |
| `F-007` | **Critical** | Architecture consistency | no_recommendation is modeled as a terminal case outcome even though the orchestration policy and integrated case-state schema treat it as a recommendation result followed by human defer/escalate/reject/accept disposition. |
| `F-008` | **Major** | Evaluator contract | Assertion JSONPaths such as $.case_state.terminal_outcome, $.side_effects, and $.claims have no committed evaluation-result schema, so implementers cannot know the canonical actual-output shape. |
| `F-009` | **Major** | Scenario realism | The case expects the real Project 4 model to predict Audit Rights above 0.95, but the frozen source passage is a general services/governance excerpt rather than an audit-rights clause. |
| `F-010` | **Minor** | Traceability | P3 scenarios use STG-01 through STG-12 while orchestration policy uses descriptive IDs such as load_configuration; no machine-readable mapping is committed. |

## Critical Finding Detail

### F-001 — Validator cannot execute

The committed validator looks for:

```text
data/scenarios/frozen/1.0.0
```

The actual package stores the cases under:

```text
data/scenarios/frozen/v1.0.0
```

The validation command therefore stops with `FileNotFoundError` before checking any case. This must be corrected and rerun from a clean extraction.

### F-004 and F-005 — Frozen inputs do not conform to the shared contracts

All **19 opportunity fixtures** fail `opportunity_record.schema.json`. They use a separate field vocabulary and omit required fields such as `opportunity_id`, `source`, `source_portal`, `solicitation_id`, `normalized_title`, `ingested_at`, and `record_key`.

All **19 human-disposition fixtures** fail `human_disposition.schema.json`. They use fields such as `decision` and `reviewer_role` instead of the required `disposition`, `reviewer`, identifiers, schema version, recommendation reference, and decision timestamp structure.

A frozen test input that cannot enter the registered component contract is not executable evidence. The v1.0.1 cases must either use the real shared schemas or explicitly define and validate an adapter-input schema.

### F-006 — Human decisions conflict with expected outcomes

The following cases contain contradictory human inputs:

| Case | Frozen Human Decision | Implied Outcome | Expected Outcome |
|---|---|---|---|
| `TC-06` | `defer_pending_information` | deferred | escalated |
| `TC-09` | `defer_pending_information` | deferred | no_recommendation |
| `TC-11` | `defer_pending_information` | deferred | escalated |
| `TC-12` | `defer_pending_information` | deferred | no_recommendation |
| `TC-17` | `accept` | finalized acceptance | finalized rejection |

The exact expected outcome must be derivable from the frozen inputs rather than contradicted by them.

### F-007 — No Recommendation is not a terminal case state

`TC-04`, `TC-09`, and `TC-12` treat `no_recommendation` as a terminal case outcome. The shared case-state schema and orchestration policy instead define terminal case states as human-finalized, deferred, escalated, or failed closed. A No Recommendation is a recommendation result that still proceeds to accountable human disposition.

The corrected model should contain both:

```text
recommendation_code: no_recommendation
terminal_outcome: deferred
```

or another authorized human terminal disposition.

## Major Finding Detail

- **F-002:** the package checksum inventory lists 218 files, but 222 files existed outside the inventory at final packaging. It was generated before later files.
- **F-008:** the 192 assertion JSONPaths have no committed actual evaluation-result schema.
- **F-009:** TC-01 and TC-02 expect a real `Audit Rights` prediction above 0.95, but the frozen source passage is a general services/governance excerpt rather than an audit-rights clause.

## Minor Finding

- **F-010:** scenarios use `STG-01` through `STG-12`, while the orchestration policy uses descriptive IDs such as `load_configuration`. A machine-readable mapping is needed.

## Required Correction Strategy

Create `data/scenarios/frozen/v1.0.1` and:

1. preserve all valid scenario intent and coverage;
2. correct the validator root;
3. rebuild opportunity and human-disposition fixtures against the shared schemas;
4. distinguish recommendation result from terminal case status;
5. correct inconsistent human outcomes;
6. define the actual evaluator-result schema;
7. add the stage-ID mapping;
8. correct the Project 4 high-confidence passage expectation;
9. regenerate every affected case manifest and package checksum inventory;
10. rerun P2, P3-01, P3-02, P3-03, and P3-04 validation from a clean environment.

## Phase 3 Status

**Not ready to close.** P3-04 remains in progress until `v1.0.1` passes the full quality gate. This is a correction to evaluation readiness, not a failure of the overall project concept. The architecture, safeguards, taxonomy breadth, and responsible-use framing remain strong.
