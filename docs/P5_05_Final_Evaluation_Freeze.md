# P5-05 — Final Evaluation Freeze

## Status

**Final baseline frozen and locally validated. Updated hosted quality-gate run pending.**

P5-05 freezes the refined Project 7 evaluation evidence as baseline `PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.0`. The frozen baseline preserves the original P5-01 results, P5-02 metrics, P5-03 failure analysis, P5-04 refinements, configuration-portability evidence, repository inventory, and automated quality controls.

## Final Results

| Measure | Final Result |
|---|---:|
| Frozen cases executed | 19/19 |
| Full-case conformance | 19/19 |
| Assertions passed | 262/262 |
| Critical assertions | 167/167 |
| Major assertions | 95/95 |
| Recommendation screening agreement | 13/13 |
| Terminal outcome agreement | 19/19 |
| Human routing agreement | 19/19 |
| Escalation recall | 3/3 |
| Fail-closed recall | 6/6 |
| Evidence-control agreement | 5/5 |
| Traceability completeness | 19/19 |
| Unsupported-claim prevention | 19/19 |
| Audit-event classification | 19/19 |
| Component attribution | 19/19 |
| External actions | 0 |

Six cases improved during P5-04 and no previously passing case regressed.

## Configuration Portability

The same executable code evaluated two opportunities under both the ICM profile and a fictional small-business profile. The profile switch changed alignment and nonbinding recommendations in both directions while preserving schemas, fixed safeguards, human final authority, and the prohibition against autonomous external action.

## Continuous Integration

The workflow now uses:

```text
actions/checkout@v5
actions/setup-python@v6
actions/upload-artifact@v7
Python 3.12
read-only repository permissions
```

The v7 update replaces the warning-producing `upload-artifact@v4` step. The final hosted run must succeed and retain at least one artifact before P5-05 is closed.

## Freeze Outputs

```text
outputs/evaluation/p5_05/final_evaluation_baseline.json
outputs/evaluation/p5_05/final_metric_summary.json
outputs/evaluation/p5_05/final_metric_summary.csv
outputs/evaluation/p5_05/final_evidence_map.json
outputs/evaluation/p5_05/final_evidence_map.csv
outputs/evaluation/p5_05/final_artifact_inventory.json
outputs/evaluation/p5_05/final_artifact_inventory.csv
outputs/evaluation/p5_05/repository_validation_report.json
config/system/final_evaluation_freeze_policy.json
```


## Notebook Verification Policy

Jupyter notebooks are frozen using a canonical source digest rather than raw
byte size. Colab and GitHub may add execution outputs, execution counts, cell
IDs, volatile metadata, or a duplicate badge-only cell when an executed
notebook is saved. Those changes do not alter the executable code.

The canonical digest preserves:

- notebook format version;
- ordered code-cell source;
- ordered substantive markdown source.

It excludes:

- outputs and execution counts;
- cell and Colab metadata;
- duplicate standalone Colab badge cells.

All non-notebook files continue to require exact raw size and SHA-256 matches.

## Immutability

The P5-01 and P5-04 raw results, frozen scenarios, expected outcomes, thresholds, and historical failure evidence may not be silently edited after this freeze. Any material change requires a new explicit version and a complete rerun.

## Hosted CI Run #1

Run #1 succeeded in 24 seconds and retained one artifact. It produced one non-blocking Node.js deprecation warning from `actions/upload-artifact@v4`. The workflow is upgraded to v7 in this package, and an updated hosted run is the final completion gate.

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.
