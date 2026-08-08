"""Verify the frozen P5-12 final submission candidate."""

from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P5 = ROOT / "outputs/evaluation/p5_05"
P6 = ROOT / "outputs/evaluation/p5_06"
P12 = ROOT / "outputs/evaluation/p5_12"

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_ci_structure() -> None:
    workflow = (ROOT / ".github/workflows/project7-quality-gate.yml").read_text(encoding="utf-8")
    required = [
        "permissions:",
        "contents: read",
        'python-version: "3.12"',
        "verify_p5_05_final_baseline.py",
        "verify_p5_06_acceptance_corrected_baseline.py",
        "validate_operator_interface.py",
        "verify_p5_12_operator_hardening.py",
        "verify_p5_12_final_submission_candidate.py",
        "tests.test_p5_12_final_submission_candidate",
        "actions/upload-artifact@v7",
    ]
    for marker in required:
        if marker not in workflow:
            raise RuntimeError(f"Missing CI invariant: {marker}")
    lowered = workflow.lower()
    for marker in ["docker push", "twine upload", "npm publish", "kubectl apply"]:
        if marker in lowered:
            raise RuntimeError(f"Prohibited publish/deploy CI action: {marker}")

def main() -> None:
    manifest = load_json(P12 / "final_submission_candidate_manifest.json")
    inventory = load_json(P12 / "final_submission_candidate_strict_inventory.json")
    visual = load_json(P12 / "final_visual_regression_acceptance.json")
    p5 = load_json(P5 / "final_evaluation_baseline.json")
    p6 = load_json(P6 / "acceptance_corrected_baseline.json")
    active_overlay = load_json(P6 / "versioned_overlay_manifest.json")
    historical_overlay = load_json(P6 / "versioned_overlay_manifest_v1.0.1.json")
    findings = load_json(P12 / "operator_hardening_findings.json")

    if manifest["candidate_id"] != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
        raise RuntimeError("Unexpected final candidate ID.")
    if manifest["candidate_status"] != "frozen":
        raise RuntimeError("Final candidate is not frozen.")
    if p5["baseline_id"] != "PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.0":
        raise RuntimeError("P5-05 baseline identity changed.")
    if p5["evaluation_results"]["cases_passed"] != 19 or p5["evaluation_results"]["assertions_passed"] != 262:
        raise RuntimeError("P5-05 evaluation result changed.")
    if p6["baseline_id"] != "PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.1":
        raise RuntimeError("P5-06 baseline identity changed.")
    if p6["parent_baseline_id"] != p5["baseline_id"]:
        raise RuntimeError("P5-06 parent baseline changed.")
    if historical_overlay["overlay_version"] != "1.0.1":
        raise RuntimeError("Historical P5-06 overlay was not preserved.")
    if active_overlay["overlay_version"] != "1.0.2":
        raise RuntimeError("Active P5-12 overlay is not v1.0.2.")
    if active_overlay["frozen_scenario_inputs_changed"]:
        raise RuntimeError("Frozen scenario inputs changed.")

    finding_map = {item["finding_id"]: item for item in findings["findings"]}
    for finding_id in ["FR-01", "FR-04", "FR-05"]:
        if not finding_map[finding_id]["disposition"].startswith("corrected"):
            raise RuntimeError(f"{finding_id} was not corrected.")
    if finding_map["FR-02"]["disposition"] != "documented_and_operator_warning_strengthened":
        raise RuntimeError("FR-02 treatment changed.")
    if finding_map["FR-03"]["disposition"] != "accepted":
        raise RuntimeError("FR-03 treatment changed.")

    if visual["visual_acceptance_result"] != "PASS":
        raise RuntimeError("Final visual regression did not pass.")
    if not all(item["status"] == "PASS" for item in visual["checks"]):
        raise RuntimeError("At least one final visual check is not PASS.")
    if visual["recommendation"]["external_actions_performed"] != 0:
        raise RuntimeError("Visual acceptance recorded an external action.")

    files = inventory["files"]
    if inventory["strict_file_count"] != len(files) or len(files) < 40:
        raise RuntimeError("Strict freeze inventory is incomplete.")
    for item in files:
        path = ROOT / item["path"]
        if not path.is_file():
            raise RuntimeError(f"Frozen artifact missing: {item['path']}")
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Frozen artifact size mismatch: {item['path']}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Frozen artifact checksum mismatch: {item['path']}")

    with (P12 / "final_submission_candidate_evidence_index.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) < 15:
        raise RuntimeError("Final evidence index is incomplete.")

    if manifest["findings_disposition"]["unresolved_critical_acceptance_defects"] != 0:
        raise RuntimeError("Critical acceptance defects remain.")
    if manifest["findings_disposition"]["unresolved_major_acceptance_defects"] != 0:
        raise RuntimeError("Major acceptance defects remain.")
    if manifest["external_actions_performed"] != 0:
        raise RuntimeError("Final candidate records external actions.")

    verify_ci_structure()
    print(f"Candidate: {manifest['candidate_id']}")
    print("Candidate status: frozen")
    print("Evaluation: 19/19 cases, 262/262 assertions")
    print(f"Strict technical/evaluation files verified: {len(files)}")
    print("Historical overlay 1.0.1 preserved: PASS")
    print("Active overlay 1.0.2: PASS")
    print("Final operator visual regression: PASS")
    print("Unresolved critical/major acceptance defects: 0")
    print("External actions performed: 0")
    print("P5-12 final submission-candidate verification: PASS")

if __name__ == "__main__":
    main()
