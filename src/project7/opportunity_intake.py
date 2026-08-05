"""Deterministic opportunity intake, normalization, and provenance.

This component implements P4-01 of Project 7. It is intentionally bounded:
it validates and normalizes one opportunity, creates an initial case state,
and produces two append-only audit events. It does not assess business fit,
predict award likelihood, generate recommendations, or take external action.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schema_validation import SchemaValidationError, validate_artifact


PRODUCTION_BOUNDARY = (
    "Controlled capstone prototype; nonbinding recommendations only; "
    "no autonomous external action; final human authority required."
)

ALLOWED_SOURCE_TYPES = {
    "public_web",
    "public_file",
    "frozen_snapshot",
    "synthetic",
    "deidentified",
    "authorized_internal",
}

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


class IntakeError(RuntimeError):
    """Fail-closed intake exception with a stable reason code."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        behavior: str = "fail_closed",
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = behavior


@dataclass(frozen=True)
class IntakeResult:
    """Validated output bundle for one opportunity intake."""

    normalized_opportunity: dict[str, Any]
    initial_case_state: dict[str, Any]
    audit_events: list[dict[str, Any]]


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _stable_suffix(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def _utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")


def _parse_datetime(
    value: Any,
    accepted_formats: list[str],
) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return None

    cleaned = value.strip()
    try:
        parsed = datetime.fromisoformat(
            cleaned.replace("Z", "+00:00")
        )
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return _utc_iso(parsed)
    except ValueError:
        pass

    for date_format in accepted_formats:
        try:
            parsed = datetime.strptime(cleaned, date_format)
            parsed = parsed.replace(tzinfo=timezone.utc)
            return _utc_iso(parsed)
        except ValueError:
            continue
    return None


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split())
    return cleaned or None


def _normalize_status(
    value: Any,
    status_map: dict[str, str],
) -> str:
    if value is None:
        return "unknown"
    key = " ".join(str(value).lower().split())
    return status_map.get(key, "unknown")


def _fiscal_period(
    posted_at: str | None,
    due_at: str | None,
) -> tuple[str | None, str | None]:
    value = posted_at or due_at
    if value is None:
        return None, None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    quarter = ((parsed.month - 1) // 3) + 1
    return str(parsed.year), f"Q{quarter}"


def _detect_secret(raw_bytes: bytes) -> bool:
    text = raw_bytes.decode("utf-8", errors="replace")
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def _validate_source(
    source_approval: dict[str, Any],
    raw_source_bytes: bytes,
) -> None:
    if not source_approval.get("approved_for_use"):
        raise IntakeError(
            "SOURCE_NOT_APPROVED",
            "The source is not approved for use.",
            "fail_closed",
        )

    approval_basis = source_approval.get("approval_basis")
    if not isinstance(approval_basis, str) or not approval_basis.strip():
        raise IntakeError(
            "SOURCE_NOT_APPROVED",
            "The source approval basis is absent.",
            "fail_closed",
        )

    if source_approval.get("source_type") not in ALLOWED_SOURCE_TYPES:
        raise IntakeError(
            "SOURCE_NOT_APPROVED",
            "The source type is not permitted for opportunity intake.",
            "fail_closed",
        )

    required_metadata = [
        "source_id",
        "source_location",
        "retrieved_at",
    ]
    missing = [
        field
        for field in required_metadata
        if not source_approval.get(field)
    ]
    if missing:
        raise IntakeError(
            "REQUIRED_SOURCE_METADATA_MISSING",
            "Required source metadata is missing: "
            + ", ".join(missing),
            "defer",
        )

    expected_sha = source_approval.get("sha256")
    if not expected_sha:
        raise IntakeError(
            "SOURCE_CHECKSUM_MISSING",
            "The source checksum is missing.",
            "defer",
        )

    observed_sha = _sha256_bytes(raw_source_bytes)
    if expected_sha != observed_sha:
        raise IntakeError(
            "SOURCE_VERSION_CHANGED",
            "The source bytes do not match the approved checksum.",
            "defer",
        )

    if _detect_secret(raw_source_bytes):
        raise IntakeError(
            "SECRET_VALUE_DETECTED",
            "A credential-like value was detected in the source.",
            "fail_closed",
        )


def _build_audit_event(
    *,
    case_id: str,
    event_type: str,
    event_time: str,
    sequence: int,
    action: str,
    status: str,
    reason_codes: list[str],
    input_artifact_ids: list[str],
    output_artifact_ids: list[str],
    configuration_versions: dict[str, str],
    sanitized_details: dict[str, Any],
    previous_event_hash: str | None,
) -> dict[str, Any]:
    event_id = f"AUD-{case_id}-{sequence:02d}"
    event = {
        "audit_schema_version": "1.0.0",
        "event_id": event_id,
        "case_id": case_id,
        "event_type": event_type,
        "event_time": event_time,
        "actor_type": "system",
        "actor_id": "PROJECT7-INTEGRATED-SYSTEM",
        "component": "case_intake_normalizer",
        "action": action,
        "status": status,
        "reason_codes": reason_codes,
        "input_artifact_ids": input_artifact_ids,
        "output_artifact_ids": output_artifact_ids,
        "configuration_versions": configuration_versions,
        "sanitized_details": sanitized_details,
        "event_hash": "",
        "previous_event_hash": previous_event_hash,
    }
    hash_payload = {
        key: value
        for key, value in event.items()
        if key != "event_hash"
    }
    event["event_hash"] = _sha256_bytes(
        _canonical_json_bytes(hash_payload)
    )
    return event


def normalize_opportunity(
    raw_opportunity: dict[str, Any],
    source_approval: dict[str, Any],
    organization_context: dict[str, Any],
    normalization_rules: dict[str, Any],
    *,
    schema_dir: Path,
    raw_source_bytes: bytes | None = None,
    event_time: str | None = None,
) -> IntakeResult:
    """Normalize one approved source and return validated intake artifacts."""

    if raw_source_bytes is None:
        raw_source_bytes = _canonical_json_bytes(raw_opportunity)

    _validate_source(source_approval, raw_source_bytes)

    event_time = event_time or _utc_iso(
        datetime.now(timezone.utc)
    )
    normalization_version = normalization_rules[
        "normalization_version"
    ]
    accepted_formats = normalization_rules["accepted_date_formats"]
    status_map = normalization_rules["status_map"]

    title = _normalize_text(raw_opportunity.get("title"))
    agency = _normalize_text(raw_opportunity.get("agency"))
    solicitation_id = _normalize_text(
        raw_opportunity.get("solicitation_id")
    )
    source_portal = _normalize_text(
        raw_opportunity.get("source_portal")
    )
    jurisdiction = _normalize_text(
        raw_opportunity.get("jurisdiction")
    )

    required_identifiers = {
        "title": title,
        "agency": agency,
        "solicitation_id": solicitation_id,
        "source_portal": source_portal,
        "jurisdiction": jurisdiction,
    }
    missing_identifiers = [
        field
        for field, value in required_identifiers.items()
        if value is None
    ]
    if missing_identifiers:
        raise IntakeError(
            "NORMALIZATION_FAILED",
            "Required opportunity identifiers are missing: "
            + ", ".join(missing_identifiers),
            "fail_closed",
        )

    posted_at = _parse_datetime(
        raw_opportunity.get("posted_at"),
        accepted_formats,
    )
    due_at = _parse_datetime(
        raw_opportunity.get("due_at"),
        accepted_formats,
    )
    description = _normalize_text(
        raw_opportunity.get("description")
    )

    tracked_optional_fields = normalization_rules[
        "tracked_optional_fields"
    ]
    missing_fields = []
    normalized_optional_values = {
        "description": description,
        "posted_at": posted_at,
        "due_at": due_at,
        "place_of_performance": _normalize_text(
            raw_opportunity.get("place_of_performance")
        ),
        "procurement_method": _normalize_text(
            raw_opportunity.get("procurement_method")
        ),
        "contract_vehicle": _normalize_text(
            raw_opportunity.get("contract_vehicle")
        ),
    }
    for field in tracked_optional_fields:
        if normalized_optional_values.get(field) is None:
            missing_fields.append(field)

    source_sha = source_approval["sha256"]
    identity_seed = (
        f"{source_sha}|{normalization_version}|"
        f"{agency}|{solicitation_id}"
    )
    record_key = _stable_suffix(identity_seed, 20)
    case_id = f"CASE-{_stable_suffix(identity_seed, 16).upper()}"
    opportunity_id = (
        f"OPP-{_stable_suffix(identity_seed + '|OPP', 16).upper()}"
    )

    fiscal_year, fiscal_quarter = _fiscal_period(
        posted_at,
        due_at,
    )

    limitations = []
    if missing_fields:
        limitations.append(
            {
                "code": "STRUCTURED_ANALYSIS_INSUFFICIENT",
                "description": (
                    "The source omits optional fields needed for "
                    "complete downstream screening: "
                    + ", ".join(missing_fields)
                ),
                "material": True,
                "mitigation": (
                    "Request the missing information before relying on "
                    "downstream alignment or recommendation outputs."
                ),
            }
        )

    normalized = {
        "record_schema_version": "1.0.0",
        "opportunity_id": opportunity_id,
        "case_id": case_id,
        "source": {
            "source_id": source_approval["source_id"],
            "source_type": source_approval["source_type"],
            "source_location": source_approval["source_location"],
            "retrieved_at": source_approval["retrieved_at"],
            "snapshot_date": source_approval.get("snapshot_date"),
            "sha256": source_sha,
            "approved_for_use": True,
            "approval_basis": source_approval["approval_basis"],
            "notes": source_approval.get("notes"),
        },
        "source_portal": source_portal,
        "jurisdiction": jurisdiction,
        "agency": agency,
        "solicitation_id": solicitation_id,
        "title": title,
        "normalized_title": title.lower(),
        "description": description,
        "status": _normalize_status(
            raw_opportunity.get("status"),
            status_map,
        ),
        "posted_at": posted_at,
        "due_at": due_at,
        "fiscal_year": fiscal_year,
        "fiscal_quarter": fiscal_quarter,
        "place_of_performance": (
            normalized_optional_values["place_of_performance"]
        ),
        "procurement_method": (
            normalized_optional_values["procurement_method"]
        ),
        "contract_vehicle": (
            normalized_optional_values["contract_vehicle"]
        ),
        "estimated_value": raw_opportunity.get("estimated_value"),
        "ingested_at": event_time,
        "normalization_version": normalization_version,
        "record_key": record_key,
        "original_values": raw_opportunity,
        "missing_fields": sorted(set(missing_fields)),
        "data_freshness_days": raw_opportunity.get(
            "data_freshness_days"
        ),
        "limitations": limitations,
    }

    raw_artifact_id = f"ART-RAW-{record_key.upper()}"
    opportunity_artifact_id = (
        f"ART-OPPORTUNITY-{record_key.upper()}"
    )
    case_artifact_id = f"ART-CASE-{record_key.upper()}"

    configuration_versions = {
        "normalization_rules": normalization_version,
        "record_key_version": normalization_rules[
            "record_key_version"
        ],
        "organization_profile": organization_context[
            "profile_version"
        ],
        "fixed_safeguards": organization_context[
            "fixed_safeguards_version"
        ],
    }

    event_1 = _build_audit_event(
        case_id=case_id,
        event_type="case_created",
        event_time=event_time,
        sequence=1,
        action="Create deterministic opportunity case.",
        status="succeeded",
        reason_codes=[],
        input_artifact_ids=[raw_artifact_id],
        output_artifact_ids=[case_artifact_id],
        configuration_versions=configuration_versions,
        sanitized_details={
            "source_id": source_approval["source_id"],
            "record_key": record_key,
            "no_external_action": True,
        },
        previous_event_hash=None,
    )
    event_2 = _build_audit_event(
        case_id=case_id,
        event_type="source_ingested",
        event_time=event_time,
        sequence=2,
        action=(
            "Validate source provenance and normalize opportunity."
        ),
        status=(
            "warned" if missing_fields else "succeeded"
        ),
        reason_codes=(
            ["STRUCTURED_ANALYSIS_INSUFFICIENT"]
            if missing_fields else []
        ),
        input_artifact_ids=[raw_artifact_id],
        output_artifact_ids=[opportunity_artifact_id],
        configuration_versions=configuration_versions,
        sanitized_details={
            "source_sha256": source_sha,
            "missing_fields": sorted(set(missing_fields)),
            "original_values_retained": True,
            "material_values_inferred": False,
        },
        previous_event_hash=event_1["event_hash"],
    )

    case_state = {
        "case_schema_version": "1.0.0",
        "case_id": case_id,
        "case_status": "intake_validated",
        "created_at": event_time,
        "updated_at": event_time,
        "organization_context": organization_context,
        "opportunity": normalized,
        "service_alignment": None,
        "historical_context": None,
        "clause_predictions": [],
        "evidence_items": [],
        "evidence_assessments": [],
        "recommendation": None,
        "human_disposition": None,
        "audit_event_ids": [
            event_1["event_id"],
            event_2["event_id"],
        ],
        "processing_errors": [],
        "production_boundary": PRODUCTION_BOUNDARY,
    }

    try:
        validate_artifact(
            normalized,
            "opportunity_record.schema.json",
            schema_dir,
        )
        validate_artifact(
            event_1,
            "audit_event.schema.json",
            schema_dir,
        )
        validate_artifact(
            event_2,
            "audit_event.schema.json",
            schema_dir,
        )
        validate_artifact(
            case_state,
            "integrated_case_state.schema.json",
            schema_dir,
        )
    except SchemaValidationError as exc:
        raise IntakeError(
            "NORMALIZATION_FAILED",
            str(exc),
            "fail_closed",
        ) from exc

    return IntakeResult(
        normalized_opportunity=normalized,
        initial_case_state=case_state,
        audit_events=[event_1, event_2],
    )


def run_intake_from_files(
    *,
    repo_root: Path,
    raw_opportunity_path: Path,
    source_approval_path: Path,
    organization_context_path: Path,
    normalization_rules_path: Path,
    output_directory: Path,
    audit_output_path: Path,
    event_time: str | None = None,
) -> IntakeResult:
    """Execute intake from repository files and persist validated outputs."""

    raw_bytes = raw_opportunity_path.read_bytes()
    raw_opportunity = json.loads(raw_bytes.decode("utf-8"))
    source_approval = json.loads(
        source_approval_path.read_text(encoding="utf-8")
    )
    organization_context = json.loads(
        organization_context_path.read_text(encoding="utf-8")
    )
    normalization_rules = json.loads(
        normalization_rules_path.read_text(encoding="utf-8")
    )

    result = normalize_opportunity(
        raw_opportunity,
        source_approval,
        organization_context,
        normalization_rules,
        schema_dir=repo_root / "config" / "schemas",
        raw_source_bytes=raw_bytes,
        event_time=event_time,
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        output_directory / "normalized_opportunity.json"
    ).write_text(
        json.dumps(
            result.normalized_opportunity,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (
        output_directory / "initial_case_state.json"
    ).write_text(
        json.dumps(
            result.initial_case_state,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    audit_output_path.write_text(
        "".join(
            json.dumps(event, ensure_ascii=False) + "\n"
            for event in result.audit_events
        ),
        encoding="utf-8",
    )
    return result
