"""JSON Schema loading and validation utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


class SchemaValidationError(ValueError):
    """Raised when an artifact violates a committed Project 7 schema."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def build_registry(schema_dir: Path) -> Registry:
    registry = Registry()
    for schema_path in sorted(schema_dir.glob("*.json")):
        schema = load_json(schema_path)
        schema_id = schema.get("$id")
        if schema_id:
            registry = registry.with_resource(
                schema_id,
                Resource.from_contents(schema),
            )
    return registry


def validate_artifact(
    artifact: Any,
    schema_name: str,
    schema_dir: Path,
) -> None:
    schema_path = schema_dir / schema_name
    if not schema_path.exists():
        raise FileNotFoundError(
            f"Required schema is missing: {schema_path}"
        )

    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(
        schema,
        registry=build_registry(schema_dir),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    errors = sorted(
        validator.iter_errors(artifact),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{list(error.absolute_path)}: {error.message}"
            for error in errors
        )
        raise SchemaValidationError(
            f"{schema_name} validation failed: {details}"
        )
