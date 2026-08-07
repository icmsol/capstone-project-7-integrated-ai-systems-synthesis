# P5-09 — Single-Entry-Point Operator Interface

## Purpose

P5-09 converts the validated Project 7 backend into an operator-facing integrated
prototype without introducing a separate production web stack. The interface is a
thin Colab/Jupyter presentation and orchestration layer over the existing Project 7
components.

## Reviewer workflow

The reviewer opens `notebooks/Project_7_Operator_Interface.ipynb`, selects **Run all**,
and then uses the displayed interface:

1. **Opportunity Intake** — upload a source file and confirm structured metadata.
2. **Organization Alignment** — select a configured organization profile and run the
   existing service-alignment and historical-context components.
3. **Clause Triage** — paste relevant source passages and run the bounded Project 4 model.
4. **Evidence Review** — automatically generate evidence requests from actual model
   predictions and source passages.
5. **Recommendation & Packet** — generate the nonbinding decision-support recommendation
   and reviewer-facing packet.
6. **Human Disposition** — record an authorized human response separately from the
   immutable system recommendation.
7. **Save / Resume** — export a checksum-inventoried case ZIP or restore a prior case
   after runtime loss.

No user-written Python glue code, manual audit-file copying, or internal path manipulation
is part of the intended reviewer workflow.

## Architectural boundary

`src/project7/operator_workflow.py` does not contain bid/no-bid, legal, pricing, staffing,
eligibility, or final-decision logic. It only:

- stages source files outside the repository;
- calls the already-tested Project 7 components in sequence;
- passes explicit predecessor audit paths;
- persists structured inputs, outputs, and audit evidence;
- derives evidence requests from model predictions plus operator-supplied passages;
- invokes the separately validated human-disposition recorder;
- creates and verifies resumable case bundles.

The UI is implemented in `src/project7/operator_ui.py`. The notebook itself contains only
setup and launch cells.

## Known and intentionally visible limitations

The interface does **not** claim automatic end-to-end PDF understanding.

- Opportunity metadata remains operator-confirmed because P4-01 validates provenance and
  schema but does not semantically cross-check every structured field against the PDF.
- Clause passages are operator-selected/pasted before Project 4 triage.
- The registered FAR corpus remains a representative bounded subset and may correctly
  return insufficient evidence.
- Project 4 was trained on commercial-contract language, so public-sector consequential
  use remains subject to the configured domain-shift human-review safeguard.
- The system recommendation is nonbinding and cannot become the organizational decision
  without the separate human-disposition step.
- The prototype performs no autonomous external action.

## Persistence

`Export Resumable Case Bundle` creates a ZIP containing the case workspace plus
`case_bundle_manifest.json`. The manifest records SHA-256 and size for each included file.
Restore validates every listed file before the case is accepted.

This addresses the manual-acceptance finding that an ephemeral Colab runtime should not
force an operator to reconstruct internal case state manually.

## P5-09 acceptance gates

- Static notebook validation passes.
- Operator workflow unit tests pass.
- Existing P5-01 through P5-08 controls continue to pass.
- Hosted GitHub Actions quality gate passes after P5-09 tests are added.
- P5-10 reruns RFO 3485A through this interface with no new code.
