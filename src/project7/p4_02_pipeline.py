"""P4-02 profile, alignment, and historical-context pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit_utils import build_audit_event
from .historical_context import attach_historical_context
from .profile_loader import load_organization_profile
from .schema_validation import validate_artifact
from .service_alignment import assess_service_alignment


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_alignment_and_history(
    *,
    repo_root: Path,
    case_state_path: Path,
    profile_path: Path,
    output_directory: Path,
    audit_output_path: Path,
    event_time: str,
) -> dict[str, Any]:
    """Run configuration loading, alignment, and historical context."""

    schema_dir = repo_root / "config" / "schemas"
    case_state = _load_json(case_state_path)
    profile_bundle = load_organization_profile(
        profile_path,
        schema_dir=schema_dir,
    )
    alignment_policy = _load_json(
        repo_root / "config" / "system"
        / "service_alignment_policy.json"
    )
    historical_policy = _load_json(
        repo_root / "config" / "system"
        / "historical_context_policy.json"
    )

    alignment = assess_service_alignment(
        case_state["opportunity"],
        profile_bundle,
        alignment_policy,
        schema_dir=schema_dir,
    )
    historical_context = attach_historical_context(
        repo_root=repo_root,
        opportunity=case_state["opportunity"],
        service_alignment=alignment,
        organization_id=profile_bundle.profile["organization_id"],
        policy=historical_policy,
        schema_dir=schema_dir,
    )

    prior_audit_path = repo_root / "audit" / "p4_01_intake_events.jsonl"
    prior_events = [
        json.loads(line)
        for line in prior_audit_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    previous_hash = prior_events[-1]["event_hash"]

    versions = profile_bundle.organization_context
    event_3 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="configuration_loaded",
        event_time=event_time,
        sequence=3,
        component="profile_loader",
        action=(
            "Load and validate active organization profile "
            "and referenced configuration."
        ),
        status="succeeded",
        reason_codes=[],
        input_artifact_ids=[
            f"ART-PROFILE-{profile_bundle.profile['organization_id']}"
        ],
        output_artifact_ids=[
            f"ART-CONFIG-BUNDLE-{profile_bundle.profile['organization_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "organization_id": profile_bundle.profile["organization_id"],
            "active_capabilities": len(
                profile_bundle.service_catalog
            ),
            "active_service_families": len(
                {
                    row["service_family_id"]
                    for row in profile_bundle.service_catalog
                }
            ),
            "fictional_profile": profile_bundle.profile["fictional"],
        },
        previous_event_hash=previous_hash,
    )
    event_4 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="alignment_completed",
        event_time=event_time,
        sequence=4,
        component="service_alignment_engine",
        action=(
            "Apply exclusion-first configuration-driven "
            "service alignment."
        ),
        status=(
            "warned"
            if alignment["alignment_label"]
            in {"weak_alignment", "no_alignment", "insufficient_information"}
            else "succeeded"
        ),
        reason_codes=alignment["reason_codes"],
        input_artifact_ids=[
            f"ART-OPPORTUNITY-{case_state['opportunity']['record_key'].upper()}",
            f"ART-CONFIG-BUNDLE-{profile_bundle.profile['organization_id']}",
        ],
        output_artifact_ids=[
            f"ART-ALIGNMENT-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "alignment_score": alignment["alignment_score"],
            "alignment_label": alignment["alignment_label"],
            "matched_capability_count": len(
                alignment["matched_capabilities"]
            ),
            "excluded_match_count": len(
                alignment["excluded_matches"]
            ),
            "award_probability_calculated": False,
        },
        previous_event_hash=event_3["event_hash"],
    )
    event_5 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="historical_context_attached",
        event_time=event_time,
        sequence=5,
        component="historical_context_provider",
        action=(
            "Attach checksum-verified descriptive "
            "historical procurement context."
        ),
        status=(
            "warned"
            if historical_context["matched_historical_records"] == 0
            else "succeeded"
        ),
        reason_codes=[
            "HISTORICAL_CONTEXT_DESCRIPTIVE_ONLY"
        ],
        input_artifact_ids=[
            f"ART-ALIGNMENT-{case_state['case_id']}",
            "ART-PROJECT2-HISTORICAL-AGGREGATES",
        ],
        output_artifact_ids=[
            f"ART-HISTORICAL-CONTEXT-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "source_records": historical_context["source_records"],
            "matched_historical_records": (
                historical_context["matched_historical_records"]
            ),
            "descriptive_only": True,
            "award_probability_calculated": False,
            "capacity_estimated": False,
        },
        previous_event_hash=event_4["event_hash"],
    )

    updated_case = {
        **case_state,
        "case_status": "analysis_in_progress",
        "updated_at": event_time,
        "organization_context": versions,
        "service_alignment": alignment,
        "historical_context": historical_context,
        "audit_event_ids": (
            case_state["audit_event_ids"]
            + [
                event_3["event_id"],
                event_4["event_id"],
                event_5["event_id"],
            ]
        ),
    }

    for event in [event_3, event_4, event_5]:
        validate_artifact(
            event,
            "audit_event.schema.json",
            schema_dir,
        )
    validate_artifact(
        updated_case,
        "integrated_case_state.schema.json",
        schema_dir,
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)

    artifacts = {
        "service_alignment": alignment,
        "historical_context": historical_context,
        "updated_case_state": updated_case,
        "audit_events": [event_3, event_4, event_5],
    }

    (output_directory / "service_alignment.json").write_text(
        json.dumps(alignment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_directory / "historical_context.json").write_text(
        json.dumps(
            historical_context,
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
            for event in [event_3, event_4, event_5]
        ),
        encoding="utf-8",
    )
    return artifacts
