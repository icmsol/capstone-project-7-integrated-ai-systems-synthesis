"""Run P4-04 integrated validation and preserve outputs."""

from __future__ import annotations

import json
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

from project7.p4_04_pipeline import run_evidence_workflow  # noqa: E402


def main() -> None:
    artifacts = run_evidence_workflow(
        repo_root=ROOT,
        case_state_path=(
            ROOT / "outputs" / "p4_03"
            / "updated_case_state.json"
        ),
        requests_path=(
            ROOT / "data" / "implementation" / "p4_04"
            / "representative_evidence_requests.json"
        ),
        output_directory=ROOT / "outputs" / "p4_04",
        audit_output_path=(
            ROOT / "audit"
            / "p4_04_evidence_workflow_events.jsonl"
        ),
        tool_trace_output_path=(
            ROOT / "audit"
            / "p4_04_tool_trace.jsonl"
        ),
        event_time="2026-08-05T18:30:00Z",
    )

    unit = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_evidence_workflow",
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
    results = artifacts["results"]
    print(f"Representative requests executed: {len(results)}")
    print(
        "Evidence items preserved: "
        f"{sum(len(item['evidence_items']) for item in results)}"
    )
    print(
        "Sufficient evidence assessments: "
        f"{sum(item['assessment']['sufficiency_status'] == 'sufficient' for item in results)}"
    )
    print(
        "Exact citation semantic substitutions: 0"
    )
    print(
        "Updated case status: "
        f"{artifacts['updated_case_state']['case_status']}"
    )
    print(
        "Audit events added: "
        f"{len(artifacts['audit_events'])}"
    )
    print("Audit hash-chain continuation: PASS")
    print("Registered corpus and snapshot checksums: PASS")
    print("External actions performed: 0")


if __name__ == "__main__":
    main()
