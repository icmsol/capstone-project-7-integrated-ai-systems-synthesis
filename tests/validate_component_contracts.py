"""Validate Project 7 component contracts and orchestration policy."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "config" / "contracts"
SYSTEM_DIR = ROOT / "config" / "system"
SCHEMA_DIR = ROOT / "config" / "schemas"
EXAMPLE_DIR = ROOT / "tests" / "contract_examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as source_file:
        return json.load(source_file)


def main() -> None:
    contract_schema = load_json(
        SCHEMA_DIR / "component_contract.schema.json"
    )
    orchestration_schema = load_json(
        SCHEMA_DIR / "orchestration_policy.schema.json"
    )

    Draft202012Validator.check_schema(contract_schema)
    Draft202012Validator.check_schema(orchestration_schema)

    contract_validator = Draft202012Validator(contract_schema)
    orchestration_validator = Draft202012Validator(
        orchestration_schema
    )

    contracts = []
    for path in sorted(CONTRACT_DIR.glob("*.contract.json")):
        contract = load_json(path)
        contract_validator.validate(contract)
        contracts.append(contract)

    registry = load_json(
        CONTRACT_DIR / "component_contract_registry.json"
    )
    policy = load_json(
        SYSTEM_DIR / "orchestration_policy.json"
    )
    orchestration_validator.validate(policy)

    registered_ids = {
        item["component_id"]
        for item in registry["contracts"]
    }
    contract_ids = {
        item["component_id"]
        for item in contracts
    }
    if registered_ids != contract_ids:
        raise AssertionError(
            "Contract registry and contract files differ."
        )

    stage_ids = {
        stage["component_id"]
        for stage in policy["stages"]
    }
    missing = stage_ids - registered_ids
    if missing:
        raise AssertionError(
            f"Policy references missing contracts: {sorted(missing)}"
        )

    invalid_contract = load_json(
        EXAMPLE_DIR / "invalid_component_contract.json"
    )
    if not list(contract_validator.iter_errors(invalid_contract)):
        raise AssertionError(
            "Invalid component contract unexpectedly passed."
        )

    invalid_policy = load_json(
        EXAMPLE_DIR / "invalid_orchestration_policy.json"
    )
    if not list(
        orchestration_validator.iter_errors(invalid_policy)
    ):
        raise AssertionError(
            "Invalid orchestration policy unexpectedly passed."
        )

    print(f"Component contracts checked: {len(contracts)}")
    print("Contract registry integrity: PASS")
    print("Orchestration policy: PASS")
    print("Stage-to-contract referential integrity: PASS")
    print("Invalid component contract: correctly rejected")
    print("Invalid orchestration policy: correctly rejected")


if __name__ == "__main__":
    main()
