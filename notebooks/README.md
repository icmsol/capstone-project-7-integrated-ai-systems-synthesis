# Notebooks

This directory currently contains two committed Colab notebooks with different purposes.

## Primary Reviewer / Operator Entry Point

### `Project_7_Operator_Interface.ipynb`

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/icmsol/capstone-project-7-integrated-ai-systems-synthesis/blob/main/notebooks/Project_7_Operator_Interface.ipynb)

This is the intended reviewer-facing interface for the integrated Project 7 prototype.

It exposes seven stages:

1. Opportunity Intake
2. Organization Alignment
3. Clause Triage
4. Evidence Review
5. Recommendation & Packet
6. Human Disposition
7. Save / Resume

A reviewer should use this notebook rather than manually invoking internal modules.

Important operator responsibilities:

- confirm structured opportunity metadata against the uploaded solicitation;
- supply the solicitation passages to be triaged;
- review model-domain/evidence limitations;
- record an authorized human disposition when appropriate.

The interface supports export and restoration of resumable case bundles.

See [P5-09 Operator Interface](../docs/P5_09_Operator_Interface.md) and [P5-12 Final Submission-Candidate Freeze](../docs/P5_12_Final_Submission_Candidate_Freeze.md).

## Project 4 Validation Notebook

### `P4_03_Bounded_Clause_Triage_Validation.ipynb`

This notebook preserves validation evidence for the frozen Project 4 clause-theme inference package used by Project 7.

It is **not** the primary Project 7 user interface.

## Runtime Boundary

The operator notebook is designed for Google Colab/Python 3.12. Its accepted historical bootstrap remains [`../requirements_p5_09.txt`](../requirements_p5_09.txt), which layers `ipywidgets` on the frozen final-baseline requirements; the notebook also preserves its explicit CPU-PyTorch install. P9-02 intentionally does not rewrite that accepted notebook.

For the **final submission and hosted replay environment**, use the authoritative root [`../requirements.txt`](../requirements.txt). The final Quality Gate installs that exact lock in Python 3.12 and records `pip freeze` evidence, while the stage-specific requirements files remain historical acceptance snapshots.
