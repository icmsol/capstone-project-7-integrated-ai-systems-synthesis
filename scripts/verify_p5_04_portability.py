#!/usr/bin/env python3
"""Verify the P5-04 configuration-portability comparison."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT / "outputs/evaluation/p5_04/portability/portability_comparison.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "config/schemas/portability_test_report.schema.json").read_text(encoding="utf-8"))


def main() -> None:
    Draft202012Validator(SCHEMA).validate(REPORT)
    comparisons = {item["opportunity_id"]: item for item in REPORT["comparisons"]}
    first = comparisons["OPP-E19200F7BD6C3161"]
    second = comparisons["OPP-P504-DATA-001"]
    if (first["icm_recommendation_code"], first["fictional_recommendation_code"]) != ("R-01", "R-04"):
        raise RuntimeError("ICM-oriented portability result changed.")
    if (second["icm_recommendation_code"], second["fictional_recommendation_code"]) != ("R-04", "R-01"):
        raise RuntimeError("Data-analytics portability result changed.")
    summary = REPORT["invariant_summary"]
    required_true = [
        "source_code_unchanged_between_profile_runs",
        "fixed_safeguards_unchanged",
        "schemas_unchanged",
        "alignment_changed_for_every_opportunity",
        "recommendation_changed_for_every_opportunity",
    ]
    if not all(summary[item] for item in required_true):
        raise RuntimeError("A portability invariant failed.")
    if summary["final_decisions_created"] != 0 or summary["external_actions_performed"] != 0:
        raise RuntimeError("Human-authority or external-action boundary failed.")
    print("Portability opportunities: 2")
    print("Profile runs: 4")
    print("ICM-oriented result: R-01 vs R-04")
    print("Data-analytics result: R-04 vs R-01")
    print("Source code, schemas, and fixed safeguards unchanged: PASS")
    print("P5-04 portability verification: PASS")


if __name__ == "__main__":
    main()
