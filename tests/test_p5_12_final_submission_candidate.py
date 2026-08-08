"""Regression tests for the P5-12 final submission candidate."""

from __future__ import annotations
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P12 = ROOT / "outputs/evaluation/p5_12"

class P512FinalSubmissionCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((P12 / "final_submission_candidate_manifest.json").read_text(encoding="utf-8"))
        cls.visual = json.loads((P12 / "final_visual_regression_acceptance.json").read_text(encoding="utf-8"))

    def test_candidate_is_explicitly_frozen(self):
        self.assertEqual(self.manifest["candidate_id"], "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0")
        self.assertEqual(self.manifest["candidate_status"], "frozen")

    def test_final_evaluation_is_fully_passing(self):
        e = self.manifest["evaluation"]
        self.assertEqual((e["cases_passed"], e["cases_total"]), (19, 19))
        self.assertEqual((e["assertions_passed"], e["assertions_total"]), (262, 262))
        self.assertEqual(e["regressions"], 0)
        self.assertFalse(e["frozen_inputs_changed"])

    def test_both_operator_acceptance_paths_are_preserved(self):
        a = self.manifest["operator_acceptance"]
        self.assertEqual(a["p5_10_same_rfo"]["status"], "PASS")
        self.assertEqual(a["p5_10_same_rfo"]["human_disposition_path"], "accept")
        self.assertEqual(a["p5_11_fresh_request"]["human_disposition_path"], "escalate")
        self.assertEqual(a["p5_11_fresh_request"]["bundle_round_trip"], "PASS")

    def test_visual_regression_passed(self):
        self.assertEqual(self.visual["visual_acceptance_result"], "PASS")
        self.assertTrue(all(check["status"] == "PASS" for check in self.visual["checks"]))

    def test_no_unresolved_critical_or_major_acceptance_defect(self):
        d = self.manifest["findings_disposition"]
        self.assertEqual(d["unresolved_critical_acceptance_defects"], 0)
        self.assertEqual(d["unresolved_major_acceptance_defects"], 0)

    def test_external_action_boundary(self):
        self.assertEqual(self.manifest["external_actions_performed"], 0)
        self.assertEqual(self.visual["recommendation"]["external_actions_performed"], 0)

    def test_phase_6_documentation_is_outside_technical_freeze(self):
        mutable = " ".join(self.manifest["freeze_scope"]["post_freeze_mutable_areas"])
        self.assertIn("README.md", mutable)
        self.assertIn("reports/", mutable)
        self.assertIn("presentation/", mutable)

if __name__ == "__main__":
    unittest.main(verbosity=2)
