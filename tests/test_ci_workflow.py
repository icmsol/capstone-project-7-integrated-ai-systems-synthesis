"""Structural tests for the final Project 7 GitHub Actions quality gate."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github/workflows/project7-quality-gate.yml"
TEXT = WORKFLOW_PATH.read_text(encoding="utf-8")
WORKFLOW = yaml.load(TEXT, Loader=yaml.BaseLoader)


class CIWorkflowTests(unittest.TestCase):
    def test_triggers_cover_push_pull_request_and_manual(self):
        triggers = WORKFLOW["on"]
        self.assertIn("push", triggers)
        self.assertIn("pull_request", triggers)
        self.assertIn("workflow_dispatch", triggers)

    def test_read_only_permissions(self):
        self.assertEqual(WORKFLOW["permissions"]["contents"], "read")

    def test_current_official_action_majors(self):
        self.assertIn("actions/checkout@v5", TEXT)
        self.assertIn("actions/setup-python@v6", TEXT)
        self.assertIn("actions/upload-artifact@v7", TEXT)
        self.assertNotIn("actions/upload-artifact@v4", TEXT)

    def test_pinned_python_and_final_dependency_lock(self):
        self.assertIn('python-version: "3.12"', TEXT)
        self.assertIn("cache: pip", TEXT)
        self.assertIn("cache-dependency-path: requirements.txt", TEXT)
        self.assertIn("-r requirements.txt", TEXT)
        self.assertIn("pip check", TEXT)

    def test_final_quality_verifiers_are_run(self):
        for script in [
            "verify_p5_01_frozen_evaluation.py",
            "verify_p5_02_metrics.py",
            "verify_p5_03_failure_analysis.py",
            "verify_p5_04_refinement.py",
            "verify_p5_04_portability.py",
            "verify_p5_05_final_baseline.py",
            "verify_p5_06_acceptance_corrected_baseline.py",
            "verify_p9_02_submission_environment.py",
        ]:
            self.assertIn(script, TEXT)

    def test_hosted_metadata_and_final_evidence_are_uploaded(self):
        self.assertIn("generate_ci_run_metadata.py", TEXT)
        self.assertIn("outputs/ci/hosted-run-metadata.json", TEXT)
        self.assertIn("outputs/evaluation/p5_05/", TEXT)
        self.assertIn("outputs/evaluation/p9_02/", TEXT)
        self.assertIn("outputs/ci/p9_02_pip_freeze.txt", TEXT)
        self.assertIn("requirements.txt", TEXT)
        self.assertIn("retention-days: 30", TEXT)

    def test_no_deployment_or_publish_step(self):
        lowered = TEXT.lower()
        self.assertNotIn("deploy", lowered)
        self.assertNotIn("pypi", lowered)
        self.assertNotIn("docker push", lowered)
        self.assertNotIn("contents: write", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
