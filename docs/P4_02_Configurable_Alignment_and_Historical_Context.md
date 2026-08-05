# P4-02 — Configurable Organization Alignment and Historical Context

## Implementation Status

**Implemented and locally validated.**

P4-02 loads the active organization profile and referenced CSV/JSON configuration, applies exclusion-first transparent service matching, maps service families to staffing families, attaches checksum-verified descriptive Project 2 historical context, updates the integrated case state, and continues the audit hash chain.

## Representative ICM Result

| Measure | Result |
|---|---|
| Alignment label | `strong_alignment` |
| Alignment score | `1.0000` |
| Matched capabilities | 5 |
| Staffing families | Application and Integration Delivery, Change and Learning, Program Delivery and Oversight, Strategy and Architecture |
| Historical source records | 29,646 |
| Matched historical records | 122 |
| Updated case status | `analysis_in_progress` |

### Matched capabilities

| Capability | Name | Family | Strength | Exact matched terms |
|---|---|---|---|---|
| `ICM-PM-001` | Project and Program Management | `SF03` | **strong** | program management |
| `ICM-OCM-005` | Technical Training and Knowledge Transfer | `SF06` | **strong** | technical training |
| `ICM-ITS-001` | IT Strategic Planning | `SF01` | **strong** | it strategy |
| `ICM-CDI-005` | Systems Integration and API Enablement | `SF02` | **strong** | systems integration |
| `ICM-PM-006` | Waterfall, Agile, Hybrid, and Client-Specific Delivery | `SF03` | **weak** | agile |

### Matched historical categories

| Project 2 service category | Historical records |
|---|---:|
| IT Consulting & Staff Augmentation | 20 |
| Organizational Change, Training & Process | 14 |
| Project Management, IV&V & Quality | 9 |
| Software Development & Systems Integration | 79 |

## Portability Result

The identical opportunity and code path were evaluated under the fictional Redwood Civic Analytics profile:

| Profile | Active capabilities | Alignment |
|---|---:|---|
| ICM Solutions | 54 | `strong_alignment` |
| Fictional alternate | 3 | `no_alignment` |

The result changes because the configuration changes—not because the Python implementation contains organization-specific branches.

## Historical Asset Boundary

Project 2 analyzed **29,646** historical records from **2021-07-01 through 2026-06-30** and identified **176** ICM-relevant opportunities using transparent title-based rules. The compact Project 7 asset retains only deidentified aggregate service-category and staffing-family counts. Buyer names and emails from the source dataset are not copied into Project 7.

Historical counts are expressly:

- descriptive rather than predictive;
- not contract-value estimates;
- not labor-hour or capacity estimates;
- not evidence of eligibility or complete scope fit;
- not award-probability estimates;
- not a current demand forecast.

## Executable Files

```text
src/project7/profile_loader.py
src/project7/service_alignment.py
src/project7/historical_context.py
src/project7/audit_utils.py
src/project7/p4_02_pipeline.py
```

## Validation

Run from the repository root:

```bash
python tests/run_p4_02_validation.py
```

Validation output:

```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/generated/interface/models.py", line 30820, in hydrate_crdt_from_proto
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/rpc/remote.py", line 749, in __call__
  File "/tmp/tmp.yTcnQsZYiA/artifact_tool_v2-2.8.4/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.
test_asset_checksum_change_warns_and_stops_context_use (tests.test_alignment_history.AlignmentHistoryTests.test_asset_checksum_change_warns_and_stops_context_use) ... ok
test_exclusion_first_blocks_positive_capability (tests.test_alignment_history.AlignmentHistoryTests.test_exclusion_first_blocks_positive_capability) ... ok
test_historical_context_is_descriptive_and_checksum_verified (tests.test_alignment_history.AlignmentHistoryTests.test_historical_context_is_descriptive_and_checksum_verified) ... ok
test_profile_loader_is_configuration_driven (tests.test_alignment_history.AlignmentHistoryTests.test_profile_loader_is_configuration_driven) ... ok
test_same_opportunity_changes_by_profile_without_code_change (tests.test_alignment_history.AlignmentHistoryTests.test_same_opportunity_changes_by_profile_without_code_change) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.100s

OK
ICM active capabilities / service families: 54 / 8
ICM alignment: strong_alignment / 1.0000
Fictional profile alignment: no_alignment / 0.0000
Matched historical records: 122
Historical context descriptive only: PASS
Profile portability without code changes: PASS
Audit hash-chain continuation: PASS
External actions performed: 0
```

## Sources

- https://github.com/icmsol/Capstone-project-2-statistical-analysis
- https://raw.githubusercontent.com/icmsol/Capstone-project-2-statistical-analysis/main/data/processed/analysis_summary.json
- https://raw.githubusercontent.com/icmsol/Capstone-project-2-statistical-analysis/main/data/processed/icm_relevant_historical_bids.csv

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.
