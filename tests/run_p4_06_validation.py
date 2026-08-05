"""Run P4-06 audit and reproducibility validation."""

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

from project7.p4_06_pipeline import (  # noqa: E402
    run_reproducibility_pipeline,
)


def main() -> None:
    artifacts = run_reproducibility_pipeline(
        repo_root=ROOT,
        output_directory=ROOT / "outputs" / "p4_06",
        audit_output_directory=ROOT / "audit",
        policy_path=(
            ROOT
            / "config"
            / "system"
            / "reproducibility_policy.json"
        ),
        event_time="2026-08-05T20:00:00Z",
    )

    unit = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_reproducibility",
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
    manifest = artifacts["manifest"]
    print(
        f"Inventoried artifacts: "
        f"{manifest['artifact_count']}"
    )
    print(
        f"Consolidated audit events: "
        f"{manifest['audit_chain']['event_count']}"
    )
    print(
        "Audit event range: "
        f"{manifest['audit_chain']['first_event_id']} "
        f"through {manifest['audit_chain']['last_event_id']}"
    )
    print(
        "Repository state digest: "
        f"{manifest['repository_state_digest']}"
    )
    print("Artifact integrity: PASS")
    print("Audit-chain integrity: PASS")
    print("Deterministic packet replay: PASS")
    print(
        "Final route: "
        f"{manifest['final_routing']['case_status']}"
    )
    print("Human disposition recorded: False")
    print("Final decision created: False")
    print("External actions performed: 0")


if __name__ == "__main__":
    main()
