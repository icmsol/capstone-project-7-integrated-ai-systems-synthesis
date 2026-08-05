"""Validate the Project 7 representative operational workload."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT / "config" / "schemas"
    / "operational_workload.schema.json"
)
WORKLOAD_PATH = (
    ROOT / "config" / "system"
    / "representative_operational_workload.json"
)
INVALID_PATH = (
    ROOT / "tests" / "workload_examples"
    / "invalid_operational_workload.json"
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as source_file:
        return json.load(source_file)


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    workload = load_json(WORKLOAD_PATH)
    invalid = load_json(INVALID_PATH)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    validator.validate(workload)

    stages = workload["stages"]
    if [stage["sequence"] for stage in stages] != list(
        range(1, 13)
    ):
        raise AssertionError(
            "Stages must be contiguous from 1 through 12."
        )

    actor_ids = {
        actor["actor_id"]
        for actor in workload["actors"]
    }
    stage_ids = {
        stage["stage_id"]
        for stage in stages
    }

    for stage in stages:
        if stage["primary_actor"] not in actor_ids:
            raise AssertionError(
                f"Unknown actor in {stage['stage_id']}."
            )

    for point in workload["human_decision_points"]:
        if point["stage_id"] not in stage_ids:
            raise AssertionError(
                f"Unknown decision stage in {point['decision_id']}."
            )

    if workload["workload_profile"]["training_required"]:
        raise AssertionError(
            "Integrated workload must not train a new model."
        )
    if workload["workload_profile"]["gpu_required"]:
        raise AssertionError(
            "Integrated workload must run without a GPU."
        )

    categories = Counter(
        target["category"]
        for target in workload["acceptance_targets"]
    )
    required_categories = {
        "functional",
        "data_quality",
        "evidence",
        "governance",
        "human_authority",
        "portability",
        "performance",
        "reproducibility",
    }
    missing = required_categories - set(categories)
    if missing:
        raise AssertionError(
            f"Missing target categories: {sorted(missing)}"
        )

    if not list(validator.iter_errors(invalid)):
        raise AssertionError(
            "Invalid operational workload unexpectedly passed."
        )

    print(
        f"Actors checked: {len(workload['actors'])}"
    )
    print(
        f"Approved inputs checked: "
        f"{len(workload['approved_inputs'])}"
    )
    print(
        f"Workflow stages checked: {len(stages)}"
    )
    print(
        f"Human decision points checked: "
        f"{len(workload['human_decision_points'])}"
    )
    print(
        f"Acceptance targets checked: "
        f"{len(workload['acceptance_targets'])}"
    )
    print("CPU and no-training boundary: PASS")
    print("Stage, actor, and decision integrity: PASS")
    print("Invalid operational workload: correctly rejected")


if __name__ == "__main__":
    main()
