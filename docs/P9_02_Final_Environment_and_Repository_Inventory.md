# P9-02 — Final Submission Environment and Repository Inventory

## Status

**Final submission environment lock and repository-inventory controls prepared for hosted validation.** P9-02 is accepted only when the updated read-only Project 7 Quality Gate installs the root lock and completes successfully.

## Purpose

P9-02 adds the reviewer-facing `requirements.txt` required for the final executable submission without relocating or rewriting the historical stage-specific dependency snapshots that support earlier acceptance evidence. It also adds a hosted, generated full-file inventory and a temporary/placeholder-file check for final submission QA.

This activity does **not** change `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`, frozen scenarios, the Project 4 model artifact, safeguards, evaluation results, recommendation logic, operator workflow behavior, or the human-authority boundary.

## Final Submission Environment

- Python: **3.12**
- Hosted platform: GitHub Actions `ubuntu-latest`
- Compute boundary: **CPU**
- Authoritative final dependency lock: [`../requirements.txt`](../requirements.txt)
- Dependency style: exact resolved `name==version` pins
- PyTorch: exact CPU build, installed using the official PyTorch CPU wheel index
- Hosted verification: `pip check`, `pip freeze`, exact lock comparison, required imports, and CPU-only torch check

The root lock covers the final integrated validation/runtime families: JSON Schema validation, reference resolution, YAML parsing, the frozen Project 4 CPU inference dependency, and the Jupyter widget stack used by the reviewer-facing operator interface.

## Historical Dependency Snapshots Are Preserved

The following 12 acceptance-era files remain at their original repository paths:

`requirements_p4_01.txt` through `requirements_p4_06.txt`, `requirements_p5_01.txt` through `requirements_p5_05.txt`, and `requirements_p5_09.txt`.

They are retained as historical stage snapshots. They are **not** moved into a new folder because their original paths are part of the project provenance and earlier replay documentation.

The frozen operator notebook also retains its historical bootstrap through `requirements_p5_09.txt` plus its explicit CPU-PyTorch install. P9-02 does not mutate that accepted notebook. The root `requirements.txt` is the final submission/hosted-replay lock.

## Repository Inventory

A human-readable area inventory is committed as [`P9_02_Final_Repository_Area_Inventory.csv`](P9_02_Final_Repository_Area_Inventory.csv).

On every hosted run, [`../scripts/verify_p9_02_submission_environment.py`](../scripts/verify_p9_02_submission_environment.py) generates the exhaustive file-level inventory and environment evidence:

- `outputs/ci/p9_02_pip_freeze.txt`
- `outputs/ci/p9_02_repository_inventory.csv`
- `outputs/ci/p9_02_repository_inventory_summary.json`

The generated repository inventory records repository-relative path, top-level area, byte count, and SHA-256 for each committed file outside generated CI output/cache locations.

## Temporary / Placeholder Asset Control

The P9-02 verifier fails closed if the final repository contains common temporary or placeholder artifacts such as `.gitkeep`, `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.bak`, editor backup files, notebook checkpoints, or Python/test cache directories.

This check supplements the existing repository-integrity scan for credentials, files over 100 MB, merge-conflict markers, notebook tracebacks, and unresolved implementation markers.

## CI Integration

The final Quality Gate:

1. provisions Python 3.12 on a clean `ubuntu-latest` runner;
2. installs the exact root `requirements.txt` using the PyTorch CPU wheel index as an additional index;
3. runs `pip check`;
4. executes the existing frozen-candidate validation/regression suite;
5. runs the P9-02 environment/inventory verifier; and
6. retains the final lock, generated freeze, repository inventory, paper, presentation, and prior acceptance evidence in the hosted artifact.

The workflow remains read-only and performs no deployment, publishing, procurement, contract, or other external write action.

## Acceptance Criterion

P9-02 passes when a fresh hosted Quality Gate confirms:

- all exact lock entries are installed at their pinned versions;
- the CPU-only PyTorch boundary is preserved;
- all 12 historical requirements snapshots remain in place;
- the exhaustive repository inventory is generated;
- no temporary/placeholder artifacts are detected; and
- all prior frozen-candidate verifiers and regression tests continue to pass.
