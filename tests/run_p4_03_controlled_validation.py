"""Run controlled P4-03 implementation validation."""

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

from project7 import build_clause_prediction  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    policy = load_json(
        ROOT / "config" / "system"
        / "clause_triage_policy.json"
    )
    registry = load_json(
        ROOT / "tests" / "fixtures" / "p4_03"
        / "synthetic_model_registry.json"
    )
    fixtures = load_json(
        ROOT / "tests" / "fixtures" / "p4_03"
        / "controlled_probability_fixtures.json"
    )
    schema_dir = ROOT / "config" / "schemas"

    predictions = []
    for name, result in fixtures.items():
        predictions.append(
            build_clause_prediction(
                case_id="CASE-P4-03-CONTROLLED",
                passage_id=f"PASSAGE-{name.upper()}",
                probability_result=result,
                model_artifact_id=(
                    "P4-03-SYNTHETIC-COMPATIBILITY-MODEL"
                ),
                model_version="0.0.1",
                model_sha256=registry["checkpoint_sha256"],
                policy=policy,
                source_domain=(
                    "public_sector"
                    if name == "truncated"
                    else "commercial_contract"
                ),
                consequential_use=(name == "truncated"),
                schema_dir=schema_dir,
            )
        )

    output_dir = ROOT / "outputs" / "p4_03"
    output_dir.mkdir(parents=True, exist_ok=True)
    (
        output_dir
        / "controlled_clause_predictions.json"
    ).write_text(
        json.dumps(
            {
                "validation_mode": (
                    "synthetic_compatible_model_and_controlled_probabilities"
                ),
                "measured_actual_model_result": False,
                "predictions": predictions,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "tests.test_clause_triage",
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
    if result.returncode != 0:
        raise RuntimeError(
            f"Unit tests failed:\n{result.stdout}\n{result.stderr}"
        )

    print(result.stdout, end="")
    print(result.stderr, end="")
    print("Controlled predictions: 3")
    print("Compatible model package load: PASS")
    print("Confidence abstention: PASS")
    print("Public-sector escalation: PASS")
    print("Truncation disclosure: PASS")
    print("Schema validation: PASS")
    print("External actions performed: 0")
    print("Actual Project 4 P4-03 wrapper run: PENDING COLAB CPU")


if __name__ == "__main__":
    main()
