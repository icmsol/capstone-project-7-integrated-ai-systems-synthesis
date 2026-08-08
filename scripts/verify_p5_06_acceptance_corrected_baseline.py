#!/usr/bin/env python3
"""Verify the versioned P5-06 acceptance-corrected baseline.

The historical P5-06 overlay remains authoritative for the acceptance correction.
Explicitly versioned P6-01 CI-maintenance artifacts may supersede historical
verifier bytes without changing evaluation/model behavior.
"""

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
P6_01_OVERLAY_PATH = ROOT / "outputs/evaluation/p6_01/post_freeze_overlay_manifest.json"

ALLOWED_P6_CI_MAINTENANCE = {
    "scripts/verify_p5_05_final_baseline.py",
    "scripts/verify_p5_06_acceptance_corrected_baseline.py",
    "scripts/verify_p5_12_final_submission_candidate.py",
    "tests/test_p5_12_final_submission_candidate.py",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_current_ci_workflow(path: Path) -> None:
    workflow = path.read_text(encoding="utf-8")
    required = [
        "permissions:",
        "contents: read",
        'python-version: "3.12"',
        "verify_p5_05_final_baseline.py",
        "verify_p5_06_acceptance_corrected_baseline.py",
        "actions/upload-artifact@v7",
    ]
    for marker in required:
        if marker not in workflow:
            raise RuntimeError(f"Current CI workflow missing invariant: {marker}")


def load_p6_ci_maintenance():
    if not P6_01_OVERLAY_PATH.is_file():
        return {}
    overlay = json.loads(P6_01_OVERLAY_PATH.read_text(encoding="utf-8"))
    if overlay.get("overlay_id") != "PROJECT7-P6-01-POST-FREEZE-OVERLAY-v1.0.0":
        raise RuntimeError("Unexpected P6-01 overlay ID.")
    if overlay.get("technical_or_evaluation_behavior_changed"):
        raise RuntimeError("P6-01 overlay changes technical/evaluation behavior.")

    items = {}
    for item in overlay.get("files", []):
        if item.get("change_class") != "ci_maintenance":
            continue
        path_string = item["path"]
        if path_string not in ALLOWED_P6_CI_MAINTENANCE:
            raise RuntimeError(f"Disallowed P6-01 CI-maintenance path: {path_string}")
        path = ROOT / path_string
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"P6-01 CI-maintenance size mismatch: {path_string}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"P6-01 CI-maintenance checksum mismatch: {path_string}")
        items[path_string] = item
    return items


def main() -> None:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    rerun = json.loads(RERUN_PATH.read_text(encoding="utf-8"))
    findings = json.loads(FINDINGS_PATH.read_text(encoding="utf-8"))
    p6_ci_items = load_p6_ci_maintenance()

    Draft202012Validator(schema).validate(baseline)

    results = baseline["evaluation_results"]
    if (
        results["cases_passed"] != 19
        or results["assertions_passed"] != 262
        or results["regressions"] != 0
        or results["frozen_inputs_changed"]
    ):
        raise RuntimeError("Acceptance-corrected baseline regression result changed.")

    if rerun["status_counts"] != {"PASS": 19, "PARTIAL": 0, "FAIL": 0}:
        raise RuntimeError("Frozen-suite rerun is not 19/19 PASS.")
    if rerun["assertions_passed"] != rerun["assertions_total"]:
        raise RuntimeError("Frozen-suite assertions are not all passing.")

    finding_map = {item["finding_id"]: item for item in findings["findings"]}
    for finding_id in ["MAF-02", "MAF-04", "MAF-05"]:
        if finding_map[finding_id]["disposition"] != "corrected":
            raise RuntimeError(f"{finding_id} is not recorded as corrected.")

    strict_verified = 0
    structural_verified = 0
    versioned_ci_verified = 0

    for item in overlay["files"]:
        path_string = item["path"]
        path = ROOT / path_string
        if not path.is_file():
            raise FileNotFoundError(path)

        if path_string in p6_ci_items:
            versioned_ci_verified += 1
            continue

        mode = item.get("verification_mode", "strict_sha256")
        if mode == "strict_sha256":
            observed = sha256_file(path)
            if observed != item["sha256"]:
                raise RuntimeError(f"P5-06 overlay checksum mismatch: {path_string}")
            strict_verified += 1
        elif mode == "structural_current_ci":
            verify_current_ci_workflow(path)
            structural_verified += 1
        else:
            raise RuntimeError(
                f"Unsupported P5-06 overlay verification mode for {path_string}: {mode}"
            )

    if baseline["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary violated.")

    print(f"Acceptance-corrected baseline: {baseline['baseline_id']}")
    print("Frozen cases rerun: 19/19 PASS")
    print("Frozen assertions rerun: 262/262 PASS")
    print(f"Historical strict overlay files verified: {strict_verified}")
    print(f"Versioned P6-01 CI-maintenance overlay files verified: {versioned_ci_verified}")
    print(f"Mutable CI workflow invariants verified: {structural_verified}")
    print("MAF-02, MAF-04, MAF-05 correction evidence: PASS")
    print("External actions performed: 0")
    print("P5-06 acceptance-corrected baseline verification: PASS")


if __name__ == "__main__":
    main()
