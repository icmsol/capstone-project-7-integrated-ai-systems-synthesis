"""Configuration-driven organization profile loader."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .schema_validation import validate_artifact


class ProfileLoadError(RuntimeError):
    """Fail-closed profile loading error."""

    def __init__(self, reason_code: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = "fail_closed"


@dataclass(frozen=True)
class OrganizationProfileBundle:
    """Validated active profile and its referenced artifacts."""

    profile: dict[str, Any]
    service_catalog: list[dict[str, str]]
    opportunity_rules: dict[str, Any]
    staffing_map: list[dict[str, str]]
    reviewer_roles: dict[str, Any]
    recommendation_thresholds: dict[str, Any]
    fixed_safeguards: dict[str, Any]

    @property
    def organization_context(self) -> dict[str, str]:
        return {
            "organization_id": self.profile["organization_id"],
            "organization_name": self.profile["organization_name"],
            "profile_version": self.profile["profile_version"],
            "service_catalog_version": (
                self.service_catalog[0]["profile_version"]
            ),
            "rules_version": self.opportunity_rules[
                "artifact_version"
            ],
            "reviewer_roles_version": self.reviewer_roles[
                "artifact_version"
            ],
            "thresholds_version": self.recommendation_thresholds[
                "artifact_version"
            ],
            "fixed_safeguards_version": self.fixed_safeguards[
                "artifact_version"
            ],
        }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


def _resolve(profile_dir: Path, relative_path: str) -> Path:
    path = (profile_dir / relative_path).resolve()
    if not path.exists():
        raise ProfileLoadError(
            "CONFIG_FILE_MISSING",
            f"Referenced configuration file is missing: {path}",
        )
    return path


def load_organization_profile(
    profile_path: Path,
    *,
    schema_dir: Path,
) -> OrganizationProfileBundle:
    """Load one organization profile without hard-coded company logic."""

    profile_path = profile_path.resolve()
    profile_dir = profile_path.parent
    profile = _load_json(profile_path)

    validate_artifact(
        profile,
        "organization_profile.schema.json",
        schema_dir,
    )

    service_catalog = _load_csv(
        _resolve(profile_dir, profile["service_catalog_file"])
    )
    opportunity_rules = _load_json(
        _resolve(profile_dir, profile["opportunity_rules_file"])
    )
    staffing_map = _load_csv(
        _resolve(profile_dir, profile["staffing_map_file"])
    )
    reviewer_roles = _load_json(
        _resolve(profile_dir, profile["reviewer_roles_file"])
    )
    recommendation_thresholds = _load_json(
        _resolve(
            profile_dir,
            profile["recommendation_thresholds_file"],
        )
    )
    fixed_safeguards = _load_json(
        _resolve(profile_dir, profile["fixed_safeguards_file"])
    )

    organization_id = profile["organization_id"]
    active_capabilities = [
        row
        for row in service_catalog
        if row.get("active", "").strip().upper() == "TRUE"
    ]
    if not active_capabilities:
        raise ProfileLoadError(
            "SERVICE_CATALOG_EMPTY",
            "No active capabilities exist in the profile.",
        )

    for row in active_capabilities:
        if row.get("organization_id") != organization_id:
            raise ProfileLoadError(
                "CONFIG_ORGANIZATION_MISMATCH",
                "Service catalog organization does not match profile.",
            )
        if row.get("profile_version") != profile["profile_version"]:
            raise ProfileLoadError(
                "CONFIG_VERSION_MISMATCH",
                "Service catalog profile version does not match profile.",
            )

    for artifact, label in [
        (opportunity_rules, "opportunity rules"),
        (reviewer_roles, "reviewer roles"),
        (recommendation_thresholds, "recommendation thresholds"),
    ]:
        if artifact.get("organization_id") != organization_id:
            raise ProfileLoadError(
                "CONFIG_ORGANIZATION_MISMATCH",
                f"{label} organization does not match profile.",
            )

    if fixed_safeguards.get(
        "ordinary_profile_override_permitted"
    ):
        raise ProfileLoadError(
            "SAFEGUARD_OVERRIDE_ATTEMPT",
            "Profile loading rejected safeguards that permit ordinary override.",
        )

    return OrganizationProfileBundle(
        profile=profile,
        service_catalog=active_capabilities,
        opportunity_rules=opportunity_rules,
        staffing_map=[
            row
            for row in staffing_map
            if row.get("active", "").strip().upper() == "TRUE"
        ],
        reviewer_roles=reviewer_roles,
        recommendation_thresholds=recommendation_thresholds,
        fixed_safeguards=fixed_safeguards,
    )
