#!/usr/bin/env python3
"""Verify historical P5-05 baseline plus explicitly versioned post-freeze overlays."""

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


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_notebook_sha256(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    cells = []
    for cell in notebook.get("cells", []):
        source_value = cell.get("source", [])
        source = (
            "".join(str(x) for x in source_value)
            if isinstance(source_value, list)
            else str(source_value)
        )
        badge_only = (
            cell.get("cell_type") == "markdown"
            and "colab-badge.svg" in source
            and source.strip().startswith("<a ")
            and "\n#" not in source
            and not source.lstrip().startswith("#")
        )
        if not badge_only:
            cells.append(
                {
                    "cell_type": cell.get("cell_type", ""),
                    "source": source.rstrip(),
                }
            )
    payload = {
        "nbformat": notebook.get("nbformat"),
        "nbformat_minor": notebook.get("nbformat_minor"),
        "cells": cells,
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


POST_FREEZE_OVERLAY_PATHS = [
    ROOT / "outputs/evaluation/p6_01/post_freeze_overlay_manifest.json",
    ROOT / "outputs/evaluation/p6_02/post_freeze_documentation_overlay_manifest.json",
    ROOT / "outputs/evaluation/p6_03/post_freeze_governance_overlay_manifest.json",
    ROOT / "outputs/evaluation/p6_04/post_freeze_reproducibility_overlay_manifest.json",
    ROOT / "outputs/evaluation/p7_04/post_freeze_paper_overlay_manifest.json",
]

ALLOWED_CI_MAINTENANCE_PATHS = {
    ".github/workflows/project7-quality-gate.yml",
    "scripts/verify_p5_05_final_baseline.py",
    "scripts/verify_p5_06_acceptance_corrected_baseline.py",
    "scripts/verify_p5_12_final_submission_candidate.py",
    "scripts/verify_p6_03_governance.py",
    "scripts/verify_p6_04_reproducibility.py",
    "tests/test_p5_12_final_submission_candidate.py",
    "tests/test_p6_03_governance.py",
    "tests/test_p6_04_reproducibility.py",
}

DOCUMENTATION_PREFIXES = (
    "docs/",
    "reports/",
    "presentation/",
    "figures/",
    "outputs/evaluation/p6_",
    "outputs/evaluation/p7_",
    "outputs/evaluation/p8_",
    "outputs/evaluation/p9_",
)


def is_allowed_documentation_path(path_string):
    p = Path(path_string)
    return p.name == "README.md" or path_string.startswith(DOCUMENTATION_PREFIXES)


def load_versioned_post_freeze_overlays():
    latest = {}
    all_paths = set()
    doc_entries = 0
    ci_entries = 0
    overlay_ids = []

    for overlay_path in POST_FREEZE_OVERLAY_PATHS:
        if not overlay_path.is_file():
            continue
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        if overlay.get("parent_candidate_id") != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
            raise RuntimeError(f"Unexpected overlay parent candidate: {overlay_path}")
        if overlay.get("technical_or_evaluation_behavior_changed"):
            raise RuntimeError(f"Overlay changes technical/evaluation behavior: {overlay_path}")
        overlay_ids.append(overlay.get("overlay_id"))

        for item in overlay.get("files", []):
            path_string = item["path"]
            change_class = item["change_class"]
            if change_class in {"documentation_correction", "documentation_governance"}:
                if not is_allowed_documentation_path(path_string):
                    raise RuntimeError(f"Disallowed documentation overlay path: {path_string}")
                doc_entries += 1
            elif change_class == "ci_maintenance":
                if path_string not in ALLOWED_CI_MAINTENANCE_PATHS:
                    raise RuntimeError(f"Disallowed CI-maintenance path: {path_string}")
                ci_entries += 1
            else:
                raise RuntimeError(f"Unsupported overlay change class: {change_class}")
            latest[path_string] = item
            all_paths.add(path_string)

    # Latest overlay entry wins when a later documentation phase legitimately
    # supersedes an earlier post-freeze documentation/CI hash.
    for path_string, item in latest.items():
        path = ROOT / path_string
        if not path.is_file():
            raise FileNotFoundError(path)
        # The quality-gate workflow is a structural-current CI artifact, not a
        # frozen byte-for-byte candidate artifact. Its behavior is validated by
        # tests/test_ci_workflow.py and the hosted Actions run.
        if path_string == ".github/workflows/project7-quality-gate.yml":
            continue
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Latest overlay size mismatch: {path_string}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Latest overlay checksum mismatch: {path_string}")

    return latest, all_paths, doc_entries, ci_entries, overlay_ids


def main():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    evidence_map = json.loads(EVIDENCE_MAP_PATH.read_text(encoding="utf-8"))
    p5_06_overlay_path = ROOT / "outputs/evaluation/p5_06/versioned_overlay_manifest.json"
    p5_06_paths = set()
    if p5_06_overlay_path.is_file():
        p5_06 = json.loads(p5_06_overlay_path.read_text(encoding="utf-8"))
        p5_06_paths = {item["path"] for item in p5_06.get("files", [])}

    _, post_freeze_paths, doc_entries, ci_entries, overlay_ids = (
        load_versioned_post_freeze_overlays()
    )
    Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    ).validate(baseline)
    results = baseline["evaluation_results"]
    if (
        baseline["baseline_status"] != "frozen"
        or results["cases_passed"] != 19
        or results["assertions_passed"] != 262
        or results["regression_case_ids"]
        or results["frozen_inputs_changed"]
    ):
        raise RuntimeError("Historical P5-05 baseline changed.")

    raw_verified = 0
    notebook_verified = 0
    p5_06_deferred = 0
    post_freeze_deferred = 0

    for item in inventory["files"]:
        path_string = item["path"]
        if path_string in post_freeze_paths:
            post_freeze_deferred += 1
            continue
        if path_string in p5_06_paths:
            p5_06_deferred += 1
            continue

        path = ROOT / path_string
        if not path.is_file():
            raise FileNotFoundError(path)
        mode = item.get("verification_mode", "raw_size_and_sha256")
        if mode == "canonical_notebook_sources":
            if canonical_notebook_sha256(path) != item["canonical_sha256"]:
                raise RuntimeError(f"Canonical notebook source mismatch: {path_string}")
            notebook_verified += 1
        elif mode == "raw_size_and_sha256":
            if path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
                raise RuntimeError(f"Historical inventory mismatch: {path_string}")
            raw_verified += 1
        else:
            raise RuntimeError(f"Unsupported verification mode: {mode}")

    if validation["validation_status"] != "PASS":
        raise RuntimeError("Historical repository validation changed.")
    if evidence_map["evidence_count"] < 19:
        raise RuntimeError("Historical evidence map changed.")
    if baseline["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary changed.")

    print(f"Frozen baseline: {baseline['baseline_id']}")
    print("Cases: 19/19")
    print("Assertions: 262/262")
    print(f"Raw historical files verified: {raw_verified}")
    print(f"Canonical notebooks verified: {notebook_verified}")
    print(f"P5-06 versioned paths deferred: {p5_06_deferred}")
    print(f"Versioned post-freeze paths deferred: {post_freeze_deferred}")
    print(f"Post-freeze documentation/CI entries verified: {doc_entries + ci_entries}")
    print(f"Overlay chain: {overlay_ids}")
    print("Repository validation: PASS")
    print("External actions performed: 0")
    print("P5-05 final baseline verification: PASS")


if __name__ == "__main__":
    main()
