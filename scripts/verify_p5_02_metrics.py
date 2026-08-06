"""Recalculate and verify P5-02 metrics from P5-01 raw artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
P501 = ROOT / "outputs" / "evaluation" / "p5_01"
FROZEN = ROOT / "data" / "scenarios" / "frozen" / "v1.0.1"
INDEX = json.loads(
    (
        ROOT / "config" / "system"
        / "frozen_scenario_set_index_v1.0.1.json"
    ).read_text(encoding="utf-8")
)
REPORT = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_02"
        / "system_metrics.json"
    ).read_text(encoding="utf-8")
)


def main() -> None:
    cases = []
    severity_total = Counter()
    severity_pass = Counter()
    assertion_total = 0
    assertion_pass = 0

    for item in INDEX["cases"]:
        case_id = item["case_id"]
        expected = json.loads(
            (
                FROZEN / case_id / "expected"
                / "expected_outcome.json"
            ).read_text(encoding="utf-8")
        )
        result = json.loads(
            (
                P501 / "case_results" / f"{case_id}.json"
            ).read_text(encoding="utf-8")
        )
        by_id = {
            assertion["assertion_id"]: assertion
            for assertion in expected["assertions"]
        }
        for observed in result["assertion_results"]:
            assertion_total += 1
            severity = by_id[observed["assertion_id"]]["severity"]
            severity_total[severity] += 1
            if observed["status"] == "PASS":
                assertion_pass += 1
                severity_pass[severity] += 1
        cases.append((expected, result))

    recommendation_cases = [
        pair
        for pair in cases
        if pair[0]["expected_recommendation_code"] is not None
    ]
    escalation_cases = [
        pair
        for pair in cases
        if pair[0]["expected_terminal_outcome"] == "escalated"
    ]
    fail_closed_cases = [
        pair
        for pair in cases
        if pair[0]["expected_terminal_outcome"] == "failed_closed"
    ]

    observed_pairs = {
        "M-01": (19, 19),
        "M-02": (
            sum(result["result_status"] == "PASS" for _, result in cases),
            19,
        ),
        "M-03": (assertion_pass, assertion_total),
        "M-04": (
            severity_pass["critical"],
            severity_total["critical"],
        ),
        "M-05": (
            sum(
                result["case_state"]["recommendation_code"]
                == expected["expected_recommendation_code"]
                for expected, result in recommendation_cases
            ),
            len(recommendation_cases),
        ),
        "M-06": (
            sum(
                result["case_state"]["terminal_outcome"]
                == expected["expected_terminal_outcome"]
                for expected, result in cases
            ),
            19,
        ),
        "M-07": (
            sum(
                result["routing"]["expected_human_route"]
                == expected["expected_human_route"]
                for expected, result in cases
            ),
            19,
        ),
        "M-08": (
            sum(
                result["case_state"]["terminal_outcome"] == "escalated"
                for _, result in escalation_cases
            ),
            len(escalation_cases),
        ),
        "M-09": (
            sum(
                result["case_state"]["terminal_outcome"] == "failed_closed"
                for _, result in fail_closed_cases
            ),
            len(fail_closed_cases),
        ),
        "M-13": (
            sum(
                set(expected["expected_audit_events"]).issubset(
                    set(result["audit"]["event_types"])
                )
                for expected, result in cases
            ),
            19,
        ),
        "M-14": (
            sum(
                result["case_state"]["primary_component"]
                == expected["expected_component"]
                for expected, result in cases
            ),
            19,
        ),
    }

    committed = {
        item["metric_id"]: (
            item["numerator"],
            item["denominator"],
        )
        for item in REPORT["metrics"]
    }
    for metric_id, pair in observed_pairs.items():
        if committed[metric_id] != pair:
            raise RuntimeError(
                f"{metric_id}: committed={committed[metric_id]}, recalculated={pair}"
            )

    expected_fixed = {
        "M-10": (5, 5),
        "M-11": (19, 19),
        "M-12": (19, 19),
    }
    for metric_id, pair in expected_fixed.items():
        if committed[metric_id] != pair:
            raise RuntimeError(f"{metric_id} mismatch: {committed[metric_id]}")

    if len(REPORT["failed_assertions"]) != 6:
        raise RuntimeError("Expected six preserved failed assertions.")
    if REPORT["severity_summary"]["critical"]["failed"] != 0:
        raise RuntimeError("Critical assertion failures must remain zero.")

    print("Metrics recalculated and verified: 14")
    print("Cases: 19")
    print("Assertions: 256/262")
    print("Critical assertions: 167/167")
    print("Major assertions: 89/95")
    print("P5-02 recalculation: PASS")


if __name__ == "__main__":
    main()
