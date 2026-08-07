"""Tests for the authorized human-disposition recorder."""

from __future__ import annotations

import copy
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

from project7.human_disposition import (  # noqa: E402
    HumanDispositionError,
    record_human_disposition,
)
from project7.schema_validation import validate_artifact  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class HumanDispositionRecorderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case_state_path = ROOT / "outputs" / "p4_05" / "updated_case_state.json"
        self.prior_audit_path = ROOT / "audit" / "p4_05_packet_events.jsonl"
        self.reviewer_roles_path = ROOT / "config" / "profiles" / "icm_reviewer_roles.json"
        self.case_state = load_json(self.case_state_path)
        self.recommendation = copy.deepcopy(self.case_state["recommendation"])
        self.base_response = {
            "disposition_schema_version": "1.0.0",
            "disposition_id": "DISP-P5-08-TEST-001",
            "case_id": self.case_state["case_id"],
            "recommendation_id": self.case_state["recommendation"]["recommendation_id"],
            "reviewer": {
                "role_id": "RR-03",
                "role_name": "Contracts or Procurement Specialist",
                "organization_id": "ICMSOL",
            },
            "disposition": "defer_pending_information",
            "rationale": (
                "Defer pending complete solicitation review and confirmation of "
                "the applicable authoritative contract requirements."
            ),
            "modified_conditions": [],
            "decided_at": "2026-08-07T20:00:00Z",
        }

    def _run(self, response=None, reviewer_identity="TEST-AUTHORIZED-REVIEWER"):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "outputs"
            audit_path = Path(directory) / "human_disposition_event.jsonl"
            artifacts = record_human_disposition(
                repo_root=ROOT,
                case_state_path=self.case_state_path,
                human_response=copy.deepcopy(response or self.base_response),
                reviewer_identity=reviewer_identity,
                reviewer_roles_path=self.reviewer_roles_path,
                prior_audit_path=self.prior_audit_path,
                output_directory=output_dir,
                audit_output_path=audit_path,
            )
            self.assertTrue((output_dir / "human_disposition.json").is_file())
            self.assertTrue((output_dir / "updated_case_state.json").is_file())
            self.assertTrue(audit_path.is_file())
            return artifacts

    def test_defer_records_separate_human_disposition(self):
        artifacts = self._run()
        updated = artifacts["updated_case_state"]
        self.assertEqual(updated["case_status"], "deferred")
        self.assertEqual(updated["human_disposition"]["disposition"], "defer_pending_information")
        self.assertEqual(updated["recommendation"], self.recommendation)
        self.assertTrue(artifacts["recommendation_unchanged"])
        self.assertEqual(artifacts["external_actions_performed"], 0)
        validate_artifact(
            updated["human_disposition"],
            "human_disposition.schema.json",
            ROOT / "config" / "schemas",
        )
        validate_artifact(
            updated,
            "integrated_case_state.schema.json",
            ROOT / "config" / "schemas",
        )

    def test_audit_event_is_human_and_continues_chain(self):
        artifacts = self._run(reviewer_identity="TEST-HUMAN-001")
        event = artifacts["audit_event"]
        prior = [
            json.loads(line)
            for line in self.prior_audit_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(event["event_type"], "human_disposition_recorded")
        self.assertEqual(event["actor_type"], "human")
        self.assertEqual(event["actor_id"], "TEST-HUMAN-001")
        self.assertEqual(event["previous_event_hash"], prior[-1]["event_hash"])
        self.assertEqual(event["sanitized_details"]["external_actions_performed"], 0)

    def test_accept_finalizes_case(self):
        response = copy.deepcopy(self.base_response)
        response["disposition"] = "accept"
        response["rationale"] = (
            "Accept the advisory recommendation as the documented human response "
            "for this controlled test case."
        )
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "outputs"
            artifacts = record_human_disposition(
                repo_root=ROOT,
                case_state_path=self.case_state_path,
                human_response=response,
                reviewer_identity="TEST-AUTHORIZED-REVIEWER",
                reviewer_roles_path=self.reviewer_roles_path,
                prior_audit_path=self.prior_audit_path,
                output_directory=output_dir,
                audit_output_path=Path(directory) / "audit.jsonl",
            )
            self.assertEqual(artifacts["updated_case_state"]["case_status"], "finalized")
            self.assertTrue((output_dir / "finalized_case_state.json").is_file())

    def test_unauthorized_reviewer_fails_closed(self):
        response = copy.deepcopy(self.base_response)
        response["reviewer"] = {
            "role_id": "RR-99",
            "role_name": "Unauthorized Reviewer",
            "organization_id": "ICMSOL",
        }
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(HumanDispositionError) as context:
                record_human_disposition(
                    repo_root=ROOT,
                    case_state_path=self.case_state_path,
                    human_response=response,
                    reviewer_identity="TEST-UNAUTHORIZED",
                    reviewer_roles_path=self.reviewer_roles_path,
                    prior_audit_path=self.prior_audit_path,
                    output_directory=Path(directory) / "outputs",
                    audit_output_path=Path(directory) / "audit.jsonl",
                )
        self.assertEqual(context.exception.reason_code, "REVIEWER_NOT_AUTHORIZED")
        self.assertEqual(context.exception.behavior, "fail_closed")

    def test_short_rationale_defers(self):
        response = copy.deepcopy(self.base_response)
        response["rationale"] = "Too short"
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(HumanDispositionError) as context:
                record_human_disposition(
                    repo_root=ROOT,
                    case_state_path=self.case_state_path,
                    human_response=response,
                    reviewer_identity="TEST-AUTHORIZED-REVIEWER",
                    reviewer_roles_path=self.reviewer_roles_path,
                    prior_audit_path=self.prior_audit_path,
                    output_directory=Path(directory) / "outputs",
                    audit_output_path=Path(directory) / "audit.jsonl",
                )
        self.assertEqual(context.exception.reason_code, "HUMAN_RATIONALE_MISSING")
        self.assertEqual(context.exception.behavior, "defer")

    def test_recommendation_mismatch_fails_closed(self):
        response = copy.deepcopy(self.base_response)
        response["recommendation_id"] = "REC-MISMATCH-001"
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(HumanDispositionError) as context:
                record_human_disposition(
                    repo_root=ROOT,
                    case_state_path=self.case_state_path,
                    human_response=response,
                    reviewer_identity="TEST-AUTHORIZED-REVIEWER",
                    reviewer_roles_path=self.reviewer_roles_path,
                    prior_audit_path=self.prior_audit_path,
                    output_directory=Path(directory) / "outputs",
                    audit_output_path=Path(directory) / "audit.jsonl",
                )
        self.assertEqual(context.exception.reason_code, "HUMAN_DECISION_REQUIRED")

    def test_escalation_target_must_be_authorized(self):
        response = copy.deepcopy(self.base_response)
        response["disposition"] = "escalate"
        response["rationale"] = (
            "Escalate this case to another authorized specialist because material "
            "contract questions remain unresolved."
        )
        response["escalated_to"] = {
            "role_id": "RR-99",
            "role_name": "Unauthorized Target",
            "organization_id": "ICMSOL",
        }
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(HumanDispositionError) as context:
                record_human_disposition(
                    repo_root=ROOT,
                    case_state_path=self.case_state_path,
                    human_response=response,
                    reviewer_identity="TEST-AUTHORIZED-REVIEWER",
                    reviewer_roles_path=self.reviewer_roles_path,
                    prior_audit_path=self.prior_audit_path,
                    output_directory=Path(directory) / "outputs",
                    audit_output_path=Path(directory) / "audit.jsonl",
                )
        self.assertEqual(context.exception.reason_code, "REVIEWER_NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
