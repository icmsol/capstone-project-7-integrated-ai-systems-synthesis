# P5-12 CI Overlay Compatibility Fix

## Root cause

The P5-12 hardening itself passed. The hosted quality gate failed only because
`tests/test_acceptance_corrected_baseline.py` still asserted that the *active*
`versioned_overlay_manifest.json` must have `overlay_version == "1.0.1"`.

P5-12 intentionally advanced the active post-freeze governance overlay to
`1.0.2` so the corrected ICM service catalog could be checksum-governed, while
preserving the original P5-06 overlay separately as
`versioned_overlay_manifest_v1.0.1.json`.

## Correction

The compatibility test now verifies both facts explicitly:

- the P5-06 acceptance-corrected baseline remains `v1.0.1`;
- the historical P5-06 overlay remains `1.0.1`;
- the active post-freeze overlay is `1.0.2`;
- frozen scenario inputs remain unchanged;
- external actions remain zero;
- the CI workflow remains structurally verified rather than byte-frozen.

The active `v1.0.2` overlay checksum entry for the corrected test is updated
accordingly. The historical `v1.0.1` overlay is not modified.

## Integrity boundary

This fix does not alter:

- frozen scenarios;
- Project 4 model weights;
- P5-01 through P5-05 evaluation outputs;
- P5-06 acceptance-corrected baseline;
- historical P5-06 overlay v1.0.1;
- safeguards or external-action boundaries.
