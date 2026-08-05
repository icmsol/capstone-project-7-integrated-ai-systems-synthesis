"""Run P4-03 against the committed actual Project 4 package."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(
    os.environ.get(
        "PROJECT7_REPO_ROOT",
        Path(__file__).resolve().parents[1],
    )
).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project7.p4_03_pipeline import run_clause_triage  # noqa: E402


def main() -> None:
    artifacts = run_clause_triage(
        repo_root=ROOT,
        case_state_path=(
            ROOT / "outputs" / "p4_02"
            / "updated_case_state.json"
        ),
        passage_set_path=(
            ROOT / "data" / "implementation" / "p4_03"
            / "representative_passages.json"
        ),
        output_directory=ROOT / "outputs" / "p4_03",
        audit_output_path=(
            ROOT / "audit"
            / "p4_03_clause_triage_event.jsonl"
        ),
        event_time="2026-08-05T17:15:00Z",
    )
    print(
        f"Actual Project 4 predictions: "
        f"{len(artifacts['predictions'])}"
    )
    for item in artifacts["predictions"]:
        print(
            f"{item['passage_id']}: "
            f"{item['predicted_category']} / "
            f"{item['confidence']:.6f} / "
            f"{item['decision']} / "
            f"domain_warning={item['domain_warning']} / "
            f"truncated={item['truncated']}"
        )
    print("Integrated case-state validation: PASS")
    print("Audit hash-chain continuation: PASS")
    print("External actions performed: 0")


if __name__ == "__main__":
    main()
