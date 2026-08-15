#!/usr/bin/env python3
"""Verify P5-06 acceptance-corrected baseline with later versioned documentation/CI overlays."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "outputs/evaluation/p5_06/acceptance_corrected_baseline.json"
SCHEMA_PATH = ROOT / "config/schemas/acceptance_corrected_baseline.schema.json"
OVERLAY_PATH = ROOT / "outputs/evaluation/p5_06/versioned_overlay_manifest.json"
RERUN_PATH = ROOT / "outputs/evaluation/p5_06/frozen_suite_rerun_summary.json"
FINDINGS_PATH = ROOT / "outputs/evaluation/p5_06/manual_operator_acceptance_findings.json"


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


POST_FREEZE_OVERLAY_PATHS = [
    ROOT / "outputs/evaluation/p6_01/post_freeze_overlay_manifest.json",
    ROOT / "outputs/evaluation/p6_02/post_freeze_documentation_overlay_manifest.json",
    ROOT / "outputs/evaluation/p6_03/post_freeze_governance_overlay_manifest.json",
    ROOT / "outputs/evaluation/p6_04/post_freeze_reproducibility_overlay_manifest.json",
    ROOT / "outputs/evaluation/p7_04/post_freeze_paper_overlay_manifest.json",
    ROOT / "outputs/evaluation/p8_04/post_freeze_presentation_overlay_manifest.json",
    ROOT / "outputs/evaluation/p9_02/post_freeze_submission_environment_overlay_manifest.json",
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
    "scripts/verify_p9_02_submission_environment.py",
    "tests/test_ci_workflow.py",
}

ALLOWED_ENVIRONMENT_LOCK_PATHS = {"requirements.txt"}

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
    environment_entries = 0
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
            elif change_class == "environment_lock":
                if path_string not in ALLOWED_ENVIRONMENT_LOCK_PATHS:
                    raise RuntimeError(f"Disallowed environment-lock path: {path_string}")
                environment_entries += 1
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
        if path_string == ".github/workflows/project7-quality-gate.yml":
            continue
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Latest overlay size mismatch: {path_string}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Latest overlay checksum mismatch: {path_string}")

    return latest, all_paths, doc_entries, ci_entries, environment_entries, overlay_ids


def verify_current_ci(path):
    text = path.read_text(encoding="utf-8")
    required = [
        "permissions:",
        "contents: read",
        'python-version: "3.12"',
        "verify_p5_05_final_baseline.py",
        "verify_p5_06_acceptance_corrected_baseline.py",
        "requirements.txt",
        "verify_p9_02_submission_environment.py",
        "actions/upload-artifact@v7",
    ]
    for marker in required:
        if marker not in text:
            raise RuntimeError(f"CI invariant missing: {marker}")


def main():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    rerun = json.loads(RERUN_PATH.read_text(encoding="utf-8"))
    findings = json.loads(FINDINGS_PATH.read_text(encoding="utf-8"))

    _, post_freeze_paths, _, _, _, overlay_ids = load_versioned_post_freeze_overlays()
    Draft202012Validator(schema).validate(baseline)
    results = baseline["evaluation_results"]
    if (
        results["cases_passed"] != 19
        or results["assertions_passed"] != 262
        or results["regressions"] != 0
        or results["frozen_inputs_changed"]
    ):
        raise RuntimeError("P5-06 baseline changed.")
    if rerun["status_counts"] != {"PASS": 19, "PARTIAL": 0, "FAIL": 0}:
        raise RuntimeError("Frozen-suite status counts changed.")
    if rerun["assertions_passed"] != rerun["assertions_total"]:
        raise RuntimeError("Frozen-suite assertions changed.")

    finding_map = {item["finding_id"]: item for item in findings["findings"]}
    for finding_id in ["MAF-02", "MAF-04", "MAF-05"]:
        if finding_map[finding_id]["disposition"] != "corrected":
            raise RuntimeError(f"{finding_id} correction evidence changed.")

    strict_verified = 0
    structural_verified = 0
    superseded = 0
    for item in overlay["files"]:
        path_string = item["path"]
        path = ROOT / path_string
        if not path.is_file():
            raise FileNotFoundError(path)

        if path_string in post_freeze_paths:
            superseded += 1
            continue

        mode = item.get("verification_mode", "strict_sha256")
        if mode == "strict_sha256":
            if sha256_file(path) != item["sha256"]:
                raise RuntimeError(f"P5-06 historical overlay mismatch: {path_string}")
            strict_verified += 1
        elif mode == "structural_current_ci":
            verify_current_ci(path)
            structural_verified += 1
        else:
            raise RuntimeError(f"Unsupported P5-06 verification mode: {mode}")

    if baseline["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary changed.")

    print(f"Acceptance-corrected baseline: {baseline['baseline_id']}")
    print("Frozen cases rerun: 19/19 PASS")
    print("Frozen assertions rerun: 262/262 PASS")
    print(f"Historical strict overlay files verified: {strict_verified}")
    print(f"P5-06 paths superseded by versioned post-freeze overlays: {superseded}")
    print(f"Mutable CI workflow invariants verified: {structural_verified}")
    print(f"Post-freeze overlay chain: {overlay_ids}")
    print("MAF-02, MAF-04, MAF-05 correction evidence: PASS")
    print("External actions performed: 0")
    print("P5-06 acceptance-corrected baseline verification: PASS")


if __name__ == "__main__":
    main()
