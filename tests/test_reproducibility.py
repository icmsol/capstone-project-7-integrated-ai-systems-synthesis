"""Tests for P4-06 audit and reproducibility outputs."""

from __future__ import annotations

import json
import os
import sys
import tempfile
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

from project7.p4_06_pipeline import (  # noqa: E402
    run_reproducibility_pipeline,
)
from project7.reproducibility import (  # noqa: E402
    ReproducibilityError,
    read_json,
    read_jsonl,
    verify_audit_chain,
    verify_inventory,
)
from project7.schema_validation import (  # noqa: E402
    validate_artifact,
)


class ReproducibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.temp_root = Path(cls.temp.name)
        cls.artifacts = run_reproducibility_pipeline(
            repo_root=ROOT,
            output_directory=(
                cls.temp_root / "outputs" / "p4_06"
            ),
            audit_output_directory=(
                cls.temp_root / "audit"
            ),
            policy_path=(
                ROOT
                / "config"
                / "system"
                / "reproducibility_policy.json"
            ),
            event_time="2026-08-05T20:00:00Z",
        )
        cls.manifest = cls.artifacts["manifest"]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_manifest_is_schema_valid(self):
        validate_artifact(
            self.manifest,
            "reproducibility_manifest.schema.json",
            ROOT / "config" / "schemas",
        )

    def test_inventory_has_no_missing_or_mismatched_files(self):
        result = verify_inventory(
            repo_root=ROOT,
            inventory=self.manifest[
                "artifact_inventory"
            ],
        )
        self.assertEqual(result["status"], "PASS")
        self.assertGreater(
            result["artifact_count"],
            50,
        )

    def test_audit_chain_contains_events_one_through_thirteen(self):
        events = self.artifacts[
            "consolidated_events"
        ]
        summary = verify_audit_chain(
            events,
            expected_sequences=list(range(1, 14)),
        )
        self.assertEqual(summary["event_count"], 13)
        self.assertEqual(
            summary["first_event_id"],
            "AUD-CASE-D850D326D21B745D-01",
        )
        self.assertEqual(
            summary["last_event_id"],
            "AUD-CASE-D850D326D21B745D-13",
        )

    def test_deterministic_packet_replay_passes(self):
        replay = self.manifest[
            "replay_verification"
        ]
        self.assertEqual(replay["status"], "PASS")
        self.assertEqual(
            replay["preserved_packet_sha256"],
            replay["replayed_packet_sha256"],
        )
        self.assertEqual(
            replay["preserved_case_sha256"],
            replay["replayed_case_sha256"],
        )

    def test_final_route_preserves_human_authority(self):
        route = self.manifest["final_routing"]
        self.assertEqual(
            route["case_status"],
            "awaiting_human_review",
        )
        self.assertEqual(
            route["recommendation_code"],
            "R-05",
        )
        self.assertIsNone(route["human_disposition"])
        self.assertIsNone(route["final_decision"])
        self.assertEqual(
            self.manifest["external_actions_performed"],
            0,
        )

    def test_full_reexecution_dependency_is_disclosed(self):
        dependency = self.manifest[
            "execution_environment"
        ]["actual_model_dependency"]
        self.assertEqual(
            dependency["path"],
            "models/project4/selected_clause_classifier.pt",
        )
        self.assertTrue(
            dependency[
                "required_for_full_reexecution"
            ]
        )

    def test_checksum_mutation_is_detected(self):
        inventory = [
            dict(item)
            for item in self.manifest[
                "artifact_inventory"
            ]
        ]
        inventory[0]["sha256"] = "0" * 64
        with self.assertRaises(
            ReproducibilityError
        ) as context:
            verify_inventory(
                repo_root=ROOT,
                inventory=inventory,
            )
        self.assertEqual(
            context.exception.reason_code,
            "ARTIFACT_CHECKSUM_MISMATCH",
        )

    def test_audit_hash_mutation_is_detected(self):
        events = [
            dict(item)
            for item in self.artifacts[
                "consolidated_events"
            ]
        ]
        events[5]["event_hash"] = "0" * 64
        with self.assertRaises(
            ReproducibilityError
        ) as context:
            verify_audit_chain(
                events,
                expected_sequences=list(range(1, 14)),
            )
        self.assertEqual(
            context.exception.reason_code,
            "AUDIT_CHAIN_INVALID",
        )

    def test_replay_plan_lists_all_phase_four_commands(self):
        commands = self.manifest[
            "replay_plan"
        ]["full_pipeline_commands"]
        self.assertEqual(len(commands), 6)
        for phase in range(1, 7):
            self.assertTrue(
                any(
                    f"run_p4_0{phase}_validation.py"
                    in command
                    for command in commands
                )
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
