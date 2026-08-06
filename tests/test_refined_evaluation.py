"""Regression tests for the P5-04 refined frozen-suite run."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "outputs/evaluation/p5_04/refined_run_manifest.json").read_text(encoding="utf-8"))
COMPARISON = json.loads((ROOT / "outputs/evaluation/p5_04/before_after_metrics.json").read_text(encoding="utf-8"))


class RefinedEvaluationTests(unittest.TestCase):
    def test_all_cases_and_assertions_pass(self):
        self.assertEqual(MANIFEST["case_count_executed"], 19)
        self.assertEqual(MANIFEST["assertion_count_passed"], 262)
        self.assertEqual(MANIFEST["status_counts"], {"PASS": 19, "PARTIAL": 0, "FAIL": 0})

    def test_exact_six_cases_improved(self):
        self.assertEqual(
            set(MANIFEST["improved_case_ids"]),
            {"TC-03", "TC-05", "TC-10", "TC-14", "TC-15", "TC-18"},
        )

    def test_no_regressions(self):
        self.assertEqual(MANIFEST["regression_case_ids"], [])

    def test_frozen_inputs_unchanged(self):
        self.assertFalse(MANIFEST["frozen_inputs_changed"])
        self.assertFalse(COMPARISON["frozen_inputs_changed"])

    def test_audit_event_classification_improved(self):
        self.assertEqual(COMPARISON["before"]["audit_event_classification"], {"numerator": 15, "denominator": 19})
        self.assertEqual(COMPARISON["after"]["audit_event_classification"], {"numerator": 19, "denominator": 19})

    def test_component_attribution_improved(self):
        self.assertEqual(COMPARISON["before"]["component_attribution"], {"numerator": 17, "denominator": 19})
        self.assertEqual(COMPARISON["after"]["component_attribution"], {"numerator": 19, "denominator": 19})

    def test_refined_event_semantics(self):
        tc03 = json.loads((ROOT / "outputs/evaluation/p5_04/refined_case_results/TC-03.json").read_text())
        tc05 = json.loads((ROOT / "outputs/evaluation/p5_04/refined_case_results/TC-05.json").read_text())
        tc15 = json.loads((ROOT / "outputs/evaluation/p5_04/refined_case_results/TC-15.json").read_text())
        self.assertIn("recommendation_abstained", tc03["audit"]["event_types"])
        self.assertIn("case_escalated", tc05["audit"]["event_types"])
        self.assertIn("processing_failed", tc15["audit"]["event_types"])

    def test_global_control_owner_attribution(self):
        for case_id in ["TC-14", "TC-18"]:
            result = json.loads((ROOT / f"outputs/evaluation/p5_04/refined_case_results/{case_id}.json").read_text())
            self.assertEqual(result["case_state"]["primary_component"], "workflow_orchestrator")

    def test_raw_output_inventory_exists(self):
        self.assertGreaterEqual(len(MANIFEST["raw_output_inventory"]), 42)
        for item in MANIFEST["raw_output_inventory"]:
            self.assertTrue((ROOT / item["path"]).is_file())

    def test_external_action_boundary(self):
        self.assertEqual(MANIFEST["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
