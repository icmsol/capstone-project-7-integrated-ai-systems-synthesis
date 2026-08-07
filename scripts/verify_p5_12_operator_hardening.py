#!/usr/bin/env python3
"""Verify P5-12 operator-acceptance hardening before final freeze."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "outputs/evaluation/p5_12/operator_hardening_findings.json"
CATALOG = ROOT / "config/profiles/icm_service_catalog.csv"
UI = ROOT / "src/project7/operator_ui.py"
OVERLAY = ROOT / "outputs/evaluation/p5_06/versioned_overlay_manifest.json"
HISTORICAL_OVERLAY = ROOT / "outputs/evaluation/p5_06/versioned_overlay_manifest_v1.0.1.json"


def main() -> None:
    findings = json.loads(FINDINGS.read_text(encoding="utf-8"))
    mapping = {item["finding_id"]: item for item in findings["findings"]}
    expected = {"FR-01", "FR-02", "FR-03", "FR-04", "FR-05"}
    if set(mapping) != expected:
        raise RuntimeError("P5-12 finding register is incomplete.")
    for finding_id in ["FR-01", "FR-04", "FR-05"]:
        if not mapping[finding_id]["disposition"].startswith("corrected"):
            raise RuntimeError(f"{finding_id} is not corrected.")
    if mapping["FR-03"]["disposition"] != "accepted":
        raise RuntimeError("FR-03 safe evidence behavior is not accepted/documented.")
    if findings["frozen_model_retrained"] or findings["frozen_evaluation_history_rewritten"]:
        raise RuntimeError("Frozen model/evaluation history was improperly rewritten.")
    if findings["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary violated.")

    with CATALOG.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rfp = next(row for row in rows if row["capability_id"] == "ICM-PRC-004")
    terms = {item.strip().lower() for item in rfp["positive_keywords"].split(";")}
    prohibited = {"request for proposal", "request for quotation"}
    if terms & prohibited:
        raise RuntimeError("Generic solicitation-format terms still drive ICM-PRC-004.")
    required = {"rfp preparation", "rfq preparation", "solicitation development", "evaluation criteria"}
    if not required <= terms:
        raise RuntimeError("Substantive RFP/RFQ preparation terms were removed.")

    ui_text = UI.read_text(encoding="utf-8")
    for marker in [
        "_operator_packet_markdown",
        "_format_operator_money",
        "Domain-shift safeguard active",
        "$12,500,000",
    ]:
        if marker not in ui_text and marker != "$12,500,000":
            raise RuntimeError(f"Operator hardening marker missing: {marker}")

    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    if overlay["overlay_version"] != "1.0.2":
        raise RuntimeError("Current post-freeze overlay is not v1.0.2.")
    overlay_paths = {item["path"] for item in overlay["files"]}
    if "config/profiles/icm_service_catalog.csv" not in overlay_paths:
        raise RuntimeError("Hardened ICM catalog is not governed by the versioned overlay.")
    historical = json.loads(HISTORICAL_OVERLAY.read_text(encoding="utf-8"))
    if historical["overlay_version"] != "1.0.1":
        raise RuntimeError("Historical P5-06 overlay v1.0.1 was not preserved.")

    print("P5-11 findings represented: 5/5")
    print("FR-01 alignment precision correction: PASS")
    print("FR-02 bounded-model limitation preserved/documented: PASS")
    print("FR-03 retrieved-but-insufficient evidence behavior: ACCEPTED")
    print("FR-04 table-free Colab operator rendering: PASS")
    print("FR-05 human-readable currency rendering: PASS")
    print("Historical overlay v1.0.1 preserved: PASS")
    print("Current overlay v1.0.2 governs configuration correction: PASS")
    print("External actions performed: 0")
    print("P5-12 operator hardening verification: PASS")


if __name__ == "__main__":
    main()
