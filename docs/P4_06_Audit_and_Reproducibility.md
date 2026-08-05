# P4-06 — Audit and Reproducibility Outputs

## Status

**Implemented and locally validated.**

P4-06 closes Phase 4 by preserving the integrated case as a traceable, checksum-verifiable, replayable workflow. It inventories replay-critical artifacts, records configuration and component versions, consolidates the full audit ledger, validates event hashes and links, verifies deterministic reconstruction of the final packet, documents all replay commands and dependencies, and preserves the final human-review route.

## Representative Results

| Measure | Result |
|---|---|
| Inventoried artifacts | `130` |
| Audit events | `13` |
| Audit range | `AUD-CASE-D850D326D21B745D-01` through `AUD-CASE-D850D326D21B745D-13` |
| Artifact integrity | `PASS` |
| Audit-chain integrity | `PASS` |
| Deterministic packet replay | `PASS` |
| Final route | `awaiting_human_review` |
| Human disposition | `null` |
| Final decision | `null` |
| External actions | `0` |

## Durable Reproducibility Outputs

```text
outputs/p4_06/reproducibility_manifest.json
outputs/p4_06/audit_chain_summary.json
outputs/p4_06/replay_verification.json
outputs/p4_06/final_routing_record.json
outputs/p4_06/replay_plan.json
audit/p4_06_consolidated_case_ledger.jsonl
audit/p4_06_reproducibility_events.jsonl
audit/p4_06_artifact_checksums.csv
scripts/verify_p4_06_reproducibility.py
```

## Replay Modes

### 1. Artifact verification

```bash
python scripts/verify_p4_06_reproducibility.py
```

This verifies every inventoried file's presence, size, and SHA-256 and revalidates the complete 13-event audit chain.

### 2. Deterministic packet replay

```bash
python tests/run_p4_06_validation.py
```

This reconstructs the P4-05 recommendation, decision-support packet, updated case state, and audit outputs from the preserved P4-04 case state. Canonical JSON hashes must match the preserved outputs exactly.

### 3. Full phase re-execution

```bash
python tests/run_p4_01_validation.py
python tests/run_p4_02_validation.py
python tests/run_p4_03_validation.py
python tests/run_p4_04_validation.py
python tests/run_p4_05_validation.py
python tests/run_p4_06_validation.py
```

Full P4-03 re-execution requires the committed Project 4 model package under `models/project4`. The approved checkpoint SHA-256 is:

```text
50a280950d31466d7002578295c64e957d144611f5b9731bb059be50e68c6c92
```

## Audit Chain

The consolidated ledger preserves events 1 through 13:

1. Case creation
2. Opportunity normalization
3. Organization profile loading
4. Service alignment
5. Historical context attachment
6. Clause-theme triage
7. Evidence retrieval
8. Evidence validation
9. Human escalation
10. Nonbinding recommendation creation
11. Human-review packet routing
12. Reproducibility manifest creation
13. Replay verification

Every event hash is recomputed from canonical JSON, and every `previous_event_hash` must match the preceding event.

## Human Authority

The final route remains:

```text
awaiting_human_review
```

with recommendation:

```text
R-05 — Escalate — Specialized Review Required
```

The human disposition and final decision remain `null`. P4-06 verifies and preserves that boundary; it does not complete or simulate a human decision.

## Validation

```text
test_audit_chain_contains_events_one_through_thirteen (tests.test_reproducibility.ReproducibilityTests.test_audit_chain_contains_events_one_through_thirteen) ... ok
test_audit_hash_mutation_is_detected (tests.test_reproducibility.ReproducibilityTests.test_audit_hash_mutation_is_detected) ... ok
test_checksum_mutation_is_detected (tests.test_reproducibility.ReproducibilityTests.test_checksum_mutation_is_detected) ... ok
test_deterministic_packet_replay_passes (tests.test_reproducibility.ReproducibilityTests.test_deterministic_packet_replay_passes) ... ok
test_final_route_preserves_human_authority (tests.test_reproducibility.ReproducibilityTests.test_final_route_preserves_human_authority) ... ok
test_full_reexecution_dependency_is_disclosed (tests.test_reproducibility.ReproducibilityTests.test_full_reexecution_dependency_is_disclosed) ... ok
test_inventory_has_no_missing_or_mismatched_files (tests.test_reproducibility.ReproducibilityTests.test_inventory_has_no_missing_or_mismatched_files) ... ok
test_manifest_is_schema_valid (tests.test_reproducibility.ReproducibilityTests.test_manifest_is_schema_valid) ... ok
test_replay_plan_lists_all_phase_four_commands (tests.test_reproducibility.ReproducibilityTests.test_replay_plan_lists_all_phase_four_commands) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.216s

OK
Inventoried artifacts: 130
Consolidated audit events: 13
Audit event range: AUD-CASE-D850D326D21B745D-01 through AUD-CASE-D850D326D21B745D-13
Repository state digest: 4cd07ab3a1f8286caeeb8268e41655a6484935a3b8ab860df029781f1247fd10
Artifact integrity: PASS
Audit-chain integrity: PASS
Deterministic packet replay: PASS
Final route: awaiting_human_review
Human disposition recorded: False
Final decision created: False
External actions performed: 0
```

## Production Boundary

Controlled capstone prototype; nonbinding recommendations only; no autonomous external action; final human authority required.

This controlled replay establishes artifact integrity and deterministic behavior for the representative case. It does not establish production security, scalability, operational resilience, legal correctness, or autonomous decision authority.
