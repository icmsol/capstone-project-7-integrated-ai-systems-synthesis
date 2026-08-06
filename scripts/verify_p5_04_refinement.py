#!/usr/bin/env python3
"""Verify the preserved P5-04 refined evaluation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "outputs/evaluation/p5_04/refined_run_manifest.json").read_text(encoding="utf-8"))
COMPARISON = json.loads((ROOT / "outputs/evaluation/p5_04/before_after_metrics.json").read_text(encoding="utf-8"))
LOCK = json.loads((ROOT / "config/system/p5_01_freeze_lock.json").read_text(encoding="utf-8"))


def sha256_file(path):
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    mismatches = []
    for item in LOCK["locked_files"]:
        path = ROOT / item["path"]
        if not path.is_file() or path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
            mismatches.append(item["path"])
    if mismatches:
        raise RuntimeError("Frozen input mismatch: " + ", ".join(mismatches))
    expected_improved = {"TC-03", "TC-05", "TC-10", "TC-14", "TC-15", "TC-18"}
    if set(MANIFEST["improved_case_ids"]) != expected_improved:
        raise RuntimeError("Improved case set changed.")
    if MANIFEST["case_count_executed"] != 19 or MANIFEST["assertion_count_passed"] != 262:
        raise RuntimeError("Refined run is incomplete.")
    if MANIFEST["status_counts"] != {"PASS": 19, "PARTIAL": 0, "FAIL": 0}:
        raise RuntimeError("Refined case status counts changed.")
    if MANIFEST["regression_case_ids"]:
        raise RuntimeError("Unexpected regression detected.")
    if COMPARISON["after"]["audit_event_classification"] != {"numerator": 19, "denominator": 19}:
        raise RuntimeError("Audit event classification is not fully conformant.")
    if COMPARISON["after"]["component_attribution"] != {"numerator": 19, "denominator": 19}:
        raise RuntimeError("Component attribution is not fully conformant.")
    if MANIFEST["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary violated.")
    print("Frozen inputs verified unchanged: PASS")
    print("Cases executed: 19/19")
    print("Assertions passed: 262/262")
    print("Improved cases: 6")
    print("Regressions: 0")
    print("Audit event classification: 19/19")
    print("Component attribution: 19/19")
    print("P5-04 refinement verification: PASS")


if __name__ == "__main__":
    main()
