"""Run the P5-04 configuration-portability comparison."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT7_REPO_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project7.configuration_portability import run_portability_comparison  # noqa: E402


def main() -> None:
    output = ROOT / "outputs/evaluation/p5_04/portability"
    report = run_portability_comparison(
        repo_root=ROOT,
        opportunities_path=ROOT / "data/implementation/p5_04/portability_opportunities.json",
        output_directory=output,
        audit_output_path=ROOT / "audit/p5_04_portability_ledger.jsonl",
    )
    with (output / "portability_comparison.csv").open("w", encoding="utf-8", newline="") as file_obj:
        rows = report["comparisons"]
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    summary = report["invariant_summary"]
    if not all([
        summary["source_code_unchanged_between_profile_runs"],
        summary["fixed_safeguards_unchanged"],
        summary["schemas_unchanged"],
        summary["alignment_changed_for_every_opportunity"],
        summary["recommendation_changed_for_every_opportunity"],
        summary["final_decisions_created"] == 0,
        summary["external_actions_performed"] == 0,
    ]):
        raise RuntimeError("Portability acceptance criteria failed.")
    print(f"Opportunities compared: {report['opportunity_count']}")
    print(f"Profiles compared: {report['profile_count']}")
    print(f"Profile runs: {report['run_count']}")
    for item in report["comparisons"]:
        print(f"{item['opportunity_id']}: ICM={item['icm_recommendation_code']} / Fictional={item['fictional_recommendation_code']}")
    print("Source code unchanged: True")
    print("Fixed safeguards unchanged: True")
    print("Schemas unchanged: True")
    print("External actions performed: 0")
    print("P5-04 configuration portability: PASS")


if __name__ == "__main__":
    main()
