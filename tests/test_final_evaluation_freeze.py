"""Tests for the Project 7 final evaluation freeze."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_05"
        / "final_evaluation_baseline.json"
    ).read_text(encoding="utf-8")
)
METRICS = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_05"
        / "final_metric_summary.json"
    ).read_text(encoding="utf-8")
)
EVIDENCE = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_05"
        / "final_evidence_map.json"
    ).read_text(encoding="utf-8")
)
INVENTORY = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_05"
        / "final_artifact_inventory.json"
    ).read_text(encoding="utf-8")
)
VALIDATION = json.loads(
    (
        ROOT / "outputs" / "evaluation" / "p5_05"
        / "repository_validation_report.json"
    ).read_text(encoding="utf-8")
)
HOSTED_RUN_1 = json.loads(
    (
        ROOT / "docs" / "P5_05_Hosted_CI_Run_1_Evidence.json"
    ).read_text(encoding="utf-8")
)
FREEZE_POLICY = json.loads(
    (
        ROOT / "config" / "system"
        / "final_evaluation_freeze_policy.json"
    ).read_text(encoding="utf-8")
)


class FinalEvaluationFreezeTests(unittest.TestCase):
    def test_baseline_is_frozen(self):
        self.assertEqual(BASELINE["baseline_status"], "frozen")
        self.assertEqual(BASELINE["freeze_version"], "1.0.0")

    def test_final_case_and_assertion_results(self):
        results = BASELINE["evaluation_results"]
        self.assertEqual(results["cases_passed"], 19)
        self.assertEqual(results["cases_partial"], 0)
        self.assertEqual(results["cases_failed"], 0)
        self.assertEqual(results["assertions_passed"], 262)
        self.assertEqual(results["assertions_evaluated"], 262)

    def test_no_regressions_or_frozen_input_changes(self):
        results = BASELINE["evaluation_results"]
        self.assertEqual(results["regression_case_ids"], [])
        self.assertFalse(results["frozen_inputs_changed"])

    def test_all_final_metrics_are_complete(self):
        self.assertEqual(METRICS["metric_count"], 15)
        for metric in METRICS["metrics"]:
            self.assertEqual(metric["numerator"], metric["denominator"])
            self.assertEqual(metric["percentage"], 100.0)

    def test_portability_preserves_control_boundaries(self):
        portability = BASELINE["configuration_portability"]
        self.assertTrue(portability["same_executable_code"])
        self.assertTrue(portability["same_schemas"])
        self.assertTrue(portability["same_fixed_safeguards"])
        self.assertTrue(
            portability["profile_specific_alignment_and_recommendations"]
        )
        self.assertEqual(portability["external_actions_performed"], 0)

    def test_final_evidence_map_is_complete(self):
        self.assertGreaterEqual(EVIDENCE["evidence_count"], 19)
        paths = {
            item["primary_path"]
            for item in EVIDENCE["evidence"]
        }
        self.assertIn("docs/Integrated_System_Architecture.md", paths)
        self.assertIn("docs/P5_05_Final_Evaluation_Freeze.md", paths)
        self.assertIn(".github/workflows/project7-quality-gate.yml", paths)

    def test_repository_validation_passed(self):
        self.assertEqual(VALIDATION["validation_status"], "PASS")
        self.assertEqual(VALIDATION["credential_pattern_hits"], [])
        self.assertEqual(VALIDATION["files_over_100_mb"], [])
        self.assertEqual(VALIDATION["merge_conflict_marker_hits"], [])
        self.assertEqual(VALIDATION["notebook_traceback_outputs"], [])
        self.assertEqual(
            VALIDATION["unresolved_implementation_markers"],
            [],
        )
        self.assertEqual(VALIDATION["missing_required_paths"], [])

    def test_inventory_is_substantial_and_versioned(self):
        self.assertGreater(INVENTORY["file_count"], 900)
        self.assertEqual(INVENTORY["inventory_schema_version"], "1.1.0")
        self.assertEqual(len(INVENTORY["repository_state_digest"]), 64)

    def test_notebooks_use_canonical_source_verification(self):
        notebooks = [
            item
            for item in INVENTORY["files"]
            if item["path"].endswith(".ipynb")
        ]
        self.assertGreaterEqual(len(notebooks), 1)
        for item in notebooks:
            self.assertEqual(
                item["verification_mode"],
                "canonical_notebook_sources",
            )
            self.assertEqual(len(item["canonical_sha256"]), 64)
            self.assertFalse(item["raw_verification_enforced"])

    def test_hosted_run_one_is_preserved(self):
        self.assertEqual(HOSTED_RUN_1["status"], "success")
        self.assertEqual(HOSTED_RUN_1["total_duration_seconds"], 24)
        self.assertEqual(HOSTED_RUN_1["artifact_count"], 1)
        self.assertEqual(HOSTED_RUN_1["warning_count"], 1)

    def test_ci_uses_node24_compatible_artifact_action(self):
        ci = BASELINE["ci_baseline"]
        self.assertEqual(
            ci["artifact_action"],
            "actions/upload-artifact@v7",
        )
        workflow = (
            ROOT / ".github" / "workflows"
            / "project7-quality-gate.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact@v7", workflow)
        self.assertNotIn("actions/upload-artifact@v4", workflow)

    def test_freeze_policy_prohibits_silent_evidence_edits(self):
        prohibited = FREEZE_POLICY["prohibited_post_freeze_changes"]
        self.assertIn(
            "editing P5-01 or P5-04 raw results",
            prohibited,
        )
        self.assertIn(
            "changing model or evidence thresholds without a new evaluation version",
            prohibited,
        )

    def test_external_action_boundary(self):
        self.assertEqual(BASELINE["external_actions_performed"], 0)
        self.assertEqual(METRICS["external_actions_performed"], 0)
        self.assertEqual(VALIDATION["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
