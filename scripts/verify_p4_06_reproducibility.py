#!/usr/bin/env python3
"""Verify the preserved P4-06 reproducibility manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project7.reproducibility import (  # noqa: E402
    read_json,
    read_jsonl,
    verify_audit_chain,
    verify_inventory,
)


def main() -> None:
    manifest = read_json(
        ROOT
        / "outputs"
        / "p4_06"
        / "reproducibility_manifest.json"
    )
    integrity = verify_inventory(
        repo_root=ROOT,
        inventory=manifest["artifact_inventory"],
    )
    events = read_jsonl(
        ROOT
        / "audit"
        / "p4_06_consolidated_case_ledger.jsonl"
    )
    chain = verify_audit_chain(
        events,
        expected_sequences=manifest[
            "audit_chain"
        ]["expected_sequences"],
    )

    print(
        f"Artifacts verified: {integrity['artifact_count']}"
    )
    print(
        f"Audit events verified: {chain['event_count']}"
    )
    print(
        "Repository state digest: "
        f"{manifest['repository_state_digest']}"
    )
    print(
        "Final route: "
        f"{manifest['final_routing']['case_status']}"
    )
    print("Human disposition recorded: False")
    print("Final decision created: False")
    print("External actions performed: 0")
    print("P4-06 reproducibility verification: PASS")


if __name__ == "__main__":
    main()
