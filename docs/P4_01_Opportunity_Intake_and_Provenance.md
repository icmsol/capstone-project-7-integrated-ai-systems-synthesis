# P4-01 — Opportunity Intake and Provenance

## Implementation Status

**Implemented and locally validated.**

The P4-01 component accepts one approved raw opportunity, verifies its exact source bytes, normalizes the record, preserves all original values, identifies missing information without inferring it, assigns deterministic identifiers, creates an initial integrated case state, and writes two append-only audit events.

## Representative Result

| Field | Value |
|---|---|
| Opportunity ID | `OPP-E19200F7BD6C3161` |
| Case ID | `CASE-D850D326D21B745D` |
| Case Status | `intake_validated` |
| Record Key | `d850d326d21b745d1bc1` |
| Source SHA-256 | `e152ac2dad41a7e34e41cf27742fb7c0e05aafd46e5d68d9a42f0ef00c00b7c2` |
| Audit Events | `AUD-CASE-D850D326D21B745D-01, AUD-CASE-D850D326D21B745D-02` |

## Files

### Executable component

```text
src/project7/opportunity_intake.py
src/project7/schema_validation.py
```

### Configuration

```text
config/system/opportunity_intake_rules.json
config/system/p4_01_reference_organization_context.json
```

The organization context is an already-validated upstream input. Full configurable profile loading and capability alignment remain P4-02 work.

### Representative input and outputs

```text
data/implementation/p4_01/raw_opportunity.json
data/implementation/p4_01/source_approval.json
outputs/p4_01/normalized_opportunity.json
outputs/p4_01/initial_case_state.json
audit/p4_01_intake_events.jsonl
```

## Observable Behavior

The component:

1. blocks an unapproved source;
2. defers when an approved checksum no longer matches;
3. rejects credential-like values before persistence;
4. normalizes text, status, and timestamps;
5. retains the original source values;
6. records missing optional fields and a material limitation;
7. derives stable case, opportunity, and record identifiers;
8. validates all output artifacts against committed schemas;
9. creates a valid audit hash chain;
10. performs no external action.

## Validation

Run from the repository root:

```bash
python tests/run_p4_01_validation.py
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
test_checksum_change_defers (tests.test_opportunity_intake.OpportunityIntakeTests.test_checksum_change_defers) ... ok
test_replay_is_deterministic (tests.test_opportunity_intake.OpportunityIntakeTests.test_replay_is_deterministic) ... ok
test_sparse_source_preserves_missing_fields (tests.test_opportunity_intake.OpportunityIntakeTests.test_sparse_source_preserves_missing_fields) ... ok
test_unapproved_source_fails_closed (tests.test_opportunity_intake.OpportunityIntakeTests.test_unapproved_source_fails_closed) ... ok
test_valid_intake_is_schema_valid_and_traceable (tests.test_opportunity_intake.OpportunityIntakeTests.test_valid_intake_is_schema_valid_and_traceable) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.114s

OK
Representative normalized opportunity: OPP-E19200F7BD6C3161
Initial case state: CASE-D850D326D21B745D / intake_validated
Source SHA-256 recorded and validated: PASS
Original values retained without material inference: PASS
Audit hash chain: PASS
Schema validation: PASS
External actions performed: 0
```

## Design Boundary

This component does not score service alignment, attach historical demand, classify contract clauses, retrieve official evidence, create a recommendation, or make a decision. Those responsibilities remain in later registered components.

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.
