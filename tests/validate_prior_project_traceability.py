"""Validate the Project 7 prior-project traceability matrix."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT / "config" / "schemas"
    / "prior_project_traceability.schema.json"
)
MATRIX_PATH = (
    ROOT / "docs"
    / "Prior_Project_Traceability_Matrix.json"
)
INVALID_PATH = (
    ROOT / "tests" / "traceability_examples"
    / "invalid_prior_project_traceability.json"
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as source_file:
        return json.load(source_file)


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    matrix = load_json(MATRIX_PATH)
    invalid = load_json(INVALID_PATH)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    validator.validate(matrix)

    entries = matrix["entries"]
    project_set = {
        entry["prior_project"]
        for entry in entries
    }
    if project_set != {1, 2, 3, 4, 5, 6}:
        raise AssertionError(
            "Every prior project must be represented."
        )

    runtime_classes = {
        "executable_reuse",
        "adapted_runtime_reuse",
    }
    runtime_projects = {
        entry["prior_project"]
        for entry in entries
        if entry["reuse_classification"] in runtime_classes
    }
    if not {1, 2, 4, 6}.issubset(runtime_projects):
        raise AssertionError(
            "Projects 1, 2, 4, and 6 require runtime entries."
        )

    for project in (3, 5):
        if any(
            entry["prior_project"] == project
            and entry["reuse_classification"] in runtime_classes
            for entry in entries
        ):
            raise AssertionError(
                f"Project {project} must remain bounded evidence."
            )

    for entry in entries:
        if (
            entry["reuse_classification"] in runtime_classes
            and entry["project7_target"].lower().startswith("no ")
        ):
            raise AssertionError(
                f"Runtime entry missing target: {entry['trace_id']}"
            )
        if (
            entry["decision"] == "exclude"
            and entry["runtime_status"] != "not_used"
        ):
            raise AssertionError(
                f"Excluded entry has invalid status: {entry['trace_id']}"
            )

    if not list(validator.iter_errors(invalid)):
        raise AssertionError(
            "Invalid traceability matrix unexpectedly passed."
        )

    print(f"Traceability entries checked: {len(entries)}")
    print(f"Prior projects covered: {len(project_set)}")
    print("Runtime contributor rule: PASS")
    print("Bounded evidence rule for Projects 3 and 5: PASS")
    print("Runtime target and exclusion integrity: PASS")
    print("Invalid traceability matrix: correctly rejected")


if __name__ == "__main__":
    main()
