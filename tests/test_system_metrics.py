"""Tests for the committed P5-02 system metrics."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_02"
        / "system_metrics.json"
    ).read_text(encoding="utf-8")
)
METRICS = {
    metric["metric_id"]: metric
    for metric in REPORT["metrics"]
}


class SystemMetricTests(unittest.TestCase):
    def pair(self, metric_id):
        metric = METRICS[metric_id]
        return metric["numerator"], metric["denominator"]

    def test_complete_population(self):
        self.assertEqual(REPORT["case_count"], 19)
        self.assertEqual(REPORT["assertion_count"], 262)

    def test_completion_and_conformance(self):
        self.assertEqual(self.pair("M-01"), (19, 19))
        self.assertEqual(self.pair("M-02"), (13, 19))
        self.assertEqual(self.pair("M-03"), (256, 262))
        self.assertEqual(self.pair("M-04"), (167, 167))

    def test_screening_terminal_and_route(self):
        self.assertEqual(self.pair("M-05"), (13, 13))
        self.assertEqual(self.pair("M-06"), (19, 19))
        self.assertEqual(self.pair("M-07"), (19, 19))

    def test_escalation_and_fail_closed_recall(self):
        self.assertEqual(self.pair("M-08"), (3, 3))
        self.assertEqual(self.pair("M-09"), (6, 6))

    def test_evidence_traceability_and_claim_controls(self):
        self.assertEqual(self.pair("M-10"), (5, 5))
        self.assertEqual(self.pair("M-11"), (19, 19))
        self.assertEqual(self.pair("M-12"), (19, 19))

    def test_diagnostics_preserve_mismatches(self):
        self.assertEqual(self.pair("M-13"), (15, 19))
        self.assertEqual(self.pair("M-14"), (17, 19))
        self.assertEqual(len(REPORT["failed_assertions"]), 6)

    def test_severity_summary(self):
        self.assertEqual(
            REPORT["severity_summary"]["critical"]["failed"],
            0,
        )
        self.assertEqual(
            REPORT["severity_summary"]["major"]["failed"],
            6,
        )

    def test_no_retroactive_thresholds(self):
        self.assertTrue(REPORT["no_retroactive_threshold_tuning"])
        self.assertEqual(REPORT["failure_analysis_deferred_to"], "P5-03")

    def test_external_action_boundary(self):
        self.assertEqual(REPORT["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
