"""Run the Project 7 frozen v1.0.1 evaluation suite."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
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

from project7.frozen_evaluation import (  # noqa: E402
    execute_case,
    read_json,
    sha256_file,
    validate_schema,
)


def canonical_bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def chained_event(
    *,
    sequence,
    event_type,
    run_id,
    case_id,
    status,
    details,
    previous_hash,
):
    event = {
        "sequence": sequence,
        "event_type": event_type,
        "run_id": run_id,
        "case_id": case_id,
        "status": status,
        "details": details,
        "previous_event_hash": previous_hash,
    }
    event["event_hash"] = hashlib.sha256(
        canonical_bytes(event)
    ).hexdigest()
    return event


def main() -> None:
    started = datetime.now(timezone.utc)
    run_id = (
        "P5-01-"
        + started.strftime("%Y%m%dT%H%M%SZ")
    )
    timer = time.perf_counter()

    index = read_json(
        ROOT / "config" / "system"
        / "frozen_scenario_set_index_v1.0.1.json"
    )
    output_root = (
        ROOT / "outputs" / "evaluation" / "p5_01"
    )
    result_dir = output_root / "case_results"
    trace_dir = output_root / "case_traces"
    audit_dir = ROOT / "audit"
    for directory in [
        result_dir,
        trace_dir,
        audit_dir,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

    run_events = []
    previous_hash = None
    event = chained_event(
        sequence=1,
        event_type="frozen_evaluation_started",
        run_id=run_id,
        case_id=None,
        status="started",
        details={
            "freeze_version": index["freeze_version"],
            "case_count_expected": index["case_count"],
            "post_run_changes_permitted": False,
        },
        previous_hash=previous_hash,
    )
    run_events.append(event)
    previous_hash = event["event_hash"]

    case_rows = []
    total_assertions = 0
    for item in index["cases"]:
        case_id = item["case_id"]
        case_dir = (
            ROOT
            / "data"
            / "scenarios"
            / "frozen"
            / "v1.0.1"
            / case_id
        )
        case_started = datetime.now(timezone.utc)
        result, trace, summary = execute_case(
            repo_root=ROOT,
            case_dir=case_dir,
            started_at=case_started,
        )

        result_path = (
            result_dir / f"{case_id}.json"
        )
        trace_path = (
            trace_dir / f"{case_id}.jsonl"
        )
        result_path.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        trace_path.write_text(
            "".join(
                json.dumps(
                    {
                        "run_id": run_id,
                        "case_id": case_id,
                        **entry,
                    },
                    ensure_ascii=False,
                )
                + "\n"
                for entry in trace
            ),
            encoding="utf-8",
        )
        total_assertions += summary[
            "assertions_evaluated"
        ]
        row = {
            **summary,
            "result_path": result_path.relative_to(
                ROOT
            ).as_posix(),
            "trace_path": trace_path.relative_to(
                ROOT
            ).as_posix(),
            "result_sha256": sha256_file(result_path),
            "trace_sha256": sha256_file(trace_path),
        }
        case_rows.append(row)

        event = chained_event(
            sequence=len(run_events) + 1,
            event_type="frozen_case_completed",
            run_id=run_id,
            case_id=case_id,
            status=result["result_status"],
            details={
                "assertions_evaluated": summary[
                    "assertions_evaluated"
                ],
                "assertions_failed": summary[
                    "assertions_failed"
                ],
                "critical_failures": summary[
                    "critical_failures"
                ],
                "major_failures": summary[
                    "major_failures"
                ],
                "external_actions_performed": 0,
            },
            previous_hash=previous_hash,
        )
        run_events.append(event)
        previous_hash = event["event_hash"]

    expected_case_ids = [
        item["case_id"] for item in index["cases"]
    ]
    observed_case_ids = [
        item["case_id"] for item in case_rows
    ]
    missing = sorted(
        set(expected_case_ids)
        - set(observed_case_ids)
    )
    status_counts = Counter(
        item["result_status"] for item in case_rows
    )

    event = chained_event(
        sequence=len(run_events) + 1,
        event_type="frozen_evaluation_completed",
        run_id=run_id,
        case_id=None,
        status=(
            "PASS"
            if not missing
            and total_assertions == 262
            else "FAIL"
        ),
        details={
            "case_count_executed": len(case_rows),
            "missing_case_count": len(missing),
            "assertion_count_evaluated": total_assertions,
            "status_counts": {
                "PASS": status_counts.get("PASS", 0),
                "PARTIAL": status_counts.get(
                    "PARTIAL",
                    0,
                ),
                "FAIL": status_counts.get("FAIL", 0),
            },
            "post_run_changes_applied": False,
            "external_actions_performed": 0,
        },
        previous_hash=previous_hash,
    )
    run_events.append(event)

    ledger_path = (
        audit_dir
        / "p5_01_frozen_evaluation_ledger.jsonl"
    )
    ledger_path.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False)
            + "\n"
            for item in run_events
        ),
        encoding="utf-8",
    )

    index_json_path = output_root / "case_run_index.json"
    index_csv_path = output_root / "case_run_index.csv"
    index_json_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "freeze_version": "1.0.1",
                "case_count": len(case_rows),
                "cases": case_rows,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with index_csv_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=list(case_rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(case_rows)

    raw_files = sorted(
        [
            *result_dir.glob("*.json"),
            *trace_dir.glob("*.jsonl"),
            index_json_path,
            index_csv_path,
            ledger_path,
        ]
    )
    completed = datetime.now(timezone.utc)
    freeze_lock_path = (
        ROOT / "config" / "system"
        / "p5_01_freeze_lock.json"
    )
    manifest = {
        "run_schema_version": "1.0.0",
        "run_id": run_id,
        "freeze_version": "1.0.1",
        "evaluation_policy_version": "1.0.0",
        "started_at": started.isoformat().replace(
            "+00:00",
            "Z",
        ),
        "completed_at": completed.isoformat().replace(
            "+00:00",
            "Z",
        ),
        "elapsed_seconds": round(
            time.perf_counter() - timer,
            6,
        ),
        "case_count_expected": 19,
        "case_count_executed": len(case_rows),
        "missing_case_ids": missing,
        "assertion_count_expected": 262,
        "assertion_count_evaluated": total_assertions,
        "status_counts": {
            "PASS": status_counts.get("PASS", 0),
            "PARTIAL": status_counts.get(
                "PARTIAL",
                0,
            ),
            "FAIL": status_counts.get("FAIL", 0),
        },
        "case_result_index": case_rows,
        "freeze_lock_sha256": sha256_file(
            freeze_lock_path
        ),
        "raw_output_inventory": [
            {
                "path": path.relative_to(
                    ROOT
                ).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in raw_files
        ],
        "post_run_changes_applied": False,
        "external_actions_performed": 0,
        "production_boundary": (
            "Controlled capstone prototype; nonbinding recommendations only; "
            "no autonomous external action; final human authority required."
        ),
    }
    manifest_path = output_root / "run_manifest.json"
    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    validate_schema(
        manifest,
        "frozen_evaluation_run_manifest.schema.json",
        ROOT / "config" / "schemas",
    )

    print(f"Run ID: {run_id}")
    print(
        f"Frozen cases executed: "
        f"{len(case_rows)}/19"
    )
    print(
        f"Assertions evaluated: "
        f"{total_assertions}/262"
    )
    print(
        "Case statuses: "
        f"PASS={status_counts.get('PASS', 0)}, "
        f"PARTIAL={status_counts.get('PARTIAL', 0)}, "
        f"FAIL={status_counts.get('FAIL', 0)}"
    )
    print(
        f"Missing cases: {len(missing)}"
    )
    print(
        "Post-run changes applied: False"
    )
    print(
        "External actions performed: 0"
    )
    print(
        f"Raw result files: "
        f"{len(list(result_dir.glob('*.json')))}"
    )
    print(
        f"Raw trace files: "
        f"{len(list(trace_dir.glob('*.jsonl')))}"
    )
    print(
        "P5-01 frozen evaluation run: PASS"
    )


if __name__ == "__main__":
    main()
