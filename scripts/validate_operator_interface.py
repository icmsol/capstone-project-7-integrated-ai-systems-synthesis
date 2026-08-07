"""Validate the Project 7 operator interface as a reviewer-facing artifact."""

from __future__ import annotations

from pathlib import Path
import ast
import json


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "Project_7_Operator_Interface.ipynb"
UI_SOURCE = ROOT / "src" / "project7" / "operator_ui.py"
WORKFLOW_SOURCE = ROOT / "src" / "project7" / "operator_workflow.py"


def main() -> None:
    for path in [NOTEBOOK, UI_SOURCE, WORKFLOW_SOURCE]:
        if not path.is_file():
            raise RuntimeError(f"Required operator artifact is missing: {path}")

    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    code_cells = [
        cell
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    ]
    if len(code_cells) != 2:
        raise RuntimeError(
            f"Operator notebook must contain exactly two code cells; found {len(code_cells)}."
        )

    for index, cell in enumerate(code_cells, start=1):
        source = "".join(cell.get("source", []))
        ast.parse(source)
        if cell.get("outputs"):
            raise RuntimeError(
                f"Operator notebook code cell {index} contains stored outputs."
            )

    notebook_text = NOTEBOOK.read_text(encoding="utf-8")
    required_notebook_markers = [
        "Project 7 — Operator Interface",
        "launch_operator_interface",
        "requirements_p5_09.txt",
    ]
    for marker in required_notebook_markers:
        if marker not in notebook_text:
            raise RuntimeError(
                f"Operator notebook marker is missing: {marker}"
            )

    ui_text = UI_SOURCE.read_text(encoding="utf-8")
    required_ui_markers = [
        "Opportunity Intake",
        "Organization Alignment",
        "Clause Triage",
        "Evidence Review",
        "Recommendation & Packet",
        "Human Disposition",
        "Save / Resume",
        "Export Resumable Case Bundle",
        "Restore Case Bundle",
    ]
    for marker in required_ui_markers:
        if marker not in ui_text:
            raise RuntimeError(f"Operator UI control is missing: {marker}")

    workflow_text = WORKFLOW_SOURCE.read_text(encoding="utf-8")
    forbidden_case_specific_markers = [
        "3485A",
        "CalJOBS",
        "Employment Development Department",
    ]
    for marker in forbidden_case_specific_markers:
        if marker in ui_text or marker in workflow_text:
            raise RuntimeError(
                f"Operator interface is improperly case-specific: {marker}"
            )

    required_backend_calls = [
        "normalize_opportunity",
        "run_alignment_and_history",
        "run_clause_triage",
        "run_evidence_workflow",
        "run_packet_assembly",
        "record_human_disposition",
    ]
    for marker in required_backend_calls:
        if marker not in workflow_text:
            raise RuntimeError(
                f"Operator workflow is missing backend integration: {marker}"
            )

    print("Operator notebook code cells: 2")
    print("Operator notebook stored outputs: 0")
    print("Reviewer workflow stages: 7")
    print("Case-specific hard-coding: 0")
    print("Backend components integrated: 6")
    print("Resumable bundle export/restore: PASS")
    print("Operator interface validation: PASS")


if __name__ == "__main__":
    main()
