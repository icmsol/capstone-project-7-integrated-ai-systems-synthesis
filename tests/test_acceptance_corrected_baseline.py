"""Tests for the P5-06 versioned acceptance correction."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / "outputs/evaluation/p5_06/acceptance_corrected_baseline.json").read_text())
RERUN = json.loads((ROOT / "outputs/evaluation/p5_06/frozen_suite_rerun_summary.json").read_text())
FINDINGS = json.loads((ROOT / "outputs/evaluation/p5_06/manual_operator_acceptance_findings.json").read_text())
OVERLAY = json.loads((ROOT / "outputs/evaluation/p5_06/versioned_overlay_manifest.json").read_text())


class AcceptanceCorrectedBaselineTests(unittest.TestCase):
    def test_version_is_explicit_and_parent_is_preserved(self):
        self.assertEqual(BASELINE["baseline_id"], "PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.1")
        self.assertEqual(BASELINE["parent_baseline_id"], "PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.0")

    def test_frozen_suite_remains_fully_passing(self):
        self.assertEqual(RERUN["status_counts"], {"PASS": 19, "PARTIAL": 0, "FAIL": 0})
        self.assertEqual(RERUN["assertions_passed"], 262)
        self.assertEqual(RERUN["assertions_total"], 262)
        self.assertFalse(RERUN["frozen_inputs_changed"])

    def test_manual_defects_are_explicit(self):
        findings = {item["finding_id"]: item for item in FINDINGS["findings"]}
        for finding_id in ["MAF-02", "MAF-04", "MAF-05"]:
            self.assertEqual(findings[finding_id]["disposition"], "corrected")
        self.assertEqual(findings["MAF-03"]["disposition"], "document")

    def test_overlay_is_versioned_and_nonempty(self):
        self.assertEqual(OVERLAY["overlay_version"], "1.0.1")
        self.assertGreaterEqual(len(OVERLAY["files"]), 10)


    def test_ci_workflow_is_structurally_verified_not_byte_frozen(self):
        workflow_items = [
            item for item in OVERLAY["files"]
            if item["path"] == ".github/workflows/project7-quality-gate.yml"
        ]
        self.assertEqual(len(workflow_items), 1)
        self.assertEqual(
            workflow_items[0]["verification_mode"],
            "structural_current_ci",
        )
        self.assertIn(
            "reference_sha256_at_overlay_creation",
            workflow_items[0],
        )

    def test_human_authority_and_external_action_boundary(self):
        self.assertTrue(BASELINE["manual_acceptance"]["human_review_required"])
        self.assertFalse(BASELINE["manual_acceptance"]["final_decision_created"])
        self.assertEqual(BASELINE["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
