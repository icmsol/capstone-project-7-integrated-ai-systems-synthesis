"""Regression tests for P6-03 governance evidence."""

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

class P603GovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.risks = read_csv(ROOT / "docs/P6_03_Risk_Register.csv")
        cls.safeguards = read_csv(ROOT / "docs/P6_03_Safeguard_Matrix.csv")
        cls.gates = read_csv(ROOT / "docs/P6_03_Production_Readiness_Gates.csv")
        cls.summary = json.loads(
            (ROOT / "outputs/evaluation/p6_03/governance_risk_summary.json").read_text(encoding="utf-8")
        )

    def test_every_major_risk_has_required_governance_fields(self):
        self.assertEqual(len(self.risks), 20)
        required = [
            "existing_controls", "accountable_owner", "required_human_oversight",
            "residual_risk", "residual_risk_statement"
        ]
        for row in self.risks:
            for field in required:
                self.assertTrue(row[field].strip(), f"{row['risk_id']} missing {field}")

    def test_all_fixed_safeguards_are_mapped(self):
        self.assertEqual(len(self.safeguards), 30)
        self.assertEqual(
            {r["control_id"] for r in self.safeguards},
            {f"SG-{i:03d}" for i in range(1, 31)},
        )

    def test_high_residual_risk_is_not_hidden(self):
        high = {r["risk_id"] for r in self.risks if r["residual_risk"] == "High"}
        self.assertEqual(high, {"GR-06", "GR-07", "GR-08", "GR-19", "GR-20"})

    def test_production_boundary(self):
        self.assertFalse(self.summary["production_ready"])
        self.assertEqual(len(self.gates), 15)
        self.assertGreater(sum(r["current_status"] == "NOT SATISFIED" for r in self.gates), 0)

    def test_external_action_boundary(self):
        self.assertEqual(self.summary["external_actions_performed"], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
