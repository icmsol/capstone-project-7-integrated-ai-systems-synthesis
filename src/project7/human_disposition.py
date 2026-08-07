"""Authorized human-disposition recording for Project 7.

This module implements the already-committed human-disposition component contract
without changing the original nonbinding recommendation.  It is intentionally
separate from packet assembly so no AI or tool can create the human disposition.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .schema_validation import SchemaValidationError, validate_artifact


class HumanDispositionError(RuntimeError):
    """Raised when an authorized human disposition cannot be recorded safely."""

    def __init__(self, reason_code: str, behavior: str, message: str) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = behavior


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _authorized_role(
    reviewer: dict[str, Any],
    reviewer_roles: dict[str, Any],
) -> bool:
    configured = next(
        (
            item
            for item in reviewer_roles.get("roles", [])
            if item.get("role_id") == reviewer.get("role_id")
        ),
        None,
    )
    if configured is None:
        return False
    if configured.get("role_name") != reviewer.get("role_name"):
        return False
    reviewer_org = reviewer.get("organization_id")
    configured_org = reviewer_roles.get("organization_id")
    if reviewer_org not in (None, configured_org):
        return False
    return True


def _build_human_audit_event(
    *,
    case_id: str,
    event_time: str,
    sequence: int,
    reviewer_identity: str,
    reviewer_role: dict[str, Any],
    disposition: str,
    recommendation_id: str,
    configuration_versions: dict[str, str],
    previous_event_hash: str,
) -> dict[str, Any]:
    event = {
        "audit_schema_version": "1.0.0",
        "event_id": f"AUD-{case_id}-{sequence:02d}",
        "case_id": case_id,
        "event_type": "human_disposition_recorded",
        "event_time": event_time,
        "actor_type": "human",
        "actor_id": reviewer_identity,
        "component": "human_disposition_recorder",
        "action": (
            "Record the authorized human response separately from the original "
            "nonbinding system recommendation."
        ),
        "status": "succeeded",
        "reason_codes": [],
        "input_artifact_ids": [
            f"ART-RECOMMENDATION-{case_id}",
            f"ART-DECISION-PACKET-{case_id}",
        ],
        "output_artifact_ids": [
            f"ART-HUMAN-DISPOSITION-{case_id}",
            f"ART-CASE-{case_id}",
        ],
        "configuration_versions": configuration_versions,
        "sanitized_details": {
            "reviewer_role_id": reviewer_role["role_id"],
            "reviewer_role_name": reviewer_role["role_name"],
            "disposition": disposition,
            "recommendation_id": recommendation_id,
            "original_recommendation_preserved": True,
            "final_human_authority_exercised": True,
            "external_actions_performed": 0,
        },
        "event_hash": "",
        "previous_event_hash": previous_event_hash,
    }
    event["event_hash"] = _sha256_json(
        {
            key: value
            for key, value in event.items()
            if key != "event_hash"
        }
    )
    return event


def record_human_disposition(
    *,
    repo_root: Path,
    case_state_path: Path,
    human_response: dict[str, Any],
    reviewer_identity: str,
    reviewer_roles_path: Path,
    prior_audit_path: Path,
    output_directory: Path,
    audit_output_path: Path,
) -> dict[str, Any]:
    """Validate and record one authorized human disposition.

    The system recommendation is immutable.  This function records the human
    response as a separate artifact, updates case state, appends one human audit
    event, and performs no external action.
    """

    if not reviewer_identity or not reviewer_identity.strip():
        raise HumanDispositionError(
            "REVIEWER_NOT_AUTHORIZED",
            "fail_closed",
            "A non-empty human reviewer identity is required.",
        )

    schema_dir = repo_root / "config" / "schemas"
    case_state = _load_json(case_state_path)
    reviewer_roles = _load_json(reviewer_roles_path)

    if case_state.get("case_status") != "awaiting_human_review":
        raise HumanDispositionError(
            "HUMAN_DECISION_REQUIRED",
            "fail_closed",
            "Human disposition may be recorded only from awaiting_human_review.",
        )

    if case_state.get("human_disposition") is not None:
        raise HumanDispositionError(
            "HUMAN_DECISION_REQUIRED",
            "fail_closed",
            "A human disposition has already been recorded for this case.",
        )

    recommendation = case_state.get("recommendation")
    if not isinstance(recommendation, dict):
        raise HumanDispositionError(
            "HUMAN_DECISION_REQUIRED",
            "fail_closed",
            "A preserved nonbinding recommendation is required before disposition.",
        )

    rationale = human_response.get("rationale")
    if not isinstance(rationale, str) or len(rationale.strip()) < 20:
        raise HumanDispositionError(
            "HUMAN_RATIONALE_MISSING",
            "defer",
            "Human disposition rationale must contain at least 20 characters.",
        )

    if human_response.get("case_id") != case_state.get("case_id"):
        raise HumanDispositionError(
            "HUMAN_DECISION_REQUIRED",
            "fail_closed",
            "Human response case_id does not match the active case.",
        )

    if human_response.get("recommendation_id") != recommendation.get(
        "recommendation_id"
    ):
        raise HumanDispositionError(
            "HUMAN_DECISION_REQUIRED",
            "fail_closed",
            "Human response recommendation_id does not match the preserved recommendation.",
        )

    reviewer = human_response.get("reviewer")
    if not isinstance(reviewer, dict) or not _authorized_role(
        reviewer, reviewer_roles
    ):
        raise HumanDispositionError(
            "REVIEWER_NOT_AUTHORIZED",
            "fail_closed",
            "The reviewer role does not map to an authorized configured role.",
        )

    disposition = human_response.get("disposition")
    if disposition == "escalate":
        escalated_to = human_response.get("escalated_to")
        if not isinstance(escalated_to, dict) or not _authorized_role(
            escalated_to, reviewer_roles
        ):
            raise HumanDispositionError(
                "REVIEWER_NOT_AUTHORIZED",
                "fail_closed",
                "Escalation requires a valid configured human target role.",
            )

    try:
        validate_artifact(
            human_response,
            "human_disposition.schema.json",
            schema_dir,
        )
    except SchemaValidationError as exc:
        raise HumanDispositionError(
            "HUMAN_DECISION_REQUIRED",
            "fail_closed",
            str(exc),
        ) from exc

    prior_events = [
        json.loads(line)
        for line in prior_audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not prior_events:
        raise HumanDispositionError(
            "AUDIT_EVENT_INVALID",
            "fail_closed",
            "P4-05 audit events are required before recording human disposition.",
        )

    expected_prior_event_id = case_state["audit_event_ids"][-1]
    if prior_events[-1].get("event_id") != expected_prior_event_id:
        raise HumanDispositionError(
            "AUDIT_EVENT_INVALID",
            "fail_closed",
            "Prior audit ledger does not continue the active case audit chain.",
        )

    recommendation_before_hash = _sha256_json(recommendation)

    if disposition == "defer_pending_information":
        next_status = "deferred"
    elif disposition == "escalate":
        next_status = "escalated"
    else:
        next_status = "finalized"

    event_sequence = len(case_state["audit_event_ids"]) + 1
    configuration_versions = {
        **case_state["organization_context"],
        "human_disposition_contract": "1.0.0",
    }

    event = _build_human_audit_event(
        case_id=case_state["case_id"],
        event_time=human_response["decided_at"],
        sequence=event_sequence,
        reviewer_identity=reviewer_identity.strip(),
        reviewer_role=reviewer,
        disposition=disposition,
        recommendation_id=recommendation["recommendation_id"],
        configuration_versions=configuration_versions,
        previous_event_hash=prior_events[-1]["event_hash"],
    )
    validate_artifact(
        event,
        "audit_event.schema.json",
        schema_dir,
    )

    updated_case = {
        **case_state,
        "case_status": next_status,
        "updated_at": human_response["decided_at"],
        "human_disposition": human_response,
        "audit_event_ids": case_state["audit_event_ids"] + [event["event_id"]],
    }

    if _sha256_json(updated_case["recommendation"]) != recommendation_before_hash:
        raise HumanDispositionError(
            "RECOMMENDATION_UNSUPPORTED",
            "fail_closed",
            "The original system recommendation changed during human disposition recording.",
        )

    validate_artifact(
        updated_case,
        "integrated_case_state.schema.json",
        schema_dir,
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)

    disposition_path = output_directory / "human_disposition.json"
    updated_case_path = output_directory / "updated_case_state.json"

    disposition_path.write_text(
        json.dumps(human_response, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    updated_case_path.write_text(
        json.dumps(updated_case, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if next_status == "finalized":
        (output_directory / "finalized_case_state.json").write_text(
            json.dumps(updated_case, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    audit_output_path.write_text(
        json.dumps(event, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return {
        "human_disposition": human_response,
        "updated_case_state": updated_case,
        "audit_event": event,
        "recommendation_unchanged": True,
        "external_actions_performed": 0,
    }
