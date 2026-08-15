# P6-04 — Reproducibility Manifest and Replay Guide

## Status

**Reproducibility package assembled against the final frozen technical/evaluation candidate and the completed P6-01 through P6-03 documentation/governance overlays.**

Current confirmed repository state:

- Repository: `https://github.com/icmsol/capstone-project-7-integrated-ai-systems-synthesis`
- Branch: `main`
- Latest confirmed commit: `de89e0f`
- Hosted Project 7 Quality Gate: **#22 — PASS**
- Hosted duration: `35 seconds`
- Retained artifacts: `1`
- Frozen candidate: `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`

## What Is Frozen

The technical/evaluation candidate remains `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`.

Its strict inventory contains **44** frozen candidate files. Phase 6 documentation changes remain separately controlled by versioned overlays and do not silently mutate the frozen model, scenarios, safeguards, evaluation results, recommendation logic, operator workflow behavior, or human-authority boundary.

## Reproducibility Evidence Set

- [`P6_04_Source_Snapshot_and_Checksum_Inventory.csv`](P6_04_Source_Snapshot_and_Checksum_Inventory.csv)
- [`P6_04_Replay_Matrix.csv`](P6_04_Replay_Matrix.csv)
- [`../outputs/evaluation/p6_04/reproducibility_manifest.json`](../outputs/evaluation/p6_04/reproducibility_manifest.json)
- [`../outputs/evaluation/p6_04/environment_and_version_spec.json`](../outputs/evaluation/p6_04/environment_and_version_spec.json)
- [`../outputs/evaluation/p5_12/final_submission_candidate_manifest.json`](../outputs/evaluation/p5_12/final_submission_candidate_manifest.json)
- [`../outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json`](../outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json)

## Environment

### Python

- Hosted CI: **Python 3.12**
- Manual Colab acceptance: **Python 3.12.13**

### Dependency constraints

The established candidate uses the existing bounded dependency specifications:

```text
requirements_p4_03.txt
requirements_p5_05.txt
requirements_p5_09.txt
```

P6-04 does **not** rewrite the frozen candidate to manufacture a new dependency lock after acceptance.

Exact resolved third-party patch versions should be captured during replay. If future compatible-range resolution no longer passes the frozen tests, that is a reproducibility failure requiring explicit change control—not a reason to silently patch the frozen candidate.

### Model

- Artifact: `PROJECT4-CLAUSE-CLASSIFIER-INFERENCE`
- Version: `1.0.0`
- Configuration: `Baseline dropout 0.10`
- Checkpoint SHA-256: `50a280950d31466d7002578295c64e957d144611f5b9731bb059be50e68c6c92`
- Runtime device: `cpu`
- Classes: `10`
- Vocabulary: `4417`
- Maximum sequence length: `256`

### APIs and Formats

Project 7's final runtime has **no OpenAI/model-provider API dependency**. Prior Project 6 agentic work is design/evaluation evidence, not a live Project 7 runtime dependency.

The repository uses JSON Schema Draft 2020-12 and the hosted workflow uses `actions/checkout@v5`, `actions/setup-python@v6`, and `actions/upload-artifact@v7`.

## Deterministic Seed

The frozen integrated evaluation uses seed:

```text
42
```

This seed is recorded in both the frozen scenario-set index and the frozen evaluation policy.

## Source Snapshots

The source inventory records exact repository checksums for the frozen scenario index, ICM configuration, fictional portability profile, historical-context summary, model registry, FAR registry/corpus and clause snapshots, candidate manifest, and strict inventory.

The actual Project 4 model checkpoint is referenced by its approved checksum:

```text
50a280950d31466d7002578295c64e957d144611f5b9731bb059be50e68c6c92
```

The complete public repository remains the authoritative location for the large model package.

## Replay Levels

### Level 1 — Integrity verification

Run the repository checks and final-candidate verifiers. This verifies the preserved artifacts without requiring interactive source entry.

### Level 2 — Frozen evaluation replay

Run the P5-01/P5-04 verifiers and regression tests. Expected result: **19/19 cases, 262/262 assertions, 0 regressions**.

### Level 3 — Representative deterministic packet replay

Run:

```bash
python tests/run_p4_06_validation.py
```

This reconstructs the preserved packet/case outputs and verifies the audit chain.

### Level 4 — Operator acceptance replay

Open:

```text
notebooks/Project_7_Operator_Interface.ipynb
```

in Google Colab, select **Run all**, and complete the seven operator stages using an approved source.

This is a controlled interactive replay, not a byte-for-byte deterministic run: source metadata, passage selection, timestamps, and human rationale are intentionally operator/human inputs.

### Level 5 — Hosted CI replay

Push to `main` or manually dispatch **Project 7 Quality Gate**. A successful replay produces a green hosted run and retains the configured evidence artifact.

## Expected Non-Determinism

The following are explicitly not expected to be byte-identical:

- timestamps;
- GitHub Actions run IDs and durations;
- operator-entered rationale;
- human disposition timing;
- exact third-party patch versions resolving within the established compatible ranges.

The following **must** remain invariant unless a new candidate version is created:

- frozen scenario inputs and expected outcomes;
- fixed safeguards;
- model identity/checkpoint checksum;
- final candidate strict inventory;
- recommendation/human-authority boundary;
- prohibition against autonomous external action.

## Known Limitations

Reproducibility does not establish production readiness. The P6-03 governance package explicitly leaves production blockers unresolved, including public-sector model validity, complete-document coverage, complete authoritative evidence, formal records retention/legal hold, and production security/IAM/operations.

## Completion Criterion

P6-04 is complete when this manifest and replay evidence are committed and the updated hosted quality gate verifies the reproducibility package without changing `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`.

## P9-02 Final Submission Environment Addendum

This addendum records a later **final-submission QA control** and does not rewrite the historical P6-04 acceptance evidence above. The P6-04 dependency constraints and replay statements remain point-in-time evidence for the accepted technical/evaluation candidate.

P9-02 adds an authoritative root [`../requirements.txt`](../requirements.txt) exact lock for the final Python 3.12 CPU submission/hosted-replay environment. All 12 historical `requirements_p4_*` / `requirements_p5_*` snapshots remain at their original paths. The accepted operator notebook retains its historical `requirements_p5_09.txt` bootstrap and explicit CPU-PyTorch install; it is not modified by P9-02.

The final hosted Quality Gate installs the root lock, runs `pip check`, emits `outputs/ci/p9_02_pip_freeze.txt`, and generates an exhaustive repository file inventory plus summary. The P9-02 environment/inventory change is separately versioned by `PROJECT7-P9-02-POST-FREEZE-SUBMISSION-ENVIRONMENT-OVERLAY-v1.0.0`.

No frozen scenario, model artifact, safeguard, evaluation result, recommendation behavior, operator responsibility, human-authority boundary, or external-action prohibition is changed by this addendum.
