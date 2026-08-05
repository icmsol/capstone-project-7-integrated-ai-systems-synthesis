"""Validate the Project 7 scenario taxonomy."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "config" / "schemas" / "scenario_taxonomy.schema.json"
TAXONOMY = ROOT / "config" / "system" / "scenario_taxonomy_and_target_cases.json"
INVALID = ROOT / "tests" / "scenario_taxonomy_examples" / "invalid_scenario_taxonomy.json"


def load(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    schema = load(SCHEMA)
    taxonomy = load(TAXONOMY)
    invalid = load(INVALID)

    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    validator.validate(taxonomy)

    categories = taxonomy["categories"]
    cases = taxonomy["target_cases"]
    category_ids = {c["category_id"] for c in categories}
    counts = Counter(
        category_id
        for case in cases
        for category_id in case["category_ids"]
    )

    for case in cases:
        unknown = set(case["category_ids"]) - category_ids
        if unknown:
            raise AssertionError(
                f"{case['case_id']} has unknown categories: {sorted(unknown)}"
            )

    for category in categories:
        actual = counts.get(category["category_id"], 0)
        if actual < category["minimum_cases"]:
            raise AssertionError(
                f"{category['category_id']} has only {actual} cases."
            )

    required_outcomes = {
        "finalized_accept",
        "finalized_accept_with_conditions",
        "finalized_reject",
        "deferred",
        "escalated",
        "failed_closed",
        "no_recommendation",
    }
    outcomes = {
        case["expected_terminal_outcome"]
        for case in cases
    }
    if required_outcomes - outcomes:
        raise AssertionError("Terminal outcome coverage is incomplete.")

    targets = {
        target_id
        for case in cases
        for target_id in case["acceptance_target_ids"]
    }
    controls = {
        control_id
        for case in cases
        for control_id in case["safeguard_control_ids"]
    }

    if {f"AT-{i:02d}" for i in range(1, 19)} - targets:
        raise AssertionError("Acceptance target coverage is incomplete.")
    if len(controls) < 20:
        raise AssertionError("Safeguard coverage is insufficient.")
    if not list(validator.iter_errors(invalid)):
        raise AssertionError("Invalid taxonomy unexpectedly passed.")

    print(f"Scenario categories checked: {len(categories)}")
    print(f"Target cases checked: {len(cases)}")
    print(f"Terminal outcomes covered: {len(outcomes)}")
    print(f"Acceptance targets covered: {len(targets)}")
    print(f"Safeguard controls covered: {len(controls)}")
    print("Category minimum coverage: PASS")
    print("Profile and outcome balance: PASS")
    print("Invalid scenario taxonomy: correctly rejected")


if __name__ == "__main__":
    main()
