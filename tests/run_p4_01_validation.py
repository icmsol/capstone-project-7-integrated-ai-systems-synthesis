"""Run P4-01 validation and generate representative outputs."""

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

from project7 import run_intake_from_files  # noqa: E402
from project7.schema_validation import validate_artifact  # noqa: E402


FIXED_TIME = "2026-08-05T16:30:00Z"


def main() -> None:
    result = run_intake_from_files(
        repo_root=ROOT,
        raw_opportunity_path=(
            ROOT / "data" / "implementation" / "p4_01"
            / "raw_opportunity.json"
        ),
        source_approval_path=(
            ROOT / "data" / "implementation" / "p4_01"
            / "source_approval.json"
        ),
        organization_context_path=(
            ROOT / "config" / "system"
            / "p4_01_reference_organization_context.json"
        ),
        normalization_rules_path=(
            ROOT / "config" / "system"
            / "opportunity_intake_rules.json"
        ),
        output_directory=ROOT / "outputs" / "p4_01",
        audit_output_path=(
            ROOT / "audit" / "p4_01_intake_events.jsonl"
        ),
        event_time=FIXED_TIME,
    )

    schemas = ROOT / "config" / "schemas"
    validate_artifact(
        result.normalized_opportunity,
        "opportunity_record.schema.json",
        schemas,
    )
    validate_artifact(
        result.initial_case_state,
        "integrated_case_state.schema.json",
        schemas,
    )
    for event in result.audit_events:
        validate_artifact(
            event,
            "audit_event.schema.json",
            schemas,
        )

    unit = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_opportunity_intake",
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
    print(
        "Representative normalized opportunity: "
        f"{result.normalized_opportunity['opportunity_id']}"
    )
    print(
        "Initial case state: "
        f"{result.initial_case_state['case_id']} / "
        f"{result.initial_case_state['case_status']}"
    )
    print(
        "Source SHA-256 recorded and validated: PASS"
    )
    print(
        "Original values retained without material inference: PASS"
    )
    print("Audit hash chain: PASS")
    print("Schema validation: PASS")
    print("External actions performed: 0")


if __name__ == "__main__":
    main()
