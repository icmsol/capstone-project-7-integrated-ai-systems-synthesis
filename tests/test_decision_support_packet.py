"""Tests for P4-05 integrated human review packet."""

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

from project7 import (  # noqa: E402
    PacketAssemblyError,
    assemble_decision_support_packet,
    create_nonbinding_recommendation,
)
from project7.p4_05_pipeline import (  # noqa: E402
    run_packet_assembly,
)
from project7.schema_validation import (  # noqa: E402
    validate_artifact,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class DecisionSupportPacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema_dir = ROOT / "config" / "schemas"
        self.case_state = load_json(
            ROOT / "outputs" / "p4_04"
            / "updated_case_state.json"
        )
        self.recommendation_policy = load_json(
            ROOT / "config" / "system"
            / "recommendation_policy.json"
        )
        self.packet_policy = load_json(
            ROOT / "config" / "system"
            / "decision_support_packet_policy.json"
        )
        self.audit_reference = (
            f"AUD-{self.case_state['case_id']}-10"
        )

    def recommendation(self):
        return create_nonbinding_recommendation(
            case_state=self.case_state,
            policy=self.recommendation_policy,
            schema_dir=self.schema_dir,
            audit_reference=self.audit_reference,
            created_at="2026-08-05T19:15:00Z",
        )

    def packet(self):
        return assemble_decision_support_packet(
            case_state=self.case_state,
            recommendation=self.recommendation(),
            packet_policy=self.packet_policy,
            schema_dir=self.schema_dir,
            packet_id="PACKET-D850D326D21B745D-P4-05",
            generated_at="2026-08-05T19:15:00Z",
            audit_event_ids=[
                self.audit_reference,
                f"AUD-{self.case_state['case_id']}-11",
            ],
        )

    def test_recommendation_escalates_specialized_review(self):
        recommendation = self.recommendation()
        self.assertEqual(
            recommendation["recommendation_code"],
            "R-05",
        )
        self.assertEqual(
            recommendation["recommendation_label"],
            "Escalate — Specialized Review Required",
        )
        self.assertIn(
            "MODEL_DOMAIN_SHIFT",
            recommendation["reason_codes"],
        )
        self.assertIn(
            "MODEL_INPUT_TRUNCATED",
            recommendation["reason_codes"],
        )

    def test_recommendation_uses_validated_evidence_ids(self):
        recommendation = self.recommendation()
        expected = sorted(
            item["evidence_id"]
            for item in self.case_state["evidence_items"]
        )
        self.assertEqual(
            recommendation["supporting_evidence_ids"],
            expected,
        )

    def test_packet_consumes_all_major_component_outputs(self):
        packet = self.packet()
        component_ids = {
            item["component_id"]
            for item in packet["component_artifacts"]
        }
        self.assertTrue(
            {
                "opportunity_intake",
                "organization_alignment",
                "historical_context",
                "clause_triage",
                "official_evidence",
                "nonbinding_recommendation",
                "human_review_packet",
            }
            <= component_ids
        )
        self.assertEqual(
            packet["organization_fit_summary"][
                "alignment_label"
            ],
            "strong_alignment",
        )
        self.assertEqual(
            packet["evidence_summary"][
                "evidence_item_count"
            ],
            2,
        )

    def test_packet_preserves_unresolved_issues(self):
        packet = self.packet()
        reason_codes = {
            reason
            for issue in packet["unresolved_issues"]
            for reason in issue["reason_codes"]
        }
        required = {
            "FULL_SOLICITATION_NOT_REVIEWED",
            "MODEL_DOMAIN_SHIFT",
            "MODEL_INPUT_TRUNCATED",
            "CLAUSE_APPLICABILITY_UNVERIFIED",
            "ELIGIBILITY_UNVERIFIED",
            "CAPACITY_UNVERIFIED",
            "PRICING_AND_MARGIN_UNVERIFIED",
            "SCHEDULE_UNVERIFIED",
            "HUMAN_DISPOSITION_PENDING",
        }
        self.assertTrue(required <= reason_codes)
        self.assertTrue(
            all(
                issue["blocks_final_disposition"]
                for issue in packet["unresolved_issues"]
            )
        )

    def test_packet_has_no_final_decision_or_external_action(self):
        packet = self.packet()
        self.assertIsNone(packet["final_decision"])
        self.assertIsNone(
            packet["human_review"]["human_disposition"]
        )
        self.assertEqual(
            packet["external_actions_performed"],
            0,
        )

    def test_packet_and_recommendation_are_schema_valid(self):
        recommendation = self.recommendation()
        packet = self.packet()
        validate_artifact(
            recommendation,
            "recommendation.schema.json",
            self.schema_dir,
        )
        validate_artifact(
            packet,
            "decision_support_packet.schema.json",
            self.schema_dir,
        )

    def test_missing_component_fails_closed(self):
        incomplete = {
            **self.case_state,
            "evidence_items": [],
        }
        recommendation = self.recommendation()
        with self.assertRaises(
            PacketAssemblyError
        ) as context:
            assemble_decision_support_packet(
                case_state=incomplete,
                recommendation=recommendation,
                packet_policy=self.packet_policy,
                schema_dir=self.schema_dir,
                packet_id="PACKET-INCOMPLETE-P4-05",
                generated_at="2026-08-05T19:15:00Z",
                audit_event_ids=[
                    self.audit_reference,
                    f"AUD-{self.case_state['case_id']}-11",
                ],
            )
        self.assertEqual(
            context.exception.reason_code,
            "PACKET_COMPONENT_MISSING",
        )

    def test_replay_is_deterministic(self):
        self.assertEqual(self.packet(), self.packet())

    def test_integrated_pipeline_sets_awaiting_human_review(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "outputs"
            audit_path = Path(directory) / "audit.jsonl"
            artifacts = run_packet_assembly(
                repo_root=ROOT,
                case_state_path=(
                    ROOT / "outputs" / "p4_04"
                    / "updated_case_state.json"
                ),
                output_directory=output_dir,
                audit_output_path=audit_path,
                event_time="2026-08-05T19:15:00Z",
            )
            case_state = artifacts["updated_case_state"]
            self.assertEqual(
                case_state["case_status"],
                "awaiting_human_review",
            )
            self.assertIsNotNone(
                case_state["recommendation"]
            )
            self.assertIsNone(
                case_state["human_disposition"]
            )
            self.assertEqual(
                len(artifacts["audit_events"]),
                2,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
