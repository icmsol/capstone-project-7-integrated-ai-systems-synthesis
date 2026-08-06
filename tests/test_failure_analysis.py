"""Tests for the P5-03 failure analysis."""

from __future__ import annotations

import csv
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_03"
        / "failure_analysis_report.json"
    ).read_text(encoding="utf-8")
)


class FailureAnalysisTests(unittest.TestCase):
    def test_all_six_failures_are_mapped_once(self):
        pairs = [
            (item["case_id"], item["assertion_id"])
            for item in REPORT["occurrences"]
        ]
        self.assertEqual(len(pairs), 6)
        self.assertEqual(len(set(pairs)), 6)

    def test_three_classes_each_have_two_occurrences(self):
        counts = Counter(
            item["failure_class_id"]
            for item in REPORT["occurrences"]
        )
        self.assertEqual(
            counts,
            Counter({"FC-01": 2, "FC-02": 2, "FC-03": 2}),
        )

    def test_no_safety_significant_failure(self):
        self.assertEqual(REPORT["critical_assertion_failures"], 0)
        self.assertEqual(REPORT["safety_significant_failure_count"], 0)
        self.assertFalse(
            any(
                item["critical_safety_failure"]
                for item in REPORT["occurrences"]
            )
        )

    def test_every_occurrence_preserves_correct_core_behavior(self):
        for item in REPORT["occurrences"]:
            self.assertTrue(item["terminal_outcome_match"])
            self.assertTrue(item["recommendation_match"])
            self.assertTrue(item["human_route_match"])
            self.assertTrue(item["traceability_complete"])
            self.assertTrue(item["unsupported_claims_prevented"])

    def test_occurrences_have_cause_impact_and_evidence(self):
        for item in REPORT["occurrences"]:
            self.assertTrue(item["root_cause_detail"])
            self.assertTrue(item["impact"])
            self.assertGreaterEqual(len(item["evidence_paths"]), 4)

    def test_backlog_prohibits_frozen_changes(self):
        self.assertEqual(len(REPORT["refinement_backlog"]), 5)
        for item in REPORT["refinement_backlog"]:
            self.assertIn("frozen cases", item["prohibited_changes"])
            self.assertTrue(item["acceptance_criteria"])

    def test_full_regression_is_required(self):
        regression = next(
            item
            for item in REPORT["refinement_backlog"]
            if item["refinement_id"] == "RB-05"
        )
        self.assertIn(
            "19 of 19 cases execute",
            regression["acceptance_criteria"],
        )
        self.assertIn(
            "262 of 262 assertions pass",
            regression["acceptance_criteria"],
        )

    def test_failure_mode_coverage_is_complete(self):
        modes = {
            item["failure_mode"]
            for item in REPORT["failure_mode_coverage"]
        }
        self.assertIn(
            "Ambiguous or sparse opportunity data",
            modes,
        )
        self.assertIn(
            "Model confidence, domain shift, truncation, or package integrity",
            modes,
        )
        self.assertIn(
            "Citation, source freshness, conflict, sufficiency, or corpus governance",
            modes,
        )
        self.assertIn("Over-escalation", modes)

    def test_no_over_escalation(self):
        self.assertEqual(
            REPORT["over_escalation"]["unexpected_escalations"],
            0,
        )

    def test_external_action_boundary(self):
        self.assertEqual(REPORT["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
