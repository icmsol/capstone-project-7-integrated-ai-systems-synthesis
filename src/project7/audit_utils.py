"""Audit-event utilities for the integrated prototype."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_audit_event(
    *,
    case_id: str,
    event_type: str,
    event_time: str,
    sequence: int,
    component: str,
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
        "component": component,
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
    event["event_hash"] = _sha256_bytes(
        _canonical_json_bytes(
            {
                key: value
                for key, value in event.items()
                if key != "event_hash"
            }
        )
    )
    return event
