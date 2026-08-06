"""Structural tests for the Project 7 GitHub Actions quality gate."""

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
        self.assertIn("actions/upload-artifact@v4", TEXT)

    def test_pinned_python_and_dependency_cache(self):
        self.assertIn('python-version: "3.12"', TEXT)
        self.assertIn("cache: pip", TEXT)
        self.assertIn("requirements_p5_04.txt", TEXT)

    def test_final_quality_verifiers_are_run(self):
        for script in [
            "verify_p5_01_frozen_evaluation.py",
            "verify_p5_02_metrics.py",
            "verify_p5_03_failure_analysis.py",
            "verify_p5_04_refinement.py",
            "verify_p5_04_portability.py",
        ]:
            self.assertIn(script, TEXT)

    def test_evidence_is_uploaded(self):
        self.assertIn("outputs/ci/project7-quality-gate.log", TEXT)
        self.assertIn("outputs/evaluation/p5_04/", TEXT)
        self.assertIn("retention-days: 30", TEXT)

    def test_no_deployment_or_publish_step(self):
        lowered = TEXT.lower()
        self.assertNotIn("deploy", lowered)
        self.assertNotIn("pypi", lowered)
        self.assertNotIn("docker push", lowered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
