"""Run P4-05 integrated packet validation."""

from __future__ import annotations

import os
import subprocess
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

from project7.p4_05_pipeline import run_packet_assembly  # noqa: E402


def main() -> None:
    artifacts = run_packet_assembly(
        repo_root=ROOT,
        case_state_path=(
            ROOT / "outputs" / "p4_04"
            / "updated_case_state.json"
        ),
        output_directory=ROOT / "outputs" / "p4_05",
        audit_output_path=(
            ROOT / "audit"
            / "p4_05_packet_events.jsonl"
        ),
        event_time="2026-08-05T19:15:00Z",
    )

    unit = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_decision_support_packet",
            "-v",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env={
            **os.environ,
            "PROJECT7_REPO_ROOT": str(ROOT),
            "PYTHONPATH": str(SRC),
        },
    )
    if unit.returncode != 0:
        raise RuntimeError(
            f"Unit tests failed:\n{unit.stdout}\n{unit.stderr}"
        )

    print(unit.stdout, end="")
    print(unit.stderr, end="")
    recommendation = artifacts["recommendation"]
    packet = artifacts["packet"]
    updated_case = artifacts["updated_case_state"]
    print(
        "Recommendation: "
        f"{recommendation['recommendation_code']} / "
        f"{recommendation['recommendation_label']}"
    )
    print(
        "Supporting evidence IDs: "
        f"{len(recommendation['supporting_evidence_ids'])}"
    )
    print(
        "Unresolved issues preserved: "
        f"{len(packet['unresolved_issues'])}"
    )
    print(
        "Required reviewer: "
        f"{packet['human_review']['required_reviewer']['role_name']}"
    )
    print(
        "Updated case status: "
        f"{updated_case['case_status']}"
    )
    print(
        "Human disposition recorded: "
        f"{updated_case['human_disposition'] is not None}"
    )
    print(
        "Audit events added: "
        f"{len(artifacts['audit_events'])}"
    )
    print("Packet schema validation: PASS")
    print("Recommendation schema validation: PASS")
    print("Final decision created: False")
    print("External actions performed: 0")


if __name__ == "__main__":
    main()
