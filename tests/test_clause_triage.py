"""Tests for P4-03 bounded clause-theme inference."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

import torch

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
    ClauseTriageError,
    Project4InferencePackage,
    build_clause_prediction,
)
from project7.schema_validation import validate_artifact  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ClauseTriageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas = ROOT / "config" / "schemas"
        self.policy = load_json(
            ROOT / "config" / "system"
            / "clause_triage_policy.json"
        )
        self.registry = load_json(
            ROOT / "tests" / "fixtures" / "p4_03"
            / "synthetic_model_registry.json"
        )
        self.model_dir = (
            ROOT / "tests" / "fixtures" / "p4_03"
            / "synthetic_model_package"
        )
        self.fixtures = load_json(
            ROOT / "tests" / "fixtures" / "p4_03"
            / "controlled_probability_fixtures.json"
        )

    def build(
        self,
        name: str,
        *,
        domain: str = "commercial_contract",
        consequential: bool = False,
    ):
        return build_clause_prediction(
            case_id="CASE-P4-03-TEST",
            passage_id=f"PASSAGE-{name.upper()}",
            probability_result=self.fixtures[name],
            model_artifact_id=(
                "P4-03-SYNTHETIC-COMPATIBILITY-MODEL"
            ),
            model_version="0.0.1",
            model_sha256=self.registry["checkpoint_sha256"],
            policy=self.policy,
            source_domain=domain,
            consequential_use=consequential,
            schema_dir=self.schemas,
        )

    def test_compatible_package_loads_and_predicts(self):
        package = Project4InferencePackage.load(
            self.model_dir,
            registry=self.registry,
            device="cpu",
        )
        result = package.predict_probabilities(
            "The contractor shall maintain records and permit audit."
        )
        self.assertEqual(len(result["probabilities"]), 10)
        self.assertAlmostEqual(
            result["probability_sum"],
            1.0,
            places=5,
        )
        self.assertTrue(
            torch.isfinite(
                torch.tensor(result["probabilities"])
            ).all()
        )

    def test_high_confidence_commercial_text_classifies(self):
        prediction = self.build("high_confidence")
        self.assertEqual(prediction["decision"], "classify")
        self.assertFalse(prediction["domain_warning"])

    def test_low_confidence_abstains(self):
        prediction = self.build("low_confidence")
        self.assertEqual(prediction["decision"], "abstain")
        self.assertIn(
            "MODEL_CONFIDENCE_LOW",
            prediction["reason_codes"],
        )

    def test_public_sector_consequential_use_escalates(self):
        prediction = self.build(
            "high_confidence",
            domain="public_sector",
            consequential=True,
        )
        self.assertEqual(prediction["decision"], "escalate")
        self.assertTrue(prediction["domain_warning"])
        self.assertIn(
            "MODEL_DOMAIN_SHIFT",
            prediction["reason_codes"],
        )

    def test_truncation_escalates_and_is_disclosed(self):
        prediction = self.build(
            "truncated",
            domain="public_sector",
            consequential=True,
        )
        self.assertEqual(prediction["decision"], "escalate")
        self.assertTrue(prediction["truncated"])
        self.assertEqual(prediction["token_count"], 615)
        self.assertIn(
            "MODEL_INPUT_TRUNCATED",
            prediction["reason_codes"],
        )

    def test_empty_passage_fails_closed(self):
        package = Project4InferencePackage.load(
            self.model_dir,
            registry=self.registry,
            device="cpu",
        )
        with self.assertRaises(
            ClauseTriageError
        ) as context:
            package.predict_probabilities("  ")
        self.assertEqual(
            context.exception.reason_code,
            "MODEL_INPUT_INVALID",
        )

    def test_schema_and_prohibited_claim_boundary(self):
        prediction = self.build(
            "high_confidence",
            domain="public_sector",
            consequential=True,
        )
        validate_artifact(
            prediction,
            "clause_prediction.schema.json",
            self.schemas,
        )
        serialized = json.dumps(prediction).lower()
        self.assertNotIn("legally enforceable", serialized)
        self.assertNotIn("contract accepted", serialized)
        self.assertNotIn("compliance approved", serialized)


if __name__ == "__main__":
    unittest.main(verbosity=2)
