"""Regression tests for the frozen P5-12 candidate plus P6-01 overlay."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P12 = ROOT / "outputs/evaluation/p5_12"
P6_01 = ROOT / "outputs/evaluation/p6_01"


class P512FinalSubmissionCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (P12 / "final_submission_candidate_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        cls.visual = json.loads(
            (P12 / "final_visual_regression_acceptance.json").read_text(
                encoding="utf-8"
            )
        )
        cls.p6_overlay = json.loads(
            (P6_01 / "post_freeze_overlay_manifest.json").read_text(
                encoding="utf-8"
            )
        )

    def test_candidate_is_explicitly_frozen(self):
        self.assertEqual(
            self.manifest["candidate_id"],
            "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0",
        )
        self.assertEqual(self.manifest["candidate_status"], "frozen")

    def test_final_evaluation_is_fully_passing(self):
        evaluation = self.manifest["evaluation"]
        self.assertEqual(evaluation["cases_passed"], 19)
        self.assertEqual(evaluation["cases_total"], 19)
        self.assertEqual(evaluation["assertions_passed"], 262)
        self.assertEqual(evaluation["assertions_total"], 262)
        self.assertEqual(evaluation["regressions"], 0)
        self.assertFalse(evaluation["frozen_inputs_changed"])

    def test_both_operator_acceptance_paths_are_preserved(self):
        acceptance = self.manifest["operator_acceptance"]
        self.assertEqual(acceptance["p5_10_same_rfo"]["status"], "PASS")
        self.assertEqual(
            acceptance["p5_10_same_rfo"]["human_disposition_path"], "accept"
        )
        self.assertEqual(
            acceptance["p5_11_fresh_request"]["human_disposition_path"], "escalate"
        )
        self.assertEqual(
            acceptance["p5_11_fresh_request"]["bundle_round_trip"], "PASS"
        )

    def test_visual_regression_passed(self):
        self.assertEqual(self.visual["visual_acceptance_result"], "PASS")
        self.assertTrue(
            all(check["status"] == "PASS" for check in self.visual["checks"])
        )

    def test_no_unresolved_critical_or_major_acceptance_defect(self):
        disposition = self.manifest["findings_disposition"]
        self.assertEqual(disposition["unresolved_critical_acceptance_defects"], 0)
        self.assertEqual(disposition["unresolved_major_acceptance_defects"], 0)

    def test_external_action_boundary(self):
        self.assertEqual(self.manifest["external_actions_performed"], 0)
        self.assertEqual(
            self.visual["recommendation"]["external_actions_performed"], 0
        )

    def test_phase_6_documentation_is_outside_technical_freeze(self):
        mutable = " ".join(
            self.manifest["freeze_scope"]["post_freeze_mutable_areas"]
        )
        self.assertIn("README.md", mutable)
        self.assertIn("reports/", mutable)
        self.assertIn("presentation/", mutable)

    def test_p6_01_overlay_is_explicit_and_bounded(self):
        self.assertEqual(
            self.p6_overlay["overlay_id"],
            "PROJECT7-P6-01-POST-FREEZE-OVERLAY-v1.0.0",
        )
        self.assertEqual(
            self.p6_overlay["parent_candidate_id"],
            "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0",
        )
        self.assertTrue(
            self.p6_overlay["documentation_only_and_ci_maintenance"]
        )
        self.assertFalse(
            self.p6_overlay["technical_or_evaluation_behavior_changed"]
        )
        self.assertFalse(self.p6_overlay["evaluation_results_changed"])
        self.assertEqual(self.p6_overlay["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
