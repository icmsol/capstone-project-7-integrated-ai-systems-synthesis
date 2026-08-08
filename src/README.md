# Source Code

The integrated reusable Python implementation is under [`project7/`](project7/).

## Operator Layer

- [`project7/operator_ui.py`](project7/operator_ui.py) — seven-stage reviewer-facing Colab interface and hardened packet presentation.
- [`project7/operator_workflow.py`](project7/operator_workflow.py) — operator-stage orchestration, runtime workspace management, and resumable case bundles.

## Intake, Configuration, and Context

- [`project7/opportunity_intake.py`](project7/opportunity_intake.py) — normalized intake and provenance.
- [`project7/profile_loader.py`](project7/profile_loader.py) — organization profile loading/validation.
- [`project7/service_alignment.py`](project7/service_alignment.py) — configuration-driven capability alignment.
- [`project7/historical_context.py`](project7/historical_context.py) — descriptive frozen Project 2 context.
- [`project7/configuration_portability.py`](project7/configuration_portability.py) — controlled profile-switch portability evaluation.

## Clause and Evidence Workflow

- [`project7/clause_triage.py`](project7/clause_triage.py) — bounded Project 4 inference wrapper and domain-shift controls.
- [`project7/evidence_retrieval.py`](project7/evidence_retrieval.py) — deterministic bounded evidence retrieval.
- [`project7/evidence_workflow.py`](project7/evidence_workflow.py) — evidence request, validation, sufficiency, and escalation workflow.

## Recommendation and Human Authority

- [`project7/recommendation_engine.py`](project7/recommendation_engine.py) — nonbinding recommendation logic.
- [`project7/decision_support_packet.py`](project7/decision_support_packet.py) — canonical packet assembly.
- [`project7/human_disposition.py`](project7/human_disposition.py) — separate authorized human disposition recording.

## Evaluation, Audit, and Reproducibility

- [`project7/frozen_evaluation.py`](project7/frozen_evaluation.py) — frozen/refined evaluation execution.
- [`project7/audit_utils.py`](project7/audit_utils.py) — audit event utilities.
- [`project7/reproducibility.py`](project7/reproducibility.py) — reproducibility support.
- [`project7/schema_validation.py`](project7/schema_validation.py) — schema validation helpers.

## Integrated Stage Pipelines

- [`project7/p4_02_pipeline.py`](project7/p4_02_pipeline.py)
- [`project7/p4_03_pipeline.py`](project7/p4_03_pipeline.py)
- [`project7/p4_04_pipeline.py`](project7/p4_04_pipeline.py)
- [`project7/p4_05_pipeline.py`](project7/p4_05_pipeline.py)
- [`project7/p4_06_pipeline.py`](project7/p4_06_pipeline.py)

The reviewer-facing entry point is **not** this directory. Use the [Operator Interface notebook](../notebooks/Project_7_Operator_Interface.ipynb).

## Frozen Technical Boundary

The final P5-12 strict inventory checksum-governs the accepted technical/evaluation source set. Silent post-freeze changes to frozen source code require a new candidate version.

See the [Final Submission-Candidate Strict Inventory](../outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json).
