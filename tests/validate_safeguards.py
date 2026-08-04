"""Validate Project 7 safeguard policy, reason codes, and risk controls."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "config" / "schemas"
SYSTEM_DIR = ROOT / "config" / "system"
EXAMPLE_DIR = ROOT / "tests" / "safeguard_examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as source_file:
        return json.load(source_file)


def main() -> None:
    policy_schema = load_json(
        SCHEMA_DIR / "safeguard_policy.schema.json"
    )
    reason_schema = load_json(
        SCHEMA_DIR / "safeguard_reason_code_registry.schema.json"
    )

    Draft202012Validator.check_schema(policy_schema)
    Draft202012Validator.check_schema(reason_schema)

    policy_validator = Draft202012Validator(policy_schema)
    reason_validator = Draft202012Validator(reason_schema)

    policy = load_json(
        SYSTEM_DIR / "safeguard_policy.json"
    )
    reason_registry = load_json(
        SYSTEM_DIR / "safeguard_reason_codes.json"
    )
    scenarios = load_json(
        EXAMPLE_DIR / "safeguard_trigger_scenarios.json"
    )

    policy_validator.validate(policy)
    reason_validator.validate(reason_registry)

    control_ids = [
        control["control_id"]
        for control in policy["controls"]
    ]
    if len(control_ids) != len(set(control_ids)):
        raise AssertionError("Duplicate control IDs detected.")

    reason_codes = {
        item["code"]
        for item in reason_registry["codes"]
    }
    used_codes = {
        code
        for control in policy["controls"]
        for code in control["reason_codes"]
    }
    missing_codes = used_codes - reason_codes
    if missing_codes:
        raise AssertionError(
            f"Unknown reason codes: {sorted(missing_codes)}"
        )

    scenario_control_ids = {
        item["control_id"]
        for item in scenarios
    }
    if scenario_control_ids != set(control_ids):
        raise AssertionError(
            "Every safeguard control must have one trigger scenario."
        )

    invalid_policy = load_json(
        EXAMPLE_DIR / "invalid_safeguard_policy.json"
    )
    if not list(policy_validator.iter_errors(invalid_policy)):
        raise AssertionError(
            "Invalid safeguard policy unexpectedly passed."
        )

    print(f"Safeguard controls checked: {len(control_ids)}")
    print(f"Reason codes checked: {len(reason_codes)}")
    print(f"Trigger scenarios checked: {len(scenarios)}")
    print("Policy schema validation: PASS")
    print("Control and reason-code integrity: PASS")
    print("Control-to-scenario coverage: PASS")
    print("Invalid safeguard policy: correctly rejected")


if __name__ == "__main__":
    main()
