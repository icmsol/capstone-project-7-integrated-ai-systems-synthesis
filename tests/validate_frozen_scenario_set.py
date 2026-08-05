"""Validate the Project 7 P3-03 frozen scenario set."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCENARIO_ROOT = (
    ROOT / "data" / "scenarios" / "frozen" / "1.0.0"
)
MANIFEST_SCHEMA_PATH = (
    ROOT / "config" / "schemas"
    / "frozen_case_manifest.schema.json"
)
OUTCOME_SCHEMA_PATH = (
    ROOT / "config" / "schemas"
    / "expected_case_outcome.schema.json"
)
TAXONOMY_PATH = (
    ROOT / "config" / "system"
    / "scenario_taxonomy_and_target_cases.json"
)
INVALID_PATH = (
    ROOT / "tests" / "frozen_scenario_examples"
    / "invalid_frozen_case_manifest.json"
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as source_file:
        return json.load(source_file)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for chunk in iter(
            lambda: source_file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    manifest_schema = load_json(MANIFEST_SCHEMA_PATH)
    outcome_schema = load_json(OUTCOME_SCHEMA_PATH)
    taxonomy = load_json(TAXONOMY_PATH)
    invalid = load_json(INVALID_PATH)

    Draft202012Validator.check_schema(manifest_schema)
    Draft202012Validator.check_schema(outcome_schema)

    manifest_validator = Draft202012Validator(manifest_schema)
    outcome_validator = Draft202012Validator(outcome_schema)

    taxonomy_by_id = {
        case["case_id"]: case
        for case in taxonomy["target_cases"]
    }

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
        manifest = load_json(case_dir / "manifest.json")
        manifest_validator.validate(manifest)

        expected = load_json(
            case_dir / "expected" / "expected_outcome.json"
        )
        outcome_validator.validate(expected)

        case_id = manifest["case_id"]
        taxonomy_case = taxonomy_by_id[case_id]

        if (
            manifest["expected_terminal_outcome"]
            != taxonomy_case["expected_terminal_outcome"]
        ):
            raise AssertionError(
                f"Terminal outcome mismatch for {case_id}."
            )

        if (
            expected["expected_reason_codes"]
            != taxonomy_case["expected_reason_codes"]
        ):
            raise AssertionError(
                f"Reason-code mismatch for {case_id}."
            )

        if manifest["result_status"] != "not_executed_target_only":
            raise AssertionError(
                f"Manifest improperly claims a result for {case_id}."
            )
        if expected["result_status"] != "not_executed_target_only":
            raise AssertionError(
                f"Expected outcome improperly claims a result "
                f"for {case_id}."
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

    if not list(manifest_validator.iter_errors(invalid)):
        raise AssertionError(
            "Invalid frozen manifest unexpectedly passed."
        )

    print(f"Frozen cases checked: {len(case_dirs)}")
    print(f"Case manifests validated: {len(case_dirs)}")
    print(f"Expected outcomes validated: {len(case_dirs)}")
    print("Required files checksum-verified: PASS")
    print("Taxonomy-to-case outcome alignment: PASS")
    print("All cases remain unexecuted targets: PASS")
    print("Invalid frozen manifest: correctly rejected")


if __name__ == "__main__":
    main()
