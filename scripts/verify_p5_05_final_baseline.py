#!/usr/bin/env python3
"""Verify the frozen Project 7 final evaluation baseline.

Normal files use strict raw size and SHA-256 verification. Jupyter notebooks use
a canonical source digest because Colab/GitHub may add execution outputs,
execution counts, IDs, volatile metadata, or a duplicate badge-only cell without
changing the executable notebook source.

Explicitly versioned post-freeze documentation corrections and CI-maintenance
artifacts are verified through the P6-01 overlay rather than compared against
their historical P5-05 bytes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "outputs/evaluation/p5_05/final_evaluation_baseline.json"
SCHEMA_PATH = ROOT / "config/schemas/final_evaluation_baseline.schema.json"
INVENTORY_PATH = ROOT / "outputs/evaluation/p5_05/final_artifact_inventory.json"
VALIDATION_PATH = ROOT / "outputs/evaluation/p5_05/repository_validation_report.json"
EVIDENCE_MAP_PATH = ROOT / "outputs/evaluation/p5_05/final_evidence_map.json"
P6_01_OVERLAY_PATH = ROOT / "outputs/evaluation/p6_01/post_freeze_overlay_manifest.json"

ALLOWED_CI_MAINTENANCE_PATHS = {
    "scripts/verify_p5_05_final_baseline.py",
    "scripts/verify_p5_06_acceptance_corrected_baseline.py",
    "scripts/verify_p5_12_final_submission_candidate.py",
    "tests/test_p5_12_final_submission_candidate.py",
}


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_notebook_sha256(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    normalized_cells = []
    for cell in notebook.get("cells", []):
        cell_type = cell.get("cell_type", "")
        source_value = cell.get("source", [])
        if isinstance(source_value, list):
            source = "".join(str(item) for item in source_value)
        else:
            source = str(source_value)
        badge_only = (
            cell_type == "markdown"
            and "colab-badge.svg" in source
            and source.strip().startswith("<a ")
            and "\n#" not in source
            and not source.lstrip().startswith("#")
        )
        if badge_only:
            continue
        normalized_cells.append(
            {"cell_type": cell_type, "source": source.rstrip()}
        )
    payload = {
        "nbformat": notebook.get("nbformat"),
        "nbformat_minor": notebook.get("nbformat_minor"),
        "cells": normalized_cells,
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def is_allowed_documentation_path(path_string):
    return (
        Path(path_string).name == "README.md"
        or path_string == "docs/ci/project7-quality-gate.yml"
    )


def verify_post_freeze_overlay():
    if not P6_01_OVERLAY_PATH.is_file():
        return set(), 0, 0

    overlay = json.loads(P6_01_OVERLAY_PATH.read_text(encoding="utf-8"))
    if overlay.get("overlay_id") != "PROJECT7-P6-01-POST-FREEZE-OVERLAY-v1.0.0":
        raise RuntimeError("Unexpected P6-01 post-freeze overlay ID.")
    if overlay.get("parent_candidate_id") != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
        raise RuntimeError("P6-01 overlay parent candidate changed.")
    if not overlay.get("documentation_only_and_ci_maintenance"):
        raise RuntimeError("P6-01 overlay is not constrained to documentation/CI maintenance.")
    if overlay.get("technical_or_evaluation_behavior_changed"):
        raise RuntimeError("P6-01 overlay claims a technical/evaluation behavior change.")

    paths = set()
    documentation_count = 0
    ci_count = 0
    for item in overlay.get("files", []):
        path_string = item["path"]
        change_class = item["change_class"]
        if change_class == "documentation_correction":
            if not is_allowed_documentation_path(path_string):
                raise RuntimeError(
                    f"Disallowed documentation-overlay path: {path_string}"
                )
            documentation_count += 1
        elif change_class == "ci_maintenance":
            if path_string not in ALLOWED_CI_MAINTENANCE_PATHS:
                raise RuntimeError(f"Disallowed CI-maintenance path: {path_string}")
            ci_count += 1
        else:
            raise RuntimeError(
                f"Unsupported P6-01 overlay change class: {change_class}"
            )

        path = ROOT / path_string
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"P6-01 overlay size mismatch: {path_string}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"P6-01 overlay checksum mismatch: {path_string}")
        paths.add(path_string)

    return paths, documentation_count, ci_count


def main():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    evidence_map = json.loads(EVIDENCE_MAP_PATH.read_text(encoding="utf-8"))
    overlay_path = ROOT / "outputs/evaluation/p5_06/versioned_overlay_manifest.json"

    p5_06_paths = set()
    if overlay_path.is_file():
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        p5_06_paths = {item["path"] for item in overlay.get("files", [])}

    p6_01_paths, p6_doc_count, p6_ci_count = verify_post_freeze_overlay()

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

    raw_verified = 0
    notebook_verified = 0
    p5_06_deferred = 0
    p6_01_deferred = 0

    for item in inventory["files"]:
        if item["path"] in p6_01_paths:
            p6_01_deferred += 1
            continue
        if item["path"] in p5_06_paths:
            p5_06_deferred += 1
            continue

        path = ROOT / item["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        mode = item.get("verification_mode", "raw_size_and_sha256")
        if mode == "canonical_notebook_sources":
            observed = canonical_notebook_sha256(path)
            if observed != item["canonical_sha256"]:
                raise RuntimeError(
                    f"Canonical notebook source mismatch: {item['path']}"
                )
            notebook_verified += 1
        elif mode == "raw_size_and_sha256":
            if path.stat().st_size != item["bytes"]:
                raise RuntimeError(f"Size mismatch: {item['path']}")
            if sha256_file(path) != item["sha256"]:
                raise RuntimeError(f"Checksum mismatch: {item['path']}")
            raw_verified += 1
        else:
            raise RuntimeError(
                f"Unsupported verification mode for {item['path']}: {mode}"
            )

    if validation["validation_status"] != "PASS":
        raise RuntimeError("Repository validation did not pass.")
    if evidence_map["evidence_count"] < 19:
        raise RuntimeError("Final evidence map is incomplete.")
    if baseline["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary violated.")

    print(f"Frozen baseline: {baseline['baseline_id']}")
    print("Cases: 19/19")
    print("Assertions: 262/262")
    print(f"Raw historical files verified: {raw_verified}")
    print(f"Canonical notebooks verified: {notebook_verified}")
    print(f"P5-06 versioned overlay paths deferred: {p5_06_deferred}")
    print(f"P6-01 versioned documentation paths verified: {p6_doc_count}")
    print(f"P6-01 versioned CI-maintenance paths verified: {p6_ci_count}")
    print(f"P6-01 historical inventory paths deferred: {p6_01_deferred}")
    print(f"Evidence areas verified: {evidence_map['evidence_count']}")
    print("Repository validation: PASS")
    print("External actions performed: 0")
    print("P5-05 final baseline verification: PASS")


if __name__ == "__main__":
    main()
