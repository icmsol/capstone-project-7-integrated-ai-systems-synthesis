# Tests and Validation

This directory contains the executable validation and regression suite used throughout Project 7.

## Test Categories

### Shared contracts and safeguards

- `validate_shared_schemas.py`
- `validate_component_contracts.py`
- `validate_safeguards.py`
- `validate_operational_workload.py`
- `validate_scenario_taxonomy.py`
- `validate_prior_project_traceability.py`

### Component / integrated behavior

Representative tests include:

- `test_opportunity_intake.py`
- `test_alignment_history.py`
- `test_clause_triage.py`
- `test_evidence_workflow.py`
- `test_decision_support_packet.py`
- `test_human_disposition_recorder.py`
- `test_operator_workflow.py`
- `test_reproducibility.py`

### Evaluation and freeze regression

- `test_frozen_evaluation.py`
- `test_system_metrics.py`
- `test_failure_analysis.py`
- `test_refined_evaluation.py`
- `test_configuration_portability.py`
- `test_final_evaluation_freeze.py`
- `test_acceptance_corrected_baseline.py`
- `test_p5_12_operator_hardening.py`
- `test_p5_12_final_submission_candidate.py`

### Controlled execution helpers

`run_p4_*`, `run_p5_*`, `calculate_p5_02_metrics.py`, and verification helpers preserve activity-specific validation/reproduction paths.

## Fixture Directories

- `contract_examples/`
- `fixtures/`
- `frozen_scenario_examples/`
- `safeguard_examples/`
- `scenario_taxonomy_examples/`
- `schema_examples/`
- `traceability_examples/`
- `workload_examples/`

## Hosted Quality Gate

The live workflow is [`../.github/workflows/project7-quality-gate.yml`](../.github/workflows/project7-quality-gate.yml).

The final workflow executes repository-integrity checks, schema/contract/safeguard validation, evaluation/freeze verifiers, operator-interface validation, P5-12 hardening verification, final-candidate verification, and the regression/unit test suite.

The final submission-candidate regression can be run directly with:

```bash
python scripts/verify_p5_12_final_submission_candidate.py
python -m unittest tests.test_p5_12_final_submission_candidate -v
```

Run those commands from the repository root.

Tests demonstrate controlled prototype behavior; they do not establish production readiness or complete live-source coverage.
