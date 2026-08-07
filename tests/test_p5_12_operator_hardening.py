"""P5-12 regression tests for operator-acceptance hardening."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(os.environ.get("PROJECT7_REPO_ROOT", Path(__file__).resolve().parents[1])).resolve()
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from project7.profile_loader import load_organization_profile  # noqa: E402
from project7.service_alignment import assess_service_alignment  # noqa: E402
from project7.operator_ui import _format_operator_money, _operator_packet_markdown  # noqa: E402


class P512OperatorHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema_dir = ROOT / "config" / "schemas"
        self.profile = load_organization_profile(
            ROOT / "config" / "profiles" / "icm_solutions.json",
            schema_dir=self.schema_dir,
        )
        self.policy = json.loads(
            (ROOT / "config" / "system" / "service_alignment_policy.json").read_text(encoding="utf-8")
        )

    def _alignment(self, *, title: str, description: str, procurement_method: str):
        opportunity = {
            "case_id": "CASE-P5-12-TEST",
            "title": title,
            "description": description,
            "place_of_performance": "California",
            "procurement_method": procurement_method,
            "contract_vehicle": "",
        }
        return assess_service_alignment(
            opportunity,
            self.profile,
            self.policy,
            schema_dir=self.schema_dir,
        )

    def test_generic_rfp_metadata_does_not_create_rfp_preparation_match(self):
        result = self._alignment(
            title="Information Security Services",
            description=(
                "Managed information security operations, incident response, threat "
                "monitoring, penetration testing, and digital forensics."
            ),
            procurement_method="Request for Proposal",
        )
        ids = {item["capability_id"] for item in result["matched_capabilities"]}
        self.assertNotIn("ICM-PRC-004", ids)

    def test_substantive_rfp_preparation_scope_still_matches(self):
        result = self._alignment(
            title="Procurement Documentation Support",
            description=(
                "Consultant will provide RFP preparation, solicitation development, "
                "requirements drafting, and evaluation criteria development."
            ),
            procurement_method="Consulting services",
        )
        match = next(
            item for item in result["matched_capabilities"]
            if item["capability_id"] == "ICM-PRC-004"
        )
        self.assertEqual(match["match_strength"], "strong")

    def test_operator_money_formatting(self):
        self.assertEqual(
            _format_operator_money({"amount": 12500000.0, "currency": "USD"}),
            "$12,500,000 USD",
        )
        self.assertEqual(_format_operator_money(None), "Not stated")

    def test_operator_packet_is_table_free_and_domain_warning_is_explicit(self):
        packet = json.loads(
            (ROOT / "outputs" / "p4_05" / "decision_support_packet.json").read_text(encoding="utf-8")
        )
        packet["opportunity_summary"]["estimated_value"] = {
            "amount": 12500000.0,
            "currency": "USD",
        }
        rendered = _operator_packet_markdown(packet)
        self.assertNotIn("| Field | Value |", rendered)
        self.assertNotIn("| Passage | Predicted theme", rendered)
        self.assertIn("$12,500,000 USD", rendered)
        if packet["clause_triage_summary"]["domain_warning_count"]:
            self.assertIn("Domain-shift safeguard active", rendered)

    def test_frozen_model_is_not_retrained_by_hardening(self):
        findings = json.loads(
            (ROOT / "outputs" / "evaluation" / "p5_12" / "operator_hardening_findings.json").read_text(encoding="utf-8")
        )
        self.assertFalse(findings["frozen_model_retrained"])
        self.assertFalse(findings["frozen_evaluation_history_rewritten"])
        self.assertEqual(findings["external_actions_performed"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
