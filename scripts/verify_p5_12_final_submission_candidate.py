"""Verify frozen P5-12 candidate plus explicitly versioned post-freeze documentation overlays."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P5 = ROOT / "outputs/evaluation/p5_05"
P6 = ROOT / "outputs/evaluation/p5_06"
P12 = ROOT / "outputs/evaluation/p5_12"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


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
        if path_string == ".github/workflows/project7-quality-gate.yml":
            continue
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"Latest overlay size mismatch: {path_string}")
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Latest overlay checksum mismatch: {path_string}")

    return latest, all_paths, doc_entries, ci_entries, overlay_ids


def verify_ci_structure():
    text = (ROOT / ".github/workflows/project7-quality-gate.yml").read_text(encoding="utf-8")
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
        if marker not in text:
            raise RuntimeError(f"CI invariant missing: {marker}")
    lowered = text.lower()
    for marker in ["docker push", "twine upload", "npm publish", "kubectl apply"]:
        if marker in lowered:
            raise RuntimeError(f"Prohibited deployment/publish action: {marker}")


def main():
    manifest = load_json(P12 / "final_submission_candidate_manifest.json")
    inventory = load_json(P12 / "final_submission_candidate_strict_inventory.json")
    visual = load_json(P12 / "final_visual_regression_acceptance.json")
    p5 = load_json(P5 / "final_evaluation_baseline.json")
    p6 = load_json(P6 / "acceptance_corrected_baseline.json")
    active_overlay = load_json(P6 / "versioned_overlay_manifest.json")
    historical_overlay = load_json(P6 / "versioned_overlay_manifest_v1.0.1.json")
    findings = load_json(P12 / "operator_hardening_findings.json")
    _, post_freeze_paths, doc_entries, ci_entries, overlay_ids = (
        load_versioned_post_freeze_overlays()
    )

    if manifest["candidate_id"] != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
        raise RuntimeError("Candidate identity changed.")
    if manifest["candidate_status"] != "frozen":
        raise RuntimeError("Candidate status changed.")
    if p5["baseline_id"] != "PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.0":
        raise RuntimeError("P5-05 identity changed.")
    if (
        p5["evaluation_results"]["cases_passed"] != 19
        or p5["evaluation_results"]["assertions_passed"] != 262
    ):
        raise RuntimeError("P5-05 result changed.")
    if p6["baseline_id"] != "PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.1":
        raise RuntimeError("P5-06 identity changed.")
    if p6["parent_baseline_id"] != p5["baseline_id"]:
        raise RuntimeError("P5-06 lineage changed.")
    if historical_overlay["overlay_version"] != "1.0.1":
        raise RuntimeError("Historical overlay changed.")
    if active_overlay["overlay_version"] != "1.0.2" or active_overlay["frozen_scenario_inputs_changed"]:
        raise RuntimeError("Active technical overlay changed.")

    finding_map = {x["finding_id"]: x for x in findings["findings"]}
    for finding_id in ["FR-01", "FR-04", "FR-05"]:
        if not finding_map[finding_id]["disposition"].startswith("corrected"):
            raise RuntimeError(f"{finding_id} changed.")
    if finding_map["FR-02"]["disposition"] != "documented_and_operator_warning_strengthened":
        raise RuntimeError("FR-02 disposition changed.")
    if finding_map["FR-03"]["disposition"] != "accepted":
        raise RuntimeError("FR-03 disposition changed.")
    if visual["visual_acceptance_result"] != "PASS":
        raise RuntimeError("Final visual regression changed.")
    if not all(x["status"] == "PASS" for x in visual["checks"]):
        raise RuntimeError("Final visual checks changed.")

    strict_verified = 0
    superseded = 0
    for item in inventory["files"]:
        path_string = item["path"]
        path = ROOT / path_string
        if not path.is_file():
            raise RuntimeError(f"Frozen artifact missing: {path_string}")
        if path_string in post_freeze_paths:
            superseded += 1
            continue
        if path.stat().st_size != item["bytes"] or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Frozen artifact mismatch: {path_string}")
        strict_verified += 1

    with (P12 / "final_submission_candidate_evidence_index.csv").open(
        newline="",
        encoding="utf-8",
    ) as f:
        evidence_rows = list(csv.DictReader(f))
    if len(evidence_rows) < 15:
        raise RuntimeError("Final evidence index incomplete.")
    if manifest["findings_disposition"]["unresolved_critical_acceptance_defects"] != 0:
        raise RuntimeError("Critical acceptance defect present.")
    if manifest["findings_disposition"]["unresolved_major_acceptance_defects"] != 0:
        raise RuntimeError("Major acceptance defect present.")
    if manifest["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary changed.")

    verify_ci_structure()
    print(f"Candidate: {manifest['candidate_id']}")
    print("Candidate status: frozen")
    print("Evaluation: 19/19 cases, 262/262 assertions")
    print(f"Strict frozen technical/evaluation files unchanged: {strict_verified}")
    print(f"Strict paths superseded only by versioned post-freeze overlays: {superseded}")
    print(f"Post-freeze documentation entries verified: {doc_entries}")
    print(f"Post-freeze CI-maintenance entries verified: {ci_entries}")
    print(f"Overlay chain: {overlay_ids}")
    print("Final operator visual regression: PASS")
    print("Unresolved critical/major acceptance defects: 0")
    print("External actions performed: 0")
    print("P5-12 final candidate with versioned post-freeze documentation overlays: PASS")


if __name__ == "__main__":
    main()
