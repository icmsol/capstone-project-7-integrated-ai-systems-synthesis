# P5-04 — Refinement, Configuration Portability, and CI Quality Gate

## Status

**Implemented and locally validated. GitHub upload and hosted Actions confirmation pending.**

P5-04 applies the four code-only refinements approved in P5-03, reruns the complete unchanged v1.0.1 frozen suite, demonstrates configuration portability across the ICM reference profile and a fictional small-business profile, and introduces a continuous-integration quality gate for the refined baseline.

## Frozen-Suite Refinement Results

| Measure | Before | After |
|---|---:|---:|
| Cases executed | 19/19 | 19/19 |
| Fully conformant cases | 13/19 | 19/19 |
| Assertions passed | 256/262 | 262/262 |
| Audit-event classification | 15/19 | 19/19 |
| Primary-component attribution | 17/19 | 19/19 |
| Critical assertion failures | 0 | 0 |
| Regressions | — | 0 |
| External actions | 0 | 0 |

The six improved cases are `TC-03`, `TC-05`, `TC-10`, `TC-14`, `TC-15`, and `TC-18`. Frozen cases, expected outcomes, assertion severities, model-confidence thresholds, evidence-sufficiency thresholds, and original P5-01 results were not changed.

## Implemented Refinements

1. **Abstention semantics:** R-03 and R-06 outcomes caused by insufficient structured information, missing citation, stale evidence, or insufficient evidence now emit `recommendation_abstained`.
2. **Mandatory specialist routing:** cases routed to mandatory specialist review now emit `case_escalated` even when the terminal label remains `deferred`.
3. **Privacy processing interruption:** sensitive-data interruption now emits `processing_failed` before specialist escalation.
4. **Global control ownership:** decisive external-action, override, and audit-persistence safeguards are attributed to `workflow_orchestrator`, while the stage executor remains visible in the interpretable trace.

## Configuration-Portability Results

The same executable functions were run against two synthetic opportunities and two organization profiles. Only the profile path changed.

| Opportunity | ICM Alignment / Recommendation | Fictional Alignment / Recommendation |
|---|---|---|
| Enterprise IT strategy, program management, and systems integration | strong, 1.0000 / `R-01` | none, 0.0000 / `R-04` |
| Public-sector cloud data platform, analytics, and dashboards | none, 0.1167 / `R-04` | strong, 1.0000 / `R-01` |

The profile switch changed alignment and screening recommendations for both opportunities while preserving the same source-code hash, shared schemas, alignment policy, fixed safeguards, human-final-decision requirement, and external-action prohibition. All recommendations remain nonbinding and all final decisions remain `null`.

## CI Quality Gate

The repository now includes `.github/workflows/project7-quality-gate.yml`. It runs on pushes and pull requests to `main` and by manual dispatch. It uses read-only repository permissions, Python 3.12, pip dependency caching, schema/contract/safeguard checks, prior evaluation verifiers, P5-04 regression and portability verification, repository credential and large-file checks, and workflow artifact upload.

This is deliberately **continuous integration**, not deployment. It does not publish a package, deploy an application, invoke an external system, or claim production readiness.

## Preserved Evidence

```text
outputs/evaluation/p5_04/refined_run_manifest.json
outputs/evaluation/p5_04/refined_case_results/
outputs/evaluation/p5_04/refined_case_traces/
outputs/evaluation/p5_04/before_after_metrics.json
outputs/evaluation/p5_04/portability/portability_comparison.json
outputs/ci/local-project7-quality-gate.log
audit/p5_04_refined_evaluation_ledger.jsonl
audit/p5_04_portability_ledger.jsonl
.github/workflows/project7-quality-gate.yml
```

## Local Quality-Gate Result

```text
Repository files checked: 753
Credential-pattern hits: 0
Files over 100 MB: 0
Merge-conflict markers: 0
Notebook traceback outputs: 0
Required final-baseline files present: PASS
CI repository checks: PASS
Schemas checked: 32
Valid integrated case: PASS
Valid audit event: PASS
Invalid integrated case: correctly rejected with 1 validation error(s)
Component contracts checked: 14
Contract registry integrity: PASS
Orchestration policy: PASS
Stage-to-contract referential integrity: PASS
Invalid component contract: correctly rejected
Invalid orchestration policy: correctly rejected
Safeguard controls checked: 30
Reason codes checked: 35
Trigger scenarios checked: 30
Policy schema validation: PASS
Control and reason-code integrity: PASS
Control-to-scenario coverage: PASS
Invalid safeguard policy: correctly rejected
Actors checked: 8
Approved inputs checked: 8
Workflow stages checked: 12
Human decision points checked: 6
Acceptance targets checked: 18
CPU and no-training boundary: PASS
Stage, actor, and decision integrity: PASS
Invalid operational workload: correctly rejected
Scenario categories checked: 11
Target cases checked: 19
Terminal outcomes covered: 6
No Recommendation modeled separately: PASS
Category minimum coverage: PASS
Cases verified: 19
Assertions verified: 262
Raw output integrity: PASS
Frozen evaluation verification: PASS
Metrics recalculated and verified: 14
Cases: 19
Assertions: 256/262
Critical assertions: 167/167
Major assertions: 89/95
P5-02 recalculation: PASS
Failure occurrences verified: 6
Failure classes verified: 3
Safety-significant failures: 0
Governance-significant failures: 6
Unexpected escalations: 0
Refinement backlog items: 5
P5-03 failure analysis verification: PASS
Frozen inputs verified unchanged: PASS
Cases executed: 19/19
Assertions passed: 262/262
Improved cases: 6
Regressions: 0
Audit event classification: 19/19
Component attribution: 19/19
P5-04 refinement verification: PASS
Portability opportunities: 2
Profile runs: 4
ICM-oriented result: R-01 vs R-04
Data-analytics result: R-04 vs R-01
Source code, schemas, and fixed safeguards unchanged: PASS
P5-04 portability verification: PASS
test_all_cases_and_assertions_pass (tests.test_refined_evaluation.RefinedEvaluationTests.test_all_cases_and_assertions_pass) ... ok
test_audit_event_classification_improved (tests.test_refined_evaluation.RefinedEvaluationTests.test_audit_event_classification_improved) ... ok
test_component_attribution_improved (tests.test_refined_evaluation.RefinedEvaluationTests.test_component_attribution_improved) ... ok
test_exact_six_cases_improved (tests.test_refined_evaluation.RefinedEvaluationTests.test_exact_six_cases_improved) ... ok
test_external_action_boundary (tests.test_refined_evaluation.RefinedEvaluationTests.test_external_action_boundary) ... ok
test_frozen_inputs_unchanged (tests.test_refined_evaluation.RefinedEvaluationTests.test_frozen_inputs_unchanged) ... ok
test_global_control_owner_attribution (tests.test_refined_evaluation.RefinedEvaluationTests.test_global_control_owner_attribution) ... ok
test_no_regressions (tests.test_refined_evaluation.RefinedEvaluationTests.test_no_regressions) ... ok
test_raw_output_inventory_exists (tests.test_refined_evaluation.RefinedEvaluationTests.test_raw_output_inventory_exists) ... ok
test_refined_event_semantics (tests.test_refined_evaluation.RefinedEvaluationTests.test_refined_event_semantics) ... ok
test_all_runs_preserve_human_authority (tests.test_configuration_portability.ConfigurationPortabilityTests.test_all_runs_preserve_human_authority) ... ok
test_data_opportunity_changes_result_in_reverse (tests.test_configuration_portability.ConfigurationPortabilityTests.test_data_opportunity_changes_result_in_reverse) ... ok
test_external_action_boundary (tests.test_configuration_portability.ConfigurationPortabilityTests.test_external_action_boundary) ... ok
test_fixed_safeguards_and_schemas_are_unchanged (tests.test_configuration_portability.ConfigurationPortabilityTests.test_fixed_safeguards_and_schemas_are_unchanged) ... ok
test_icm_oriented_opportunity_changes_result (tests.test_configuration_portability.ConfigurationPortabilityTests.test_icm_oriented_opportunity_changes_result) ... ok
test_profile_switch_changes_alignment_and_recommendation (tests.test_configuration_portability.ConfigurationPortabilityTests.test_profile_switch_changes_alignment_and_recommendation) ... ok
test_source_code_is_unchanged (tests.test_configuration_portability.ConfigurationPortabilityTests.test_source_code_is_unchanged) ... ok
test_two_opportunities_and_two_profiles (tests.test_configuration_portability.ConfigurationPortabilityTests.test_two_opportunities_and_two_profiles) ... ok
test_current_official_action_majors (tests.test_ci_workflow.CIWorkflowTests.test_current_official_action_majors) ... ok
test_evidence_is_uploaded (tests.test_ci_workflow.CIWorkflowTests.test_evidence_is_uploaded) ... ok
test_final_quality_verifiers_are_run (tests.test_ci_workflow.CIWorkflowTests.test_final_quality_verifiers_are_run) ... ok
test_no_deployment_or_publish_step (tests.test_ci_workflow.CIWorkflowTests.test_no_deployment_or_publish_step) ... ok
test_pinned_python_and_dependency_cache (tests.test_ci_workflow.CIWorkflowTests.test_pinned_python_and_dependency_cache) ... ok
test_read_only_permissions (tests.test_ci_workflow.CIWorkflowTests.test_read_only_permissions) ... ok
test_triggers_cover_push_pull_request_and_manual (tests.test_ci_workflow.CIWorkflowTests.test_triggers_cover_push_pull_request_and_manual) ... ok

----------------------------------------------------------------------
Ran 25 tests in 0.001s

OK
```

The hosted GitHub Actions run is intentionally pending until the workflow is committed to the public repository.

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.
