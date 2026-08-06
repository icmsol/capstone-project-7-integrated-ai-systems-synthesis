# P5-02 — System-Level Metrics

## Status

**Calculated and locally validated. GitHub upload pending.**

P5-02 calculates system-level metrics directly from the preserved P5-01 raw results and frozen v1.0.1 expected outcomes. Each metric records its applicable population, numerator, denominator, formula-derived value, target type, matched cases, unmatched cases, and interpretation.

No threshold or denominator was changed after observing the P5-01 results. Safety gates retain fixed 100% requirements; diagnostic metrics are reported descriptively.

## Results

| Metric | Name | Numerator / Denominator | Value | Target Status |
|---|---|---:|---:|---|
| `M-01` | Workflow Completion Rate | 19/19 | 100.00% | met |
| `M-02` | Full-Case Conformance Rate | 13/19 | 68.42% | descriptive |
| `M-03` | Assertion Conformance Rate | 256/262 | 97.71% | descriptive |
| `M-04` | Critical Assertion Conformance | 167/167 | 100.00% | met |
| `M-05` | Recommendation Screening Agreement | 13/13 | 100.00% | descriptive |
| `M-06` | Terminal Outcome Agreement | 19/19 | 100.00% | descriptive |
| `M-07` | Human Routing Agreement | 19/19 | 100.00% | met |
| `M-08` | Escalation Recall | 3/3 | 100.00% | met |
| `M-09` | Fail-Closed Recall | 6/6 | 100.00% | met |
| `M-10` | Citation and Evidence-Control Agreement | 5/5 | 100.00% | descriptive |
| `M-11` | Traceability Completeness | 19/19 | 100.00% | met |
| `M-12` | Unsupported-Claim Prevention | 19/19 | 100.00% | met |
| `M-13` | Audit Event Classification Conformance | 15/19 | 78.95% | descriptive |
| `M-14` | Primary Component Attribution Agreement | 17/19 | 89.47% | descriptive |

## Core Findings

- Workflow completion: **19/19**
- Full-case conformance: **13/19**
- Assertion conformance: **256/262**
- Critical assertion conformance: **167/167**
- Recommendation screening agreement: **13/13 applicable cases**
- Terminal outcome agreement: **19/19**
- Human routing agreement: **19/19**
- Escalation recall: **3/3**
- Fail-closed recall: **6/6**
- Citation and evidence-control agreement: **5/5**
- Traceability completeness: **19/19**
- Unsupported-claim prevention: **19/19**

## Diagnostic Gaps

The six failed assertions are all major severity:

| Case | Assertion | Target | Severity |
|---|---|---|---|
| `TC-03` | `AS-TC-03-AUDIT` | `$.audit.event_types` | major |
| `TC-05` | `AS-TC-05-AUDIT` | `$.audit.event_types` | major |
| `TC-10` | `AS-TC-10-AUDIT` | `$.audit.event_types` | major |
| `TC-14` | `AS-TC-14-COMP` | `$.case_state.primary_component` | major |
| `TC-15` | `AS-TC-15-AUDIT` | `$.audit.event_types` | major |
| `TC-18` | `AS-TC-18-COMP` | `$.case_state.primary_component` | major |

Four concern audit-event classification and two concern primary-component attribution. None changes the terminal outcome, recommendation, human route, escalation, fail-closed behavior, traceability, unsupported-claim boundary, or external-action boundary.

## Denominator Discipline

Recommendation agreement excludes cases with no expected recommendation. Escalation and fail-closed recall include only their respective expected populations. Evidence-control agreement includes CAT-04 and CAT-05. Traceability and unsupported-claim prevention include all 19 cases.

## Preserved Outputs

```text
outputs/evaluation/p5_02/system_metrics.json
outputs/evaluation/p5_02/system_metrics.csv
outputs/evaluation/p5_02/category_metrics.csv
outputs/evaluation/p5_02/assertion_type_metrics.csv
outputs/evaluation/p5_02/case_outcome_matrix.csv
outputs/evaluation/p5_02/failed_assertions.csv
config/system/system_metric_definitions.json
```

## Validation

```text
Metrics recalculated and verified: 14
Cases: 19
Assertions: 256/262
Critical assertions: 167/167
Major assertions: 89/95
P5-02 recalculation: PASS
```

```text

test_complete_population (tests.test_system_metrics.SystemMetricTests.test_complete_population) ... ok
test_completion_and_conformance (tests.test_system_metrics.SystemMetricTests.test_completion_and_conformance) ... ok
test_diagnostics_preserve_mismatches (tests.test_system_metrics.SystemMetricTests.test_diagnostics_preserve_mismatches) ... ok
test_escalation_and_fail_closed_recall (tests.test_system_metrics.SystemMetricTests.test_escalation_and_fail_closed_recall) ... ok
test_evidence_traceability_and_claim_controls (tests.test_system_metrics.SystemMetricTests.test_evidence_traceability_and_claim_controls) ... ok
test_external_action_boundary (tests.test_system_metrics.SystemMetricTests.test_external_action_boundary) ... ok
test_no_retroactive_thresholds (tests.test_system_metrics.SystemMetricTests.test_no_retroactive_thresholds) ... ok
test_screening_terminal_and_route (tests.test_system_metrics.SystemMetricTests.test_screening_terminal_and_route) ... ok
test_severity_summary (tests.test_system_metrics.SystemMetricTests.test_severity_summary) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.000s

OK
```

Detailed root-cause, impact, mitigation, and residual-risk analysis is deferred to **P5-03**.

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.
