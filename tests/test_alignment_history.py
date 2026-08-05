"""Tests for P4-02 organization alignment and historical context."""

from __future__ import annotations

import csv
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

from project7 import (  # noqa: E402
    HistoricalContextError,
    assess_service_alignment,
    attach_historical_context,
    load_organization_profile,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class AlignmentHistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schemas = ROOT / "config" / "schemas"
        self.opportunity = load_json(
            ROOT / "outputs" / "p4_01"
            / "normalized_opportunity.json"
        )
        self.alignment_policy = load_json(
            ROOT / "config" / "system"
            / "service_alignment_policy.json"
        )
        self.history_policy = load_json(
            ROOT / "config" / "system"
            / "historical_context_policy.json"
        )
        self.icm = load_organization_profile(
            ROOT / "config" / "profiles"
            / "icm_solutions.json",
            schema_dir=self.schemas,
        )
        self.fictional = load_organization_profile(
            ROOT / "config" / "profiles"
            / "fictional_small_business.json",
            schema_dir=self.schemas,
        )

    def test_profile_loader_is_configuration_driven(self):
        self.assertEqual(len(self.icm.service_catalog), 54)
        self.assertEqual(
            len(
                {
                    row["service_family_id"]
                    for row in self.icm.service_catalog
                }
            ),
            8,
        )
        self.assertEqual(len(self.fictional.service_catalog), 3)
        self.assertEqual(
            self.icm.profile["organization_id"],
            "ICMSOL",
        )
        self.assertEqual(
            self.fictional.profile["organization_id"],
            "RCALABS",
        )

    def test_same_opportunity_changes_by_profile_without_code_change(self):
        icm_result = assess_service_alignment(
            self.opportunity,
            self.icm,
            self.alignment_policy,
            schema_dir=self.schemas,
        )
        fictional_result = assess_service_alignment(
            self.opportunity,
            self.fictional,
            self.alignment_policy,
            schema_dir=self.schemas,
        )
        self.assertEqual(
            icm_result["alignment_label"],
            "strong_alignment",
        )
        self.assertGreaterEqual(
            len(icm_result["matched_capabilities"]),
            2,
        )
        self.assertEqual(
            fictional_result["alignment_label"],
            "no_alignment",
        )
        self.assertEqual(
            fictional_result["matched_capabilities"],
            [],
        )

    def test_exclusion_first_blocks_positive_capability(self):
        excluded_opportunity = {
            **self.opportunity,
            "title": (
                "Website content writing only and custom application "
                "development support"
            ),
            "normalized_title": (
                "website content writing only and custom application "
                "development support"
            ),
            "description": (
                "The engagement is limited to website content writing only."
            ),
        }
        result = assess_service_alignment(
            excluded_opportunity,
            self.icm,
            self.alignment_policy,
            schema_dir=self.schemas,
        )
        blocked = {
            item["term"]
            for item in result["excluded_matches"]
        }
        self.assertIn("website content writing only", blocked)
        matched_ids = {
            item["capability_id"]
            for item in result["matched_capabilities"]
        }
        self.assertNotIn("ICM-CDI-003", matched_ids)

    def test_historical_context_is_descriptive_and_checksum_verified(self):
        alignment = assess_service_alignment(
            self.opportunity,
            self.icm,
            self.alignment_policy,
            schema_dir=self.schemas,
        )
        context = attach_historical_context(
            repo_root=ROOT,
            opportunity=self.opportunity,
            service_alignment=alignment,
            organization_id="ICMSOL",
            policy=self.history_policy,
            schema_dir=self.schemas,
        )
        self.assertEqual(context["source_records"], 29646)
        self.assertEqual(
            context["matched_historical_records"],
            122,
        )
        self.assertEqual(
            context["staffing_family_counts"][
                "Technology Delivery"
            ],
            79,
        )
        self.assertEqual(
            context["staffing_family_counts"][
                "Advisory, Assurance & Change"
            ],
            43,
        )
        limitation_codes = {
            item["code"]
            for item in context["limitations"]
        }
        self.assertIn("DESCRIPTIVE_ONLY", limitation_codes)
        self.assertIn(
            "NOT_CAPACITY_OR_AWARD_FORECAST",
            limitation_codes,
        )
        self.assertIn("not predict", context["interpretation"])

    def test_asset_checksum_change_warns_and_stops_context_use(self):
        registry_path = (
            ROOT / "data" / "reference" / "project2"
            / "project2_asset_registry.json"
        )
        original = registry_path.read_text(encoding="utf-8")
        registry = json.loads(original)
        registry["assets"][0]["sha256"] = "0" * 64
        registry_path.write_text(
            json.dumps(registry, indent=2) + "\n",
            encoding="utf-8",
        )
        try:
            alignment = assess_service_alignment(
                self.opportunity,
                self.icm,
                self.alignment_policy,
                schema_dir=self.schemas,
            )
            with self.assertRaises(
                HistoricalContextError
            ) as context:
                attach_historical_context(
                    repo_root=ROOT,
                    opportunity=self.opportunity,
                    service_alignment=alignment,
                    organization_id="ICMSOL",
                    policy=self.history_policy,
                    schema_dir=self.schemas,
                )
            self.assertEqual(
                context.exception.reason_code,
                "HISTORICAL_ASSET_MISSING",
            )
            self.assertEqual(
                context.exception.behavior,
                "warn_and_continue",
            )
        finally:
            registry_path.write_text(
                original,
                encoding="utf-8",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
