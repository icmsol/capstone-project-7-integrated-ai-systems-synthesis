#!/usr/bin/env python3
"""Verify the frozen Project 7 final evaluation baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = (
    ROOT / "outputs" / "evaluation" / "p5_05"
    / "final_evaluation_baseline.json"
)
SCHEMA_PATH = (
    ROOT / "config" / "schemas"
    / "final_evaluation_baseline.schema.json"
)
INVENTORY_PATH = (
    ROOT / "outputs" / "evaluation" / "p5_05"
    / "final_artifact_inventory.json"
)
VALIDATION_PATH = (
    ROOT / "outputs" / "evaluation" / "p5_05"
    / "repository_validation_report.json"
)
EVIDENCE_MAP_PATH = (
    ROOT / "outputs" / "evaluation" / "p5_05"
    / "final_evidence_map.json"
)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    evidence_map = json.loads(EVIDENCE_MAP_PATH.read_text(encoding="utf-8"))

    Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    ).validate(baseline)

    if baseline["baseline_status"] != "frozen":
        raise RuntimeError("Baseline is not frozen.")
    results = baseline["evaluation_results"]
    if (
        results["cases_passed"] != 19
        or results["assertions_passed"] != 262
        or results["regression_case_ids"]
        or results["frozen_inputs_changed"]
    ):
        raise RuntimeError("Final evaluation results changed.")

    for item in inventory["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Size mismatch: {item['path']}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Checksum mismatch: {item['path']}")

    if validation["validation_status"] != "PASS":
        raise RuntimeError("Repository validation did not pass.")
    if evidence_map["evidence_count"] < 19:
        raise RuntimeError("Final evidence map is incomplete.")
    if baseline["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary violated.")

    print(f"Frozen baseline: {baseline['baseline_id']}")
    print("Cases: 19/19")
    print("Assertions: 262/262")
    print(f"Inventory files verified: {inventory['file_count']}")
    print(f"Evidence areas verified: {evidence_map['evidence_count']}")
    print("Repository validation: PASS")
    print("External actions performed: 0")
    print("P5-05 final baseline verification: PASS")


if __name__ == "__main__":
    main()
