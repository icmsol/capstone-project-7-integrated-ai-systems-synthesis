# P6-01 Post-Freeze Documentation and CI Compatibility Correction

## Root cause

P6-01 intentionally updated all repository README files so reviewer-facing
documentation matched the real integrated system. The historical P5-05 artifact
inventory had captured those scaffold-era README files with strict byte-level
hashes. GitHub Actions therefore correctly reported a historical size mismatch
after the documentation was improved.

That historical behavior is too broad for the documented freeze policy, which
explicitly permits versioned documentation corrections and versioned CI
maintenance after the evaluation freeze.

## Correction approach

The obsolete READMEs are **not** restored and the historical P5-05 inventory is
**not** rewritten.

Instead, this correction adds a tightly constrained P6-01 post-freeze overlay that
checksum-governs:

- all 18 existing README files trued up during P6-01;
- `docs/ci/project7-quality-gate.yml`, the documentation copy of the live workflow;
- the P5-05 and P5-06 verifier maintenance needed to recognize this versioned overlay;
- the final-candidate verifier/test maintenance needed to continue enforcing the
  P5-12 technical/evaluation freeze.

The overlay permits only `README.md` files and the documentation workflow copy as
documentation corrections. CI maintenance is restricted to four named
verification/test files. Arbitrary technical files cannot be hidden inside this
overlay.

## Freeze integrity

`PROJECT7-SUBMISSION-CANDIDATE-v1.0.0` remains the frozen technical/evaluation
candidate. This correction does not change:

- frozen scenarios or expected outcomes;
- model artifacts or thresholds;
- safeguards;
- evaluation results;
- recommendation logic;
- operator acceptance evidence;
- human-authority requirements; or
- the zero-external-action boundary.

The original historical P5-05 and P5-06 hashes remain preserved in their original
manifests. The new P6-01 overlay records the permitted post-freeze documentation
and CI-maintenance hashes.

## Workflow

The existing `.github/workflows/project7-quality-gate.yml` does not need to be
edited. It already invokes the verifier/test files updated by this package.
