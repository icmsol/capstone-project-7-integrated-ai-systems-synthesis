"""Regression tests for the frozen P5-12 candidate plus Phase 6 documentation overlays."""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P12 = ROOT / "outputs/evaluation/p5_12"

class FinalCandidatePhase6OverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((P12 / "final_submission_candidate_manifest.json").read_text(encoding="utf-8"))
        cls.visual = json.loads((P12 / "final_visual_regression_acceptance.json").read_text(encoding="utf-8"))
        cls.p6_01 = json.loads((ROOT / "outputs/evaluation/p6_01/post_freeze_overlay_manifest.json").read_text(encoding="utf-8"))
        cls.p6_02 = json.loads((ROOT / "outputs/evaluation/p6_02/post_freeze_documentation_overlay_manifest.json").read_text(encoding="utf-8"))

    def test_candidate_identity(self):
        self.assertEqual(self.manifest["candidate_id"], "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0")
        self.assertEqual(self.manifest["candidate_status"], "frozen")

    def test_evaluation(self):
        e = self.manifest["evaluation"]
        self.assertEqual((e["cases_passed"], e["cases_total"]), (19, 19))
        self.assertEqual((e["assertions_passed"], e["assertions_total"]), (262, 262))
        self.assertEqual(e["regressions"], 0)
        self.assertFalse(e["frozen_inputs_changed"])

    def test_operator_acceptance(self):
        a = self.manifest["operator_acceptance"]
        self.assertEqual(a["p5_10_same_rfo"]["status"], "PASS")
        self.assertEqual(a["p5_11_fresh_request"]["human_disposition_path"], "escalate")
        self.assertEqual(a["p5_11_fresh_request"]["bundle_round_trip"], "PASS")

    def test_visual_regression(self):
        self.assertEqual(self.visual["visual_acceptance_result"], "PASS")
        self.assertTrue(all(x["status"] == "PASS" for x in self.visual["checks"]))

    def test_no_unresolved_major_or_critical_defects(self):
        d = self.manifest["findings_disposition"]
        self.assertEqual(d["unresolved_critical_acceptance_defects"], 0)
        self.assertEqual(d["unresolved_major_acceptance_defects"], 0)

    def test_external_action_boundary(self):
        self.assertEqual(self.manifest["external_actions_performed"], 0)

    def test_p6_01_overlay(self):
        self.assertTrue(self.p6_01["documentation_only_and_ci_maintenance"])
        self.assertFalse(self.p6_01["technical_or_evaluation_behavior_changed"])

    def test_p6_02_overlay(self):
        self.assertEqual(self.p6_02["overlay_id"], "PROJECT7-P6-02-POST-FREEZE-DOCUMENTATION-OVERLAY-v1.0.0")
        self.assertEqual(self.p6_02["parent_candidate_id"], "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0")
        self.assertTrue(self.p6_02["documentation_only_and_ci_maintenance"])
        self.assertFalse(self.p6_02["technical_or_evaluation_behavior_changed"])
        self.assertFalse(self.p6_02["evaluation_results_changed"])
        self.assertEqual(self.p6_02["external_actions_performed"], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
