"""Validate Project 7 shared schemas and examples."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "config" / "schemas"
EXAMPLE_DIR = ROOT / "tests" / "schema_examples"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as source_file:
        return json.load(source_file)


def build_registry() -> tuple[Registry, dict[str, dict]]:
    registry = Registry()
    schemas: dict[str, dict] = {}

    for path in sorted(SCHEMA_DIR.glob("*.schema.json")):
        schema = load_json(path)
        Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(
            schema["$id"],
            Resource.from_contents(schema),
        )
        schemas[path.name] = schema

    return registry, schemas


def main() -> None:
    registry, schemas = build_registry()

    case_validator = Draft202012Validator(
        schemas["integrated_case_state.schema.json"],
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    audit_validator = Draft202012Validator(
        schemas["audit_event.schema.json"],
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )

    valid_case = load_json(
        EXAMPLE_DIR / "valid_integrated_case.json"
    )
    valid_audit = load_json(
        EXAMPLE_DIR / "valid_audit_event.json"
    )
    invalid_case = load_json(
        EXAMPLE_DIR / "invalid_integrated_case.json"
    )

    case_validator.validate(valid_case)
    audit_validator.validate(valid_audit)

    invalid_errors = list(
        case_validator.iter_errors(invalid_case)
    )
    if not invalid_errors:
        raise AssertionError(
            "The invalid integrated case unexpectedly passed."
        )

    print(f"Schemas checked: {len(schemas)}")
    print("Valid integrated case: PASS")
    print("Valid audit event: PASS")
    print(
        "Invalid integrated case: correctly rejected "
        f"with {len(invalid_errors)} validation error(s)"
    )


if __name__ == "__main__":
    main()
