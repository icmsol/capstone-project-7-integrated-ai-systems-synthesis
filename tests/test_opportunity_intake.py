"""Tests for P4-01 opportunity intake and provenance."""

from __future__ import annotations

import hashlib
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

from project7 import IntakeError, normalize_opportunity  # noqa: E402


FIXED_TIME = "2026-08-05T16:30:00Z"
DATA = ROOT / "data" / "implementation" / "p4_01"
FIXTURES = ROOT / "tests" / "fixtures" / "p4_01"
SCHEMAS = ROOT / "config" / "schemas"
CONFIG = ROOT / "config" / "system"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class OpportunityIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw_path = DATA / "raw_opportunity.json"
        self.raw_bytes = self.raw_path.read_bytes()
        self.raw = json.loads(self.raw_bytes.decode("utf-8"))
        self.approval = load_json(DATA / "source_approval.json")
        self.organization = load_json(
            CONFIG / "p4_01_reference_organization_context.json"
        )
        self.rules = load_json(
            CONFIG / "opportunity_intake_rules.json"
        )

    def run_valid(self):
        return normalize_opportunity(
            self.raw,
            self.approval,
            self.organization,
            self.rules,
            schema_dir=SCHEMAS,
            raw_source_bytes=self.raw_bytes,
            event_time=FIXED_TIME,
        )

    def test_valid_intake_is_schema_valid_and_traceable(self):
        result = self.run_valid()
        opportunity = result.normalized_opportunity

        self.assertEqual(opportunity["status"], "open")
        self.assertEqual(
            opportunity["due_at"],
            "2026-09-16T00:00:00Z",
        )
        self.assertEqual(opportunity["missing_fields"], [])
        self.assertEqual(
            opportunity["source"]["sha256"],
            hashlib.sha256(self.raw_bytes).hexdigest(),
        )
        self.assertEqual(
            opportunity["original_values"],
            self.raw,
        )
        self.assertEqual(
            result.initial_case_state["case_status"],
            "intake_validated",
        )
        self.assertEqual(len(result.audit_events), 2)
        self.assertEqual(
            result.audit_events[1]["previous_event_hash"],
            result.audit_events[0]["event_hash"],
        )

    def test_replay_is_deterministic(self):
        first = self.run_valid()
        second = self.run_valid()

        self.assertEqual(
            first.normalized_opportunity,
            second.normalized_opportunity,
        )
        self.assertEqual(
            first.initial_case_state,
            second.initial_case_state,
        )
        self.assertEqual(first.audit_events, second.audit_events)

    def test_unapproved_source_fails_closed(self):
        approval = load_json(
            FIXTURES / "unapproved_source_approval.json"
        )
        with self.assertRaises(IntakeError) as context:
            normalize_opportunity(
                self.raw,
                approval,
                self.organization,
                self.rules,
                schema_dir=SCHEMAS,
                raw_source_bytes=self.raw_bytes,
                event_time=FIXED_TIME,
            )
        self.assertEqual(
            context.exception.reason_code,
            "SOURCE_NOT_APPROVED",
        )
        self.assertEqual(
            context.exception.behavior,
            "fail_closed",
        )

    def test_checksum_change_defers(self):
        approval = load_json(
            FIXTURES / "checksum_mismatch_source_approval.json"
        )
        with self.assertRaises(IntakeError) as context:
            normalize_opportunity(
                self.raw,
                approval,
                self.organization,
                self.rules,
                schema_dir=SCHEMAS,
                raw_source_bytes=self.raw_bytes,
                event_time=FIXED_TIME,
            )
        self.assertEqual(
            context.exception.reason_code,
            "SOURCE_VERSION_CHANGED",
        )
        self.assertEqual(context.exception.behavior, "defer")

    def test_sparse_source_preserves_missing_fields(self):
        sparse_path = (
            FIXTURES / "sparse_raw_opportunity.json"
        )
        sparse_bytes = sparse_path.read_bytes()
        sparse = json.loads(sparse_bytes.decode("utf-8"))
        approval = load_json(
            FIXTURES / "sparse_source_approval.json"
        )
        result = normalize_opportunity(
            sparse,
            approval,
            self.organization,
            self.rules,
            schema_dir=SCHEMAS,
            raw_source_bytes=sparse_bytes,
            event_time=FIXED_TIME,
        )
        self.assertIn(
            "description",
            result.normalized_opportunity["missing_fields"],
        )
        self.assertIn(
            "due_at",
            result.normalized_opportunity["missing_fields"],
        )
        self.assertIsNone(
            result.normalized_opportunity["description"]
        )
        self.assertEqual(
            result.audit_events[1]["status"],
            "warned",
        )
        self.assertIn(
            "STRUCTURED_ANALYSIS_INSUFFICIENT",
            result.audit_events[1]["reason_codes"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
