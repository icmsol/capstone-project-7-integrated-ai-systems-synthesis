#!/usr/bin/env python3
"""Verify the versioned P5-06 acceptance-corrected Project 7 baseline."""

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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    overlay = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    rerun = json.loads(RERUN_PATH.read_text(encoding="utf-8"))
    findings = json.loads(FINDINGS_PATH.read_text(encoding="utf-8"))

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

    verified = 0
    for item in overlay["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        observed = sha256_file(path)
        if observed != item["sha256"]:
            raise RuntimeError(f"P5-06 overlay checksum mismatch: {item['path']}")
        verified += 1

    if baseline["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary violated.")

    print(f"Acceptance-corrected baseline: {baseline['baseline_id']}")
    print("Frozen cases rerun: 19/19 PASS")
    print("Frozen assertions rerun: 262/262 PASS")
    print(f"Versioned overlay files verified: {verified}")
    print("MAF-02, MAF-04, MAF-05 correction evidence: PASS")
    print("External actions performed: 0")
    print("P5-06 acceptance-corrected baseline verification: PASS")


if __name__ == "__main__":
    main()
