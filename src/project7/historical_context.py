"""Descriptive frozen historical procurement context."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .schema_validation import validate_artifact


class HistoricalContextError(RuntimeError):
    """Historical asset integrity or comparability error."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        behavior: str,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = behavior


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


def _asset_path(repo_root: Path, relative_path: str) -> Path:
    return (repo_root / relative_path).resolve()


def _verify_registry(
    repo_root: Path,
    registry: dict[str, Any],
) -> dict[str, str]:
    checksums = {}
    for asset in registry["assets"]:
        path = _asset_path(repo_root, asset["path"])
        if not path.exists():
            raise HistoricalContextError(
                "HISTORICAL_ASSET_MISSING",
                f"Historical asset is missing: {path}",
                "warn_and_continue",
            )
        observed = _sha256_file(path)
        if observed != asset["sha256"]:
            raise HistoricalContextError(
                "HISTORICAL_ASSET_MISSING",
                f"Historical asset checksum changed: {path}",
                "warn_and_continue",
            )
        checksums[path.name] = observed
    return checksums


def _mapping_file(
    repo_root: Path,
    organization_id: str,
    mapping_registry: dict[str, Any],
) -> tuple[Path, str]:
    for entry in mapping_registry["mappings"]:
        if entry["organization_id"] == organization_id:
            return (
                repo_root
                / "config"
                / "profiles"
                / entry["mapping_file"],
                entry["comparability"],
            )
    raise HistoricalContextError(
        "HISTORICAL_CONTEXT_NOT_COMPARABLE",
        f"No historical mapping exists for {organization_id}.",
        "abstain",
    )


def attach_historical_context(
    *,
    repo_root: Path,
    opportunity: dict[str, Any],
    service_alignment: dict[str, Any],
    organization_id: str,
    policy: dict[str, Any],
    schema_dir: Path,
) -> dict[str, Any]:
    """Attach descriptive aggregate context to a validated alignment."""

    registry = _load_json(
        _asset_path(repo_root, policy["asset_registry_path"])
    )
    checksums = _verify_registry(repo_root, registry)
    summary = _load_json(
        _asset_path(repo_root, policy["analysis_summary_path"])
    )
    aggregate_rows = _load_csv(
        _asset_path(repo_root, policy["historical_aggregate_path"])
    )
    mapping_registry = _load_json(
        _asset_path(repo_root, policy["mapping_registry_path"])
    )
    mapping_path, comparability = _mapping_file(
        repo_root,
        organization_id,
        mapping_registry,
    )
    mapping_rows = _load_csv(mapping_path)

    matched_families = {
        item["service_family_id"]
        for item in service_alignment["matched_capabilities"]
    }
    selected_categories = {
        row["project2_service_category"]
        for row in mapping_rows
        if row["active"].strip().upper() == "TRUE"
        and row["service_family_id"] in matched_families
    }

    service_counts: Counter[str] = Counter()
    staffing_counts: Counter[str] = Counter()

    for row in aggregate_rows:
        if row["service_category"] not in selected_categories:
            continue
        count = int(row["historical_record_count"])
        service_counts[row["service_category"]] += count
        staffing_counts[row["staffing_family"]] += count

    matched_count = sum(service_counts.values())
    reason_limitations = [
        {
            "code": "DESCRIPTIVE_ONLY",
            "description": (
                "Historical counts summarize a frozen 2021-07-01 through "
                "2026-06-30 procurement dataset and are not predictive."
            ),
            "material": True,
            "mitigation": (
                "Use current solicitation evidence and authorized human judgment."
            ),
        },
        {
            "code": "TITLE_CLASSIFICATION_LIMIT",
            "description": (
                "The source records were identified using transparent "
                "title-based rules and may not reflect complete solicitation scope."
            ),
            "material": True,
            "mitigation": (
                "Treat counts as directional context and review current full-text evidence."
            ),
        },
        {
            "code": "NOT_CAPACITY_OR_AWARD_FORECAST",
            "description": (
                "The counts do not measure contract value, labor hours, "
                "current staffing capacity, eligibility, or award probability."
            ),
            "material": True,
            "mitigation": (
                "Verify current capacity, qualifications, and pursuit decisions separately."
            ),
        },
    ]

    if comparability != "directional_with_limitations":
        reason_limitations.append(
            {
                "code": "PROFILE_TRANSFER_LIMIT",
                "description": (
                    "The historical dataset was screened for the ICM reference "
                    "profile; use with the fictional profile only to test portability."
                ),
                "material": True,
                "mitigation": (
                    "Do not generalize these counts to a real alternate organization."
                ),
            }
        )

    if not selected_categories or matched_count == 0:
        reason_limitations.append(
            {
                "code": "HISTORICAL_CONTEXT_NOT_COMPARABLE",
                "description": (
                    "No configured historical category is comparable to "
                    "the matched service families for this opportunity."
                ),
                "material": True,
                "mitigation": (
                    "Continue without historical demand context and rely on current evidence."
                ),
            }
        )

    interpretation = (
        f"The frozen Project 2 dataset contains {summary['historical_rows']:,} "
        f"records, including {summary['icm_relevant_rows']} title-classified "
        f"ICM-relevant records. The current alignment maps to "
        f"{matched_count} historical records across "
        f"{len(service_counts)} configured service categories. "
        "This is descriptive directional context only and does not predict "
        "award likelihood, contract value, labor demand, or current capacity."
    )

    result = {
        "context_schema_version": "1.0.0",
        "case_id": opportunity["case_id"],
        "source_period": {
            "start_date": summary["historical_period_start"],
            "end_date": summary["historical_period_end"],
        },
        "source_records": summary["historical_rows"],
        "matched_historical_records": matched_count,
        "service_category_counts": dict(
            sorted(service_counts.items())
        ),
        "staffing_family_counts": dict(
            sorted(staffing_counts.items())
        ),
        "source_asset_checksums": checksums,
        "interpretation": interpretation,
        "limitations": reason_limitations,
    }
    validate_artifact(
        result,
        "historical_context.schema.json",
        schema_dir,
    )
    return result
