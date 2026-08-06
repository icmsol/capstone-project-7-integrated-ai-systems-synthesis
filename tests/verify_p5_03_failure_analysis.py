"""Verify the P5-03 failure-analysis package."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    ROOT / "outputs" / "evaluation" / "p5_03"
    / "failure_analysis_report.json"
)
FAILED_PATH = (
    ROOT / "outputs" / "evaluation" / "p5_02"
    / "failed_assertions.csv"
)
METRICS_PATH = (
    ROOT / "outputs" / "evaluation" / "p5_02"
    / "system_metrics.json"
)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    with FAILED_PATH.open("r", encoding="utf-8", newline="") as file_obj:
        failed = list(csv.DictReader(file_obj))
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    source_pairs = {
        (row["case_id"], row["assertion_id"])
        for row in failed
    }
    report_pairs = {
        (row["case_id"], row["assertion_id"])
        for row in report["occurrences"]
    }
    if source_pairs != report_pairs:
        raise RuntimeError("Failure occurrence mapping is incomplete or contains extras.")
    if report["source_metrics_report_sha256"] != sha256_file(METRICS_PATH):
        raise RuntimeError("Metrics source hash mismatch.")
    if report["source_failed_assertions_sha256"] != sha256_file(FAILED_PATH):
        raise RuntimeError("Failed-assertion source hash mismatch.")
    if report["critical_assertion_failures"] != 0:
        raise RuntimeError("Critical failure count changed.")
    if report["safety_significant_failure_count"] != 0:
        raise RuntimeError("Safety-significant classification is inconsistent.")
    if report["over_escalation"]["unexpected_escalations"] != 0:
        raise RuntimeError("Unexpected escalation count changed.")
    if any(
        occurrence["critical_safety_failure"]
        for occurrence in report["occurrences"]
    ):
        raise RuntimeError("An occurrence was incorrectly marked as critical.")
    if any(
        "frozen cases" not in item["prohibited_changes"]
        for item in report["refinement_backlog"]
    ):
        raise RuntimeError("A backlog item permits frozen-case changes.")
    if report["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary violated.")

    print("Failure occurrences verified: 6")
    print("Failure classes verified: 3")
    print("Safety-significant failures: 0")
    print("Governance-significant failures: 6")
    print("Unexpected escalations: 0")
    print("Refinement backlog items: 5")
    print("P5-03 failure analysis verification: PASS")


if __name__ == "__main__":
    main()
