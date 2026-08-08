"""Verify the frozen P5-12 final candidate plus permitted P6-01 overlay."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P5 = ROOT / "outputs/evaluation/p5_05"
P6 = ROOT / "outputs/evaluation/p5_06"
P12 = ROOT / "outputs/evaluation/p5_12"
P6_01 = ROOT / "outputs/evaluation/p6_01"

STRICT_CI_MAINTENANCE_EXCEPTIONS = {
    "scripts/verify_p5_05_final_baseline.py",
    "scripts/verify_p5_06_acceptance_corrected_baseline.py",
}
ALLOWED_CI_MAINTENANCE_PATHS = {
    "scripts/verify_p5_05_final_baseline.py",
    "scripts/verify_p5_06_acceptance_corrected_baseline.py",
    "scripts/verify_p5_12_final_submission_candidate.py",
    "tests/test_p5_12_final_submission_candidate.py",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_allowed_documentation_path(path_string: str) -> bool:
    return (
        Path(path_string).name == "README.md"
        or path_string == "docs/ci/project7-quality-gate.yml"
    )


def verify_p6_01_overlay():
    overlay_path = P6_01 / "post_freeze_overlay_manifest.json"
    if not overlay_path.is_file():
        raise RuntimeError("P6-01 post-freeze overlay is missing.")

    overlay = load_json(overlay_path)
    if overlay["overlay_id"] != "PROJECT7-P6-01-POST-FREEZE-OVERLAY-v1.0.0":
        raise RuntimeError("Unexpected P6-01 overlay ID.")
    if overlay["parent_candidate_id"] != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
        raise RuntimeError("P6-01 overlay parent candidate changed.")
    if not overlay["documentation_only_and_ci_maintenance"]:
        raise RuntimeError("P6-01 overlay scope is not documentation/CI-only.")
    if overlay["technical_or_evaluation_behavior_changed"]:
        raise RuntimeError("P6-01 overlay changes technical/evaluation behavior.")

    items = {}
    doc_count = 0
    ci_count = 0
    for item in overlay["files"]:
        path_string = item["path"]
        change_class = item["change_class"]
        if change_class == "documentation_correction":
            if not is_allowed_documentation_path(path_string):
                raise RuntimeError(
                    f"Disallowed documentation correction: {path_string}"
                )
            doc_count += 1
        elif change_class == "ci_maintenance":
            if path_string not in ALLOWED_CI_MAINTENANCE_PATHS:
                raise RuntimeError(f"Disallowed CI maintenance: {path_string}")
            ci_count += 1
        else:
            raise RuntimeError(f"Unsupported overlay change class: {change_class}")

        path = ROOT / path_string
        if not path.is_file():
            raise RuntimeError(f"Overlay artifact missing: {path_string}")
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Overlay artifact size mismatch: {path_string}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Overlay artifact checksum mismatch: {path_string}")
        items[path_string] = item

    return overlay, items, doc_count, ci_count


def verify_ci_structure() -> None:
    workflow = (ROOT / ".github/workflows/project7-quality-gate.yml").read_text(
        encoding="utf-8"
    )
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
    _, p6_items, p6_doc_count, p6_ci_count = verify_p6_01_overlay()

    if manifest["candidate_id"] != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
        raise RuntimeError("Unexpected final candidate ID.")
    if manifest["candidate_status"] != "frozen":
        raise RuntimeError("Final candidate is not frozen.")

    if p5["baseline_id"] != "PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.0":
        raise RuntimeError("P5-05 baseline identity changed.")
    if p5["evaluation_results"]["cases_passed"] != 19:
        raise RuntimeError("P5-05 case result changed.")
    if p5["evaluation_results"]["assertions_passed"] != 262:
        raise RuntimeError("P5-05 assertion result changed.")

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
        raise RuntimeError("FR-02 bounded-model limitation treatment changed.")
    if finding_map["FR-03"]["disposition"] != "accepted":
        raise RuntimeError("FR-03 safe limitation treatment changed.")

    if visual["visual_acceptance_result"] != "PASS":
        raise RuntimeError("Final visual regression did not pass.")
    if not all(item["status"] == "PASS" for item in visual["checks"]):
        raise RuntimeError("At least one final visual acceptance check is not PASS.")
    if visual["recommendation"]["external_actions_performed"] != 0:
        raise RuntimeError("Visual acceptance recorded an external action.")

    files = inventory["files"]
    if inventory["strict_file_count"] != len(files) or len(files) < 40:
        raise RuntimeError("Strict freeze inventory is incomplete.")

    strict_verified = 0
    versioned_ci_verified = 0
    for item in files:
        path_string = item["path"]
        path = ROOT / path_string
        if not path.is_file():
            raise RuntimeError(f"Frozen artifact missing: {path_string}")

        if path_string in STRICT_CI_MAINTENANCE_EXCEPTIONS:
            overlay_item = p6_items.get(path_string)
            if not overlay_item or overlay_item["change_class"] != "ci_maintenance":
                raise RuntimeError(
                    f"Missing versioned CI-maintenance overlay for {path_string}"
                )
            versioned_ci_verified += 1
            continue

        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Frozen artifact size mismatch: {path_string}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Frozen artifact checksum mismatch: {path_string}")
        strict_verified += 1

    with (P12 / "final_submission_candidate_evidence_index.csv").open(
        newline="", encoding="utf-8"
    ) as f:
        evidence_rows = list(csv.DictReader(f))
    if len(evidence_rows) < 15:
        raise RuntimeError("Final evidence index is incomplete.")

    if manifest["findings_disposition"]["unresolved_critical_acceptance_defects"] != 0:
        raise RuntimeError("Critical acceptance defects remain unresolved.")
    if manifest["findings_disposition"]["unresolved_major_acceptance_defects"] != 0:
        raise RuntimeError("Major acceptance defects remain unresolved.")
    if manifest["external_actions_performed"] != 0:
        raise RuntimeError("Final candidate records external actions.")

    verify_ci_structure()

    print(f"Candidate: {manifest['candidate_id']}")
    print("Candidate status: frozen")
    print("Evaluation: 19/19 cases, 262/262 assertions")
    print(f"Strict technical/evaluation files verified unchanged: {strict_verified}")
    print(f"Versioned CI-maintenance strict exceptions verified: {versioned_ci_verified}")
    print(f"P6-01 documentation corrections verified: {p6_doc_count}")
    print(f"P6-01 CI-maintenance artifacts verified: {p6_ci_count}")
    print("Historical overlay 1.0.1 preserved: PASS")
    print("Active overlay 1.0.2: PASS")
    print("Final operator visual regression: PASS")
    print("Unresolved critical/major acceptance defects: 0")
    print("External actions performed: 0")
    print("P5-12 final submission-candidate verification with P6-01 overlay: PASS")


if __name__ == "__main__":
    main()
