# P5-07 — CI Manifest Verification Correction

## Observed failure

The first hosted P5-07 quality-gate run reached the new P5-06 verifier after all prior P5-01 through P5-05 checks passed. It then failed because the P5-06 versioned overlay compared `.github/workflows/project7-quality-gate.yml` to the byte hash recorded before P5-07 intentionally updated that workflow.

## Root cause

The workflow was incorrectly treated as an immutable correction artifact. It is orchestration that must evolve as validation coverage is extended. Byte-freezing it creates a circular condition: changing CI to add a new verifier causes that verifier to reject CI for having changed.

## Correction

The versioned overlay now uses two verification modes:

- `strict_sha256` for the 19 source, test, configuration, documentation, and evidence artifacts that define the P5-06 correction;
- `structural_current_ci` for the GitHub Actions workflow.

The structural CI check requires read-only repository permissions, Python 3.12, P5-01 through P5-06 verification, P5-06 correction regression tests, `actions/upload-artifact@v7`, and no publishing/deployment permissions or commands.

## Evaluation impact

None. The P5-06 backend correction already passed hosted run #5. The first P5-07 failure was verification metadata design only; it occurred after the frozen evaluation, metric, refinement, portability, and P5-05 freeze checks had all passed.
