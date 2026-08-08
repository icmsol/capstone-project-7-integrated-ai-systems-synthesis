# P4-03 — Bounded Clause-Theme Inference

> **P6-02 current-status clarification (2026-08-08):** The “requires one CPU Colab run after upload” statement below is historical. Actual repository-model execution was completed and preserved in `notebooks/P4_03_Bounded_Clause_Triage_Validation.ipynb`, then exercised through operator acceptance. Public-sector results remain bounded by `MODEL_DOMAIN_SHIFT`; confidence is not legal or semantic correctness. Any unrelated spreadsheet-runtime warmup traceback below is not a Project 4 inference failure.

## Status

**Implementation and controlled validation complete. Actual repository-model wrapper execution requires one CPU Colab run after upload.**

P4-03 reconstructs the Project 4 Transformer inference architecture, loads its checkpoint and companion artifacts, verifies the package fingerprint, produces a ten-class probability vector, and applies fixed abstention, truncation, domain-shift, and human-review controls.

## Decision Rules

| Condition | Behavior |
|---|---|
| Confidence at least 0.80, commercial-contract domain, no truncation | `classify` |
| Confidence below 0.80 | `abstain` with `MODEL_CONFIDENCE_LOW` |
| Input exceeds 256 tokens | `escalate` with `MODEL_INPUT_TRUNCATED` |
| Public-sector consequential use | `escalate` with `MODEL_DOMAIN_SHIFT` |
| Empty input | fail closed with `MODEL_INPUT_INVALID` |
| Package mismatch | fail closed with `MODEL_PACKAGE_INVALID` |

## Controlled Validation

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
test_compatible_package_loads_and_predicts (tests.test_clause_triage.ClauseTriageTests.test_compatible_package_loads_and_predicts) ... /opt/pyvenv/lib/python3.13/site-packages/torch/nn/modules/transformer.py:531: UserWarning: The PyTorch API of nested tensors is in prototype stage and will change in the near future. We recommend specifying layout=torch.jagged when constructing a nested tensor, as this layout receives active development, has better operator coverage, and works with torch.compile. (Triggered internally at /pytorch/aten/src/ATen/NestedTensorImpl.cpp:178.)
  output = torch._nested_tensor_from_mask(
ok
test_empty_passage_fails_closed (tests.test_clause_triage.ClauseTriageTests.test_empty_passage_fails_closed) ... ok
test_high_confidence_commercial_text_classifies (tests.test_clause_triage.ClauseTriageTests.test_high_confidence_commercial_text_classifies) ... ok
test_low_confidence_abstains (tests.test_clause_triage.ClauseTriageTests.test_low_confidence_abstains) ... ok
test_public_sector_consequential_use_escalates (tests.test_clause_triage.ClauseTriageTests.test_public_sector_consequential_use_escalates) ... ok
test_schema_and_prohibited_claim_boundary (tests.test_clause_triage.ClauseTriageTests.test_schema_and_prohibited_claim_boundary) ... ok
test_truncation_escalates_and_is_disclosed (tests.test_clause_triage.ClauseTriageTests.test_truncation_escalates_and_is_disclosed) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.070s

OK
Controlled predictions: 3
Compatible model package load: PASS
Confidence abstention: PASS
Public-sector escalation: PASS
Truncation disclosure: PASS
Schema validation: PASS
External actions performed: 0
Actual Project 4 P4-03 wrapper run: PENDING COLAB CPU
```

The controlled fixture validates implementation behavior and schemas. It is not a new model-performance result.

## Actual Project 4 Evidence

The committed Project 4 package previously passed CPU loading and prediction with:

- checkpoint SHA-256: `50a280950d31466d7002578295c64e957d144611f5b9731bb059be50e68c6c92`
- ten output classes;
- output shape `[1, 10]`;
- prior predicted category `Audit Rights`;
- prior confidence `0.9997158647`;
- finite probabilities summing to one.

## Final P4-03 Validation

Run the supplied CPU notebook after the package is committed:

```text
notebooks/P4_03_Bounded_Clause_Triage_Validation.ipynb
```

It executes three public-sector representative passages through the actual repository model package and validates the updated case state and sixth audit event.

## Boundary

The model output is review triage only. It cannot establish legal meaning, enforceability, compliance, contract acceptability, required contractual action, or final disposition. Public-sector consequential use requires qualified human review.

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.
