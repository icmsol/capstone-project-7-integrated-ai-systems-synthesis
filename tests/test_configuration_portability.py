"""Tests for the P5-04 configuration-portability comparison."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = json.loads((ROOT / "outputs/evaluation/p5_04/portability/portability_comparison.json").read_text(encoding="utf-8"))


class ConfigurationPortabilityTests(unittest.TestCase):
    def test_two_opportunities_and_two_profiles(self):
        self.assertEqual(REPORT["opportunity_count"], 2)
        self.assertEqual(REPORT["profile_count"], 2)
        self.assertEqual(REPORT["run_count"], 4)

    def test_icm_oriented_opportunity_changes_result(self):
        item = next(row for row in REPORT["comparisons"] if row["opportunity_id"] == "OPP-E19200F7BD6C3161")
        self.assertEqual((item["icm_recommendation_code"], item["fictional_recommendation_code"]), ("R-01", "R-04"))

    def test_data_opportunity_changes_result_in_reverse(self):
        item = next(row for row in REPORT["comparisons"] if row["opportunity_id"] == "OPP-P504-DATA-001")
        self.assertEqual((item["icm_recommendation_code"], item["fictional_recommendation_code"]), ("R-04", "R-01"))

    def test_source_code_is_unchanged(self):
        self.assertTrue(REPORT["invariant_summary"]["source_code_unchanged_between_profile_runs"])

    def test_fixed_safeguards_and_schemas_are_unchanged(self):
        self.assertTrue(REPORT["invariant_summary"]["fixed_safeguards_unchanged"])
        self.assertTrue(REPORT["invariant_summary"]["schemas_unchanged"])

    def test_all_runs_preserve_human_authority(self):
        for run in REPORT["profile_runs"]:
            self.assertIsNone(run["screening_recommendation"]["final_decision"])
            self.assertTrue(run["invariants"]["human_final_decision_required"])
            self.assertTrue(run["invariants"]["autonomous_external_actions_prohibited"])

    def test_profile_switch_changes_alignment_and_recommendation(self):
        for item in REPORT["comparisons"]:
            self.assertTrue(item["alignment_changed"])
            self.assertTrue(item["recommendation_changed"])

    def test_external_action_boundary(self):
        self.assertEqual(REPORT["invariant_summary"]["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
