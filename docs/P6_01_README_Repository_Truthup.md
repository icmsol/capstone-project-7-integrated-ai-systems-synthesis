# P6-01 README and Repository Documentation Truth-Up

## Scope

This activity updates **all 18 existing `README.md` files** in the current Project 7 repository and synchronizes the documentation copy of the GitHub Actions quality gate.

The purpose is to eliminate scaffold-era language, stale folder descriptions, stale workflow references, and reviewer links that no longer match the accepted P5-12 repository state.

## README Coverage

- `README.md`
- `audit/README.md`
- `config/README.md`
- `data/README.md`
- `data/frozen_scenarios/README.md`
- `data/processed/README.md`
- `data/raw/README.md`
- `data/scenarios/frozen/v1.0.0/_shared/README.md`
- `docs/README.md`
- `figures/README.md`
- `notebooks/README.md`
- `outputs/README.md`
- `outputs/case_packets/README.md`
- `outputs/evaluation/README.md`
- `presentation/README.md`
- `reports/README.md`
- `src/README.md`
- `tests/README.md`

## Validation Results

- README files discovered: **18**
- README files updated: **18**
- README coverage: **PASS**
- Relative Markdown links checked: **194**
- Broken relative links: **0**
- Known stale scaffold phrases remaining: **0**
- `docs/ci/project7-quality-gate.yml` matches `.github/workflows/project7-quality-gate.yml`: **PASS**

External links are intentionally not treated as local-file checks. The root README uses the public repository, GitHub Actions, and Colab operator-interface links.

## Truth Sources

The documentation is reconciled to:

- `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`
- `outputs/evaluation/p5_12/final_submission_candidate_manifest.json`
- `outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json`
- `outputs/evaluation/p5_12/final_visual_regression_acceptance.json`
- the current repository directory tree
- the current live `.github/workflows/project7-quality-gate.yml`
- the accepted operator-interface workflow and limitations

## Documentation Boundary

This truth-up changes reviewer documentation only. It does not alter the frozen P5-12 technical/evaluation artifacts.

Any later Phase 6 documentation changes should continue to preserve this distinction: documentation may evolve, but technical/evaluation claims must remain traceable to the frozen candidate or be explicitly versioned.
