#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    manifest = json.loads((ROOT / "outputs/evaluation/p6_04/reproducibility_manifest.json").read_text())
    env = json.loads((ROOT / "outputs/evaluation/p6_04/environment_and_version_spec.json").read_text())
    sources = read_csv(ROOT / "docs/P6_04_Source_Snapshot_and_Checksum_Inventory.csv")
    replay = read_csv(ROOT / "docs/P6_04_Replay_Matrix.csv")
    candidate = json.loads((ROOT / "outputs/evaluation/p5_12/final_submission_candidate_manifest.json").read_text())
    strict = json.loads((ROOT / "outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json").read_text())

    if manifest["candidate_id"] != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
        raise RuntimeError("Candidate ID changed.")
    if manifest["candidate_id"] != candidate["candidate_id"]:
        raise RuntimeError("P6-04 candidate reference does not match frozen candidate.")
    if manifest["candidate_freeze_reference"]["strict_file_count"] != strict["strict_file_count"]:
        raise RuntimeError("Strict inventory count mismatch.")
    if manifest["frozen_evaluation"]["deterministic_seed"] != 42:
        raise RuntimeError("Frozen evaluation seed changed.")
    if manifest["frozen_evaluation"]["cases_passed"] != 19 or manifest["frozen_evaluation"]["assertions_passed"] != 262:
        raise RuntimeError("Frozen evaluation result changed.")
    if manifest["project4_model"]["checkpoint_sha256"] != "50a280950d31466d7002578295c64e957d144611f5b9731bb059be50e68c6c92":
        raise RuntimeError("Project 4 checkpoint identity changed.")
    if env["api_and_format_versions"]["openai_api_runtime_dependency"]:
        raise RuntimeError("Project 7 final runtime incorrectly claims an OpenAI API dependency.")
    if manifest["governance"]["production_ready"]:
        raise RuntimeError("P6-04 incorrectly claims production readiness.")
    if manifest["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary changed.")
    if len(replay) != 10:
        raise RuntimeError("Replay matrix must contain 10 replay scopes.")

    for row in sources:
        path = row["repository_path_or_external_reference"]
        if path.startswith("http"):
            continue
        p = ROOT / path
        if not p.exists():
            raise RuntimeError(f"Source inventory path missing: {path}")
        if row["sha256"] and sha256(p) != row["sha256"]:
            raise RuntimeError(f"Source checksum mismatch: {path}")
        if row["bytes"] and p.stat().st_size != int(row["bytes"]):
            raise RuntimeError(f"Source size mismatch: {path}")

    for overlay in manifest["post_freeze_overlays"]:
        p = ROOT / overlay["path"]
        if not p.exists():
            raise RuntimeError(f"Overlay missing: {overlay['path']}")
        if sha256(p) != overlay["sha256"]:
            raise RuntimeError(f"Overlay checksum mismatch: {overlay['path']}")

    print("Frozen candidate: PROJECT7-SUBMISSION-CANDIDATE-v1.0.0")
    print("Strict frozen candidate files:", strict["strict_file_count"])
    print("Source snapshots/checksum entries:", len(sources))
    print("Frozen evaluation seed: 42")
    print("Frozen evaluation: 19/19 cases, 262/262 assertions")
    print("Replay scopes: 10/10")
    print("Project 4 checkpoint identity: PASS")
    print("OpenAI/model-provider API runtime dependency: none")
    print("Production-ready claim: FALSE")
    print("External actions: 0")
    print("P6-04 reproducibility verification: PASS")

if __name__ == "__main__":
    main()
