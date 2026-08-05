"""Validate the active Project 7 scenario taxonomy."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "config" / "schemas"
SCHEMA_PATH = SCHEMA_DIR / "scenario_taxonomy.schema.json"
TAXONOMY_PATH = (
    ROOT / "config" / "system"
    / "scenario_taxonomy_and_target_cases.json"
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def build_registry() -> Registry:
    registry = Registry()
    for path in SCHEMA_DIR.glob("*.json"):
        schema = load_json(path)
        if schema.get("$id"):
            registry = registry.with_resource(
                schema["$id"],
                Resource.from_contents(schema),
            )
    return registry


def main() -> None:
    schema = load_json(SCHEMA_PATH)
    taxonomy = load_json(TAXONOMY_PATH)
    validator = Draft202012Validator(
        schema,
        registry=build_registry(),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    validator.validate(taxonomy)

    cases = taxonomy["target_cases"]
    outcomes = {
        case["expected_terminal_outcome"]
        for case in cases
    }
    required_outcomes = {
        "finalized_accept",
        "finalized_accept_with_conditions",
        "finalized_reject",
        "deferred",
        "escalated",
        "failed_closed",
    }
    if required_outcomes - outcomes:
        raise AssertionError(
            "Terminal outcome coverage is incomplete."
        )

    recommendation_labels = {
        case["expected_recommendation_label"]
        for case in cases
    }
    if "No Recommendation" not in recommendation_labels:
        raise AssertionError(
            "No Recommendation coverage is missing."
        )

    for case in cases:
        if (
            case["expected_recommendation_label"]
            == "No Recommendation"
            and case["expected_terminal_outcome"]
            == "failed_closed"
        ):
            raise AssertionError(
                f"{case['case_id']} confuses No Recommendation "
                "with failed-closed termination."
            )

    counts = Counter(
        category_id
        for case in cases
        for category_id in case["category_ids"]
    )
    for category in taxonomy["categories"]:
        if counts[category["category_id"]] < category["minimum_cases"]:
            raise AssertionError(
                f"{category['category_id']} minimum is not met."
            )

    print(f"Scenario categories checked: {len(taxonomy['categories'])}")
    print(f"Target cases checked: {len(cases)}")
    print(f"Terminal outcomes covered: {len(outcomes)}")
    print("No Recommendation modeled separately: PASS")
    print("Category minimum coverage: PASS")


if __name__ == "__main__":
    main()
