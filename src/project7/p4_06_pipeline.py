"""P4-06 audit consolidation and reproducibility pipeline."""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path
from typing import Any

from .audit_utils import build_audit_event
from .reproducibility import (
    build_final_routing,
    canonical_sha256,
    deterministic_packet_replay,
    inventory_artifacts,
    read_json,
    read_jsonl,
    verify_audit_chain,
    verify_inventory,
    write_checksum_csv,
)
from .schema_validation import validate_artifact


def run_reproducibility_pipeline(
    *,
    repo_root: Path,
    output_directory: Path,
    audit_output_directory: Path,
    policy_path: Path,
    event_time: str,
) -> dict[str, Any]:
    policy = read_json(policy_path)
    schema_dir = repo_root / "config" / "schemas"

    prior_audit_paths = [
        repo_root / "audit" / "p4_01_intake_events.jsonl",
        repo_root / "audit" / "p4_02_alignment_history_events.jsonl",
        repo_root / "audit" / "p4_03_clause_triage_event.jsonl",
        repo_root / "audit" / "p4_04_evidence_workflow_events.jsonl",
        repo_root / "audit" / "p4_05_packet_events.jsonl",
    ]
    prior_events = [
        event
        for path in prior_audit_paths
        for event in read_jsonl(path)
    ]
    prior_chain = verify_audit_chain(
        prior_events,
        expected_sequences=list(range(1, 12)),
    )

    inventory = inventory_artifacts(
        repo_root=repo_root,
        included_prefixes=policy[
            "inventory_scope"
        ]["included_prefixes"],
        excluded_patterns=policy[
            "inventory_scope"
        ]["excluded_patterns"],
    )
    artifact_integrity = verify_inventory(
        repo_root=repo_root,
        inventory=inventory,
    )
    repository_state_digest = canonical_sha256(
        [
            {
                "path": item["path"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            }
            for item in inventory
        ]
    )

    packet_path = (
        repo_root
        / "outputs"
        / "p4_05"
        / "decision_support_packet.json"
    )
    case_path = (
        repo_root
        / "outputs"
        / "p4_05"
        / "updated_case_state.json"
    )
    packet = read_json(packet_path)
    case_state = read_json(case_path)

    replay = deterministic_packet_replay(
        repo_root=repo_root,
        preserved_packet_path=packet_path,
        preserved_case_path=case_path,
        event_time=event_time.replace(
            "20:00:00",
            "19:15:00",
        ),
    )
    final_routing = build_final_routing(
        packet=packet,
        case_state=case_state,
    )

    versions = {
        **case_state["organization_context"],
        "reproducibility_policy": "1.0.0",
        "manifest_schema": "1.0.0",
        "audit_schema": "1.0.0",
    }
    event_12 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="reproducibility_manifest_created",
        event_time=event_time,
        sequence=12,
        component="reproducibility_recorder",
        action=(
            "Create a versioned inventory of replay-critical artifacts, "
            "environment dependencies, component versions, and final routing."
        ),
        status="succeeded",
        reason_codes=[
            "REPRODUCIBILITY_MANIFEST_CREATED"
        ],
        input_artifact_ids=[
            f"ART-CASE-{case_state['case_id']}",
            f"ART-DECISION-PACKET-{case_state['case_id']}",
        ],
        output_artifact_ids=[
            f"ART-REPRO-MANIFEST-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "artifact_count": len(inventory),
            "repository_state_digest": repository_state_digest,
            "human_disposition_recorded": False,
            "final_decision_created": False,
            "external_actions_performed": 0,
        },
        previous_event_hash=prior_events[-1]["event_hash"],
    )
    validate_artifact(
        event_12,
        "audit_event.schema.json",
        schema_dir,
    )

    event_13 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="replay_verified",
        event_time=event_time,
        sequence=13,
        component="replay_verifier",
        action=(
            "Verify artifact checksums, the complete audit hash chain, "
            "deterministic final-packet reconstruction, and preserved routing."
        ),
        status="succeeded",
        reason_codes=["REPLAY_VERIFIED"],
        input_artifact_ids=[
            f"ART-REPRO-MANIFEST-{case_state['case_id']}",
            f"ART-DECISION-PACKET-{case_state['case_id']}",
        ],
        output_artifact_ids=[
            f"ART-REPLAY-RESULT-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "artifact_integrity": replay[
                "artifact_integrity"
            ],
            "packet_replay": replay[
                "packet_replay"
            ],
            "final_route": final_routing[
                "case_status"
            ],
            "human_disposition_recorded": False,
            "final_decision_created": False,
            "external_actions_performed": 0,
        },
        previous_event_hash=event_12["event_hash"],
    )
    validate_artifact(
        event_13,
        "audit_event.schema.json",
        schema_dir,
    )

    all_events = prior_events + [event_12, event_13]
    audit_chain = verify_audit_chain(
        all_events,
        expected_sequences=policy[
            "required_audit_event_sequences"
        ],
    )

    dependency_files = [
        {
            "path": item["path"],
            "sha256": item["sha256"],
        }
        for item in inventory
        if item["category"] == "requirements"
    ]
    manifest = {
        "manifest_schema_version": "1.0.0",
        "manifest_id": (
            "REPRO-"
            + case_state["case_id"].replace(
                "CASE-",
                "",
            )
            + "-P4-06"
        ),
        "case_id": case_state["case_id"],
        "created_at": event_time,
        "inventory_scope": policy[
            "inventory_scope"
        ],
        "repository_state_digest": (
            repository_state_digest
        ),
        "artifact_count": len(inventory),
        "artifact_inventory": inventory,
        "component_versions": {
            "opportunity_intake": "1.0.0",
            "organization_alignment": "1.0.0",
            "historical_context": "1.0.0",
            "project4_clause_triage": "1.0.0",
            "evidence_workflow": "1.0.0",
            "recommendation_engine": "1.0.0",
            "decision_support_packet": "1.0.0",
            "reproducibility_pipeline": "1.0.0",
            "organization_profile": case_state[
                "organization_context"
            ]["profile_version"],
            "far_fac": "2026-01",
        },
        "execution_environment": {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "dependency_files": dependency_files,
            "actual_model_dependency": {
                "path": "models/project4/selected_clause_classifier.pt",
                "checkpoint_sha256": (
                    "50a280950d31466d7002578295c64e957"
                    "d144611f5b9731bb059be50e68c6c92"
                ),
                "required_for_full_reexecution": True,
            },
        },
        "audit_chain": audit_chain,
        "replay_plan": {
            "artifact_verification_command": (
                "python scripts/verify_p4_06_reproducibility.py"
            ),
            "deterministic_packet_replay_command": (
                "python tests/run_p4_06_validation.py"
            ),
            "full_pipeline_commands": [
                "python tests/run_p4_01_validation.py",
                "python tests/run_p4_02_validation.py",
                "python tests/run_p4_03_validation.py",
                "python tests/run_p4_04_validation.py",
                "python tests/run_p4_05_validation.py",
                "python tests/run_p4_06_validation.py",
            ],
            "expected_outcomes": [
                "All inventoried artifact hashes and sizes match.",
                "Audit events 1 through 13 form one valid hash chain.",
                "P4-05 replay reproduces the preserved packet and case hashes.",
                "The final route remains awaiting_human_review.",
                "Human disposition and final decision remain null.",
                "External actions remain zero.",
            ],
            "limitations": [
                {
                    "code": (
                        "FULL_REEXECUTION_REQUIRES_MODEL_PACKAGE"
                    ),
                    "description": (
                        "Full P4-03 re-execution requires the committed "
                        "Project 4 checkpoint and companion model files."
                    ),
                    "material": True,
                    "mitigation": (
                        "Run the replay from the complete public repository "
                        "where models/project4 is preserved."
                    ),
                },
                {
                    "code": "GIT_COMMIT_CAPTURE_DEFERRED",
                    "description": (
                        "The package is generated before its GitHub commit, "
                        "so the manifest uses a canonical repository-state "
                        "digest rather than a post-upload commit hash."
                    ),
                    "material": False,
                    "mitigation": (
                        "Record the resulting Git commit during final "
                        "submission manifest preparation."
                    ),
                },
            ],
        },
        "replay_verification": replay,
        "final_routing": final_routing,
        "limitations": [
            {
                "code": "CONTROLLED_CAPSTONE_SCOPE",
                "description": (
                    "The replay demonstrates deterministic controlled-case "
                    "behavior and artifact integrity, not production readiness."
                ),
                "material": True,
                "mitigation": (
                    "Complete production security, scalability, monitoring, "
                    "and operational validation before broader deployment."
                ),
            },
            {
                "code": "HUMAN_DISPOSITION_PENDING",
                "description": (
                    "The case is intentionally incomplete until an authorized "
                    "reviewer records a separate disposition and rationale."
                ),
                "material": True,
                "mitigation": (
                    "Preserve the original recommendation and record the "
                    "authorized human disposition separately."
                ),
            },
        ],
        "final_decision": None,
        "external_actions_performed": 0,
        "production_boundary": policy[
            "production_boundary"
        ],
    }
    validate_artifact(
        manifest,
        "reproducibility_manifest.schema.json",
        schema_dir,
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        output_directory
        / "reproducibility_manifest.json"
    ).write_text(
        json.dumps(
            manifest,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (
        output_directory
        / "audit_chain_summary.json"
    ).write_text(
        json.dumps(
            audit_chain,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (
        output_directory
        / "replay_verification.json"
    ).write_text(
        json.dumps(
            replay,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (
        output_directory
        / "final_routing_record.json"
    ).write_text(
        json.dumps(
            {
                **final_routing,
                "human_review_required": True,
                "original_recommendation_immutable": True,
                "external_actions_performed": 0,
                "production_boundary": policy[
                    "production_boundary"
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (
        output_directory
        / "replay_plan.json"
    ).write_text(
        json.dumps(
            manifest["replay_plan"],
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    (
        audit_output_directory
        / "p4_06_reproducibility_events.jsonl"
    ).write_text(
        "".join(
            json.dumps(event, ensure_ascii=False)
            + "\n"
            for event in [event_12, event_13]
        ),
        encoding="utf-8",
    )
    (
        audit_output_directory
        / "p4_06_consolidated_case_ledger.jsonl"
    ).write_text(
        "".join(
            json.dumps(event, ensure_ascii=False)
            + "\n"
            for event in all_events
        ),
        encoding="utf-8",
    )
    write_checksum_csv(
        audit_output_directory
        / "p4_06_artifact_checksums.csv",
        inventory,
    )

    return {
        "manifest": manifest,
        "audit_events": [event_12, event_13],
        "consolidated_events": all_events,
        "artifact_integrity": artifact_integrity,
        "replay": replay,
        "final_routing": final_routing,
    }
