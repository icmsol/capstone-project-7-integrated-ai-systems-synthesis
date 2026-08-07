"""P4-05 integrated packet assembly pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit_utils import build_audit_event
from .decision_support_packet import (
    assemble_decision_support_packet,
    render_packet_markdown,
)
from .recommendation_engine import (
    create_nonbinding_recommendation,
)
from .schema_validation import validate_artifact


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_packet_assembly(
    *,
    repo_root: Path,
    case_state_path: Path,
    output_directory: Path,
    audit_output_path: Path,
    event_time: str,
    prior_audit_path: Path | None = None,
) -> dict[str, Any]:
    schema_dir = repo_root / "config" / "schemas"
    case_state = _load_json(case_state_path)
    recommendation_policy = _load_json(
        repo_root / "config" / "system"
        / "recommendation_policy.json"
    )
    packet_policy = _load_json(
        repo_root / "config" / "system"
        / "decision_support_packet_policy.json"
    )

    prior_audit_path = (
        prior_audit_path
        if prior_audit_path is not None
        else repo_root / "audit" / "p4_04_evidence_workflow_events.jsonl"
    )
    prior_events = [
        json.loads(line)
        for line in prior_audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not prior_events:
        raise RuntimeError(
            "P4-04 audit events are required before packet assembly."
        )
    previous_hash = prior_events[-1]["event_hash"]

    event_10_id = (
        f"AUD-{case_state['case_id']}-10"
    )
    recommendation = create_nonbinding_recommendation(
        case_state=case_state,
        policy=recommendation_policy,
        schema_dir=schema_dir,
        audit_reference=event_10_id,
        created_at=event_time,
    )

    versions = {
        **case_state["organization_context"],
        "recommendation_policy": "1.0.0",
        "packet_policy": "1.0.0",
    }
    event_10 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="recommendation_created",
        event_time=event_time,
        sequence=10,
        component="recommendation_engine",
        action=(
            "Create a nonbinding recommendation from completed component "
            "outputs and preserve required limitations and human-review routing."
        ),
        status="warned",
        reason_codes=recommendation["reason_codes"],
        input_artifact_ids=[
            f"ART-CASE-{case_state['case_id']}",
            f"ART-EVIDENCE-ASSESSMENTS-{case_state['case_id']}",
        ],
        output_artifact_ids=[
            f"ART-RECOMMENDATION-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "recommendation_code": recommendation[
                "recommendation_code"
            ],
            "recommendation_label": recommendation[
                "recommendation_label"
            ],
            "supporting_evidence_count": len(
                recommendation["supporting_evidence_ids"]
            ),
            "nonbinding": True,
            "final_decision_created": False,
            "external_actions_performed": 0,
        },
        previous_event_hash=previous_hash,
    )
    validate_artifact(
        event_10,
        "audit_event.schema.json",
        schema_dir,
    )

    event_11 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="case_escalated",
        event_time=event_time,
        sequence=11,
        component="packet_assembler",
        action=(
            "Assemble the integrated human decision-support packet and "
            "route it to the required authorized reviewer."
        ),
        status="warned",
        reason_codes=[
            "PACKET_READY_FOR_HUMAN_REVIEW",
            "HUMAN_DISPOSITION_PENDING",
            "HUMAN_REVIEW_REQUIRED",
        ],
        input_artifact_ids=[
            f"ART-RECOMMENDATION-{case_state['case_id']}",
            f"ART-CASE-{case_state['case_id']}",
        ],
        output_artifact_ids=[
            f"ART-DECISION-PACKET-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "required_reviewer": recommendation[
                "required_human_reviewer"
            ]["role_name"],
            "packet_status": "ready_for_human_review",
            "human_disposition_recorded": False,
            "final_decision_created": False,
            "external_actions_performed": 0,
        },
        previous_event_hash=event_10["event_hash"],
    )
    validate_artifact(
        event_11,
        "audit_event.schema.json",
        schema_dir,
    )

    packet_id = (
        "PACKET-" + case_state["case_id"].replace(
            "CASE-", ""
        ) + "-P4-05"
    )
    packet = assemble_decision_support_packet(
        case_state=case_state,
        recommendation=recommendation,
        packet_policy=packet_policy,
        schema_dir=schema_dir,
        packet_id=packet_id,
        generated_at=event_time,
        audit_event_ids=[
            event_10["event_id"],
            event_11["event_id"],
        ],
    )
    markdown = render_packet_markdown(packet)

    updated_case = {
        **case_state,
        "case_status": "awaiting_human_review",
        "updated_at": event_time,
        "recommendation": recommendation,
        "human_disposition": None,
        "audit_event_ids": (
            case_state["audit_event_ids"]
            + [event_10["event_id"], event_11["event_id"]]
        ),
    }
    validate_artifact(
        updated_case,
        "integrated_case_state.schema.json",
        schema_dir,
    )

    disposition_template = {
        "template_schema_version": "1.0.0",
        "status": "pending",
        "case_id": case_state["case_id"],
        "recommendation_id": recommendation[
            "recommendation_id"
        ],
        "required_reviewer": recommendation[
            "required_human_reviewer"
        ],
        "allowed_dispositions": packet_policy[
            "allowed_human_dispositions"
        ],
        "required_fields": [
            "disposition_id",
            "reviewer",
            "disposition",
            "rationale",
            "modified_conditions",
            "decided_at",
        ],
        "human_disposition_schema": (
            "config/schemas/human_disposition.schema.json"
        ),
        "instructions": (
            "Complete only after authorized review. Preserve the original "
            "system recommendation and record the human disposition separately."
        ),
        "external_actions_performed": 0,
    }

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)

    (output_directory / "recommendation.json").write_text(
        json.dumps(
            recommendation,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_directory / "decision_support_packet.json").write_text(
        json.dumps(
            packet,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_directory / "decision_support_packet.md").write_text(
        markdown,
        encoding="utf-8",
    )
    (output_directory / "human_disposition_template.json").write_text(
        json.dumps(
            disposition_template,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_directory / "updated_case_state.json").write_text(
        json.dumps(
            updated_case,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    audit_output_path.write_text(
        "".join(
            json.dumps(event, ensure_ascii=False) + "\n"
            for event in [event_10, event_11]
        ),
        encoding="utf-8",
    )

    return {
        "recommendation": recommendation,
        "packet": packet,
        "updated_case_state": updated_case,
        "audit_events": [event_10, event_11],
        "human_disposition_template": disposition_template,
    }
