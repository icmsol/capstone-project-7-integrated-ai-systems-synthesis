#!/usr/bin/env python3
"""Generate non-secret metadata for the current GitHub Actions run."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "ci" / "hosted-run-metadata.json"


def main() -> None:
    payload = {
        "metadata_schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "workflow": os.environ.get("GITHUB_WORKFLOW", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "local"),
        "event_name": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "ref": os.environ.get("GITHUB_REF", "local"),
        "sha": os.environ.get("GITHUB_SHA", "local"),
        "actor": os.environ.get("GITHUB_ACTOR", "local"),
        "runner_os": os.environ.get("RUNNER_OS", "local"),
        "external_actions_performed": 0,
        "contains_secrets": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Hosted run metadata written: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
