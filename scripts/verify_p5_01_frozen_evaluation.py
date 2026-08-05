#!/usr/bin/env python3
"""Verify a preserved P5-01 frozen evaluation run."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project7.frozen_evaluation import (  # noqa: E402
    read_json,
    sha256_file,
    validate_schema,
)


def main() -> None:
    manifest_path = (
        ROOT / "outputs" / "evaluation" / "p5_01"
        / "run_manifest.json"
    )
    manifest = read_json(manifest_path)
    validate_schema(
        manifest,
        "frozen_evaluation_run_manifest.schema.json",
        ROOT / "config" / "schemas",
    )

    for item in manifest["raw_output_inventory"]:
        path = ROOT / item["path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(
                f"Size mismatch: {item['path']}"
            )
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(
                f"Checksum mismatch: {item['path']}"
            )

    for item in manifest["case_result_index"]:
        result = read_json(ROOT / item["result_path"])
        validate_schema(
            result,
            "scenario_evaluation_result.schema.json",
            ROOT / "config" / "schemas",
        )

    print(
        f"Cases verified: "
        f"{manifest['case_count_executed']}"
    )
    print(
        f"Assertions verified: "
        f"{manifest['assertion_count_evaluated']}"
    )
    print(
        "Raw output integrity: PASS"
    )
    print(
        "Frozen evaluation verification: PASS"
    )


if __name__ == "__main__":
    main()
