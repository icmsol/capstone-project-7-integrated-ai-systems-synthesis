"""Validate the corrected Project 7 frozen scenario set v1.0.1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "config" / "schemas"
SCENARIO_ROOT = (
    ROOT / "data" / "scenarios" / "frozen" / "v1.0.1"
)
TAXONOMY_PATH = (
    ROOT / "config" / "system"
    / "scenario_taxonomy_and_target_cases.json"
)
STAGE_MAP_PATH = (
    ROOT / "config" / "system"
    / "stage_identifier_mapping.json"
)
CHECKSUM_PATH = (
    ROOT / "docs"
    / "P3_04_v1_0_1_Package_Checksum_Inventory.json"
)
INVALID_MANIFEST_PATH = (
    ROOT / "tests" / "frozen_scenario_examples"
    / "invalid_frozen_case_manifest.json"
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(
            lambda: file_obj.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)
    return digest.hexdigest()


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


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(
        load_json(SCHEMA_DIR / name),
        registry=build_registry(),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )


def main() -> None:
    taxonomy = load_json(TAXONOMY_PATH)
    taxonomy_by_id = {
        case["case_id"]: case
        for case in taxonomy["target_cases"]
    }
    stage_map = load_json(STAGE_MAP_PATH)
    stage_by_numeric = {
        item["numeric_stage_id"]: item
        for item in stage_map["mappings"]
    }

    manifest_validator = validator(
        "frozen_case_manifest.schema.json"
    )
    outcome_validator = validator(
        "expected_case_outcome.schema.json"
    )
    opportunity_validator = validator(
        "opportunity_record.schema.json"
    )
    human_validator = validator(
        "human_disposition_fixture.schema.json"
    )
    evaluation_validator = validator(
        "scenario_evaluation_result.schema.json"
    )

    case_dirs = sorted(
        path
        for path in SCENARIO_ROOT.iterdir()
        if path.is_dir() and path.name.startswith("TC-")
    )
    if len(case_dirs) != 19:
        raise AssertionError(
            f"Expected 19 cases, "
            f"found {len(case_dirs)}."
        )

    for case_dir in case_dirs:
        case_id = case_dir.name
        manifest = load_json(case_dir / "manifest.json")
        expected = load_json(
            case_dir / "expected" / "expected_outcome.json"
        )
        opportunity = load_json(
            case_dir / "inputs" / "opportunity.json"
        )
        human_fixture = load_json(
            case_dir / "inputs" / "human_disposition.json"
        )

        manifest_validator.validate(manifest)
        outcome_validator.validate(expected)
        opportunity_validator.validate(opportunity)
        human_validator.validate(human_fixture)

        taxonomy_case = taxonomy_by_id[case_id]
        if (
            expected["expected_terminal_outcome"]
            != taxonomy_case["expected_terminal_outcome"]
        ):
            raise AssertionError(
                f"Terminal outcome mismatch for {case_id}."
            )
        if (
            expected["expected_recommendation_code"]
            != taxonomy_case["expected_recommendation_code"]
        ):
            raise AssertionError(
                f"Recommendation mismatch for {case_id}."
            )

        mapping = stage_by_numeric[
            expected["expected_primary_stage_id"]
        ]
        if (
            expected["expected_primary_stage"]
            != mapping["orchestration_stage_id"]
        ):
            raise AssertionError(
                f"Stage mapping mismatch for {case_id}."
            )
        reached = human_fixture["reached"]
        disposition = human_fixture["disposition"]
        terminal = expected["expected_terminal_outcome"]

        if terminal.startswith("finalized_"):
            if not reached:
                raise AssertionError(
                    f"Finalized case lacks disposition: {case_id}."
                )
            expected_disposition = {
                "finalized_accept": "accept",
                "finalized_accept_with_conditions": (
                    "accept_with_modified_conditions"
                ),
                "finalized_reject": "reject",
            }[terminal]
            if disposition["disposition"] != expected_disposition:
                raise AssertionError(
                    f"Disposition mismatch for {case_id}."
                )
        elif terminal == "deferred":
            if (
                not reached
                or disposition["disposition"]
                != "defer_pending_information"
            ):
                raise AssertionError(
                    f"Deferred case lacks defer disposition: {case_id}."
                )
        elif terminal == "escalated" and reached:
            if disposition["disposition"] != "escalate":
                raise AssertionError(
                    f"Escalated disposition mismatch: {case_id}."
                )
        elif terminal == "failed_closed" and reached:
            raise AssertionError(
                f"Failed-closed case has a disposition: {case_id}."
            )

        if (
            expected["expected_recommendation_code"] == "R-06"
            and terminal != "deferred"
        ):
            raise AssertionError(
                f"No Recommendation must terminate through human "
                f"deferral in this frozen set: {case_id}."
            )

        for entry in manifest["required_files"]:
            target = case_dir / entry["path"]
            if not target.exists():
                raise AssertionError(
                    f"Missing file for {case_id}: {entry['path']}"
                )
            if target.stat().st_size != entry["bytes"]:
                raise AssertionError(
                    f"File-size mismatch for {case_id}: "
                    f"{entry['path']}"
                )
            if sha256_file(target) != entry["sha256"]:
                raise AssertionError(
                    f"Checksum mismatch for {case_id}: "
                    f"{entry['path']}"
                )

    valid_result = load_json(
        ROOT / "tests" / "frozen_scenario_examples"
        / "valid_scenario_evaluation_result.json"
    )
    evaluation_validator.validate(valid_result)

    invalid_manifest = load_json(INVALID_MANIFEST_PATH)
    if not list(
        manifest_validator.iter_errors(invalid_manifest)
    ):
        raise AssertionError(
            "Invalid frozen manifest unexpectedly passed."
        )

    checksum_inventory = load_json(CHECKSUM_PATH)
    declared = {
        item["path"]
        for item in checksum_inventory["files"]
    }
    actual = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.relative_to(ROOT).as_posix()
        != (
            "docs/"
            "P3_04_v1_0_1_Package_Checksum_Inventory.json"
        )
    }
    if declared != actual:
        raise AssertionError(
            f"Package inventory mismatch. "
            f"Missing={sorted(actual - declared)}; "
            f"extra={sorted(declared - actual)}"
        )
    for item in checksum_inventory["files"]:
        path = ROOT / item["path"]
        if (
            path.stat().st_size != item["bytes"]
            or sha256_file(path) != item["sha256"]
        ):
            raise AssertionError(
                f"Package checksum mismatch: {item['path']}"
            )

    print(f"Frozen cases checked: {len(case_dirs)}")
    print(f"Case manifests validated: {len(case_dirs)}")
    print(f"Expected outcomes validated: {len(case_dirs)}")
    print(f"Opportunities schema-valid: {len(case_dirs)}")
    print(f"Human fixtures schema-valid: {len(case_dirs)}")
    print("Recommendation and terminal-state separation: PASS")
    print("Human-disposition coherence: PASS")
    print("Stage identifier mapping: PASS")
    print("Required files checksum-verified: PASS")
    print("Package checksum inventory complete: PASS")
    print("Evaluation-result contract: PASS")
    print("All cases remain unexecuted targets: PASS")


if __name__ == "__main__":
    main()
