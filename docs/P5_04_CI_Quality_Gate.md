# Project 7 Continuous-Integration Quality Gate

> **P6-02 historical-record notice (2026-08-08):** This describes the quality gate at its P5-04 introduction. The live workflow was later extended through acceptance, freeze, and documentation overlays.

## Purpose

The quality gate provides automated reproducibility and control validation for the final refined baseline. It is a CI workflow only; it does not deploy or publish the prototype.

## Trigger and Permissions

- Pushes to `main`
- Pull requests targeting `main`
- Manual `workflow_dispatch`
- Read-only `contents` permission
- Concurrency cancellation for superseded runs
- 20-minute timeout

## Automated Checks

- Python compilation
- Credential-pattern, file-size, merge-conflict, and notebook-traceback checks
- Shared-schema validation
- Component-contract and orchestration-policy validation
- Safeguard policy and scenario coverage
- Operational-workload and scenario-taxonomy validation
- P5-01 raw-output integrity
- P5-02 metric recalculation
- P5-03 failure-analysis verification
- P5-04 refined-suite and portability verification
- Unit tests for refinement, portability, and workflow structure
- Upload of the quality-gate log and P5-04 evidence as a 30-day workflow artifact

## Official Implementation References

- GitHub Python CI guidance: https://docs.github.com/actions/automating-builds-and-tests/building-and-testing-python
- Checkout action: https://github.com/actions/checkout
- Python setup action: https://github.com/actions/setup-python
- Workflow artifact upload: https://github.com/actions/upload-artifact
- Workflow artifact concepts: https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts

The workflow uses `actions/checkout@v5`, `actions/setup-python@v6`, and `actions/upload-artifact@v4`. It pins Python to 3.12 instead of using a floating `3.x` version.

## Hosted Confirmation Requirement

P5-04 should not be marked complete until the first hosted **Project 7 Quality Gate** run is green. The run will be triggered automatically by the commit containing `.github/workflows/project7-quality-gate.yml`.
