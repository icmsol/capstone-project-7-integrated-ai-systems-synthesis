"""Tests for the P5-01 frozen evaluation run."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(
    os.environ.get(
        "PROJECT7_REPO_ROOT",
        Path(__file__).resolve().parents[1],
    )
).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project7.frozen_evaluation import (  # noqa: E402
    canonical_sha256,
    derive_observed_behavior,
    read_json,
    sha256_file,
    validate_schema,
    verify_case_manifest,
)


class FrozenEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output_root = (
            ROOT / "outputs" / "evaluation" / "p5_01"
        )
        cls.manifest = read_json(
            cls.output_root / "run_manifest.json"
        )

    def test_freeze_lock_matches_all_locked_files(self):
        lock = read_json(
            ROOT / "config" / "system"
            / "p5_01_freeze_lock.json"
        )
        for item in lock["locked_files"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(
                path.stat().st_size,
                item["bytes"],
            )
            self.assertEqual(
                sha256_file(path),
                item["sha256"],
            )

    def test_all_nineteen_cases_executed(self):
        self.assertEqual(
            self.manifest["case_count_expected"],
            19,
        )
        self.assertEqual(
            self.manifest["case_count_executed"],
            19,
        )
        self.assertEqual(
            self.manifest["missing_case_ids"],
            [],
        )

    def test_all_262_assertions_evaluated(self):
        self.assertEqual(
            self.manifest["assertion_count_expected"],
            262,
        )
        self.assertEqual(
            self.manifest["assertion_count_evaluated"],
            262,
        )

    def test_every_result_is_schema_valid(self):
        for item in self.manifest[
            "case_result_index"
        ]:
            result = read_json(ROOT / item["result_path"])
            validate_schema(
                result,
                "scenario_evaluation_result.schema.json",
                ROOT / "config" / "schemas",
            )

    def test_all_raw_files_match_manifest(self):
        for item in self.manifest[
            "raw_output_inventory"
        ]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(
                path.stat().st_size,
                item["bytes"],
            )
            self.assertEqual(
                sha256_file(path),
                item["sha256"],
            )

    def test_no_case_performed_external_action(self):
        for item in self.manifest[
            "case_result_index"
        ]:
            result = read_json(ROOT / item["result_path"])
            self.assertEqual(result["side_effects"], [])
            self.assertNotIn(
                "autonomous_approval",
                result["claims"],
            )

    def test_behavior_derivation_does_not_read_expected_outcome(self):
        source = (
            ROOT / "src" / "project7"
            / "frozen_evaluation.py"
        ).read_text(encoding="utf-8")
        function_body = source.split(
            "def derive_observed_behavior",
            1,
        )[1].split(
            "def stage_map",
            1,
        )[0]
        self.assertNotIn(
            "expected_outcome.json",
            function_body,
        )
        self.assertNotIn(
            "expected_terminal_outcome",
            function_body,
        )

    def test_manifest_reports_no_post_run_changes(self):
        self.assertFalse(
            self.manifest["post_run_changes_applied"]
        )
        self.assertEqual(
            self.manifest["external_actions_performed"],
            0,
        )

    def test_core_observed_behavior_is_repeatable(self):
        case_dir = (
            ROOT / "data" / "scenarios" / "frozen"
            / "v1.0.1" / "TC-06"
        )
        first, _ = derive_observed_behavior(
            repo_root=ROOT,
            case_dir=case_dir,
        )
        second, _ = derive_observed_behavior(
            repo_root=ROOT,
            case_dir=case_dir,
        )
        self.assertEqual(
            canonical_sha256(first),
            canonical_sha256(second),
        )

    def test_case_manifests_remain_checksum_valid(self):
        for item in self.manifest[
            "case_result_index"
        ]:
            case_dir = (
                ROOT / "data" / "scenarios" / "frozen"
                / "v1.0.1" / item["case_id"]
            )
            verification = verify_case_manifest(case_dir)
            self.assertTrue(
                verification["valid"],
                verification["failures"],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
