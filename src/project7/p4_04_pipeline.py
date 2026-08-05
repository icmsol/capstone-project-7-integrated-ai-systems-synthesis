"""P4-04 integrated evidence-grounded workflow pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit_utils import build_audit_event
from .evidence_workflow import EvidenceGroundedAgentWorkflow
from .schema_validation import validate_artifact


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_evidence_workflow(
    *,
    repo_root: Path,
    case_state_path: Path,
    requests_path: Path,
    output_directory: Path,
    audit_output_path: Path,
    tool_trace_output_path: Path,
    event_time: str,
) -> dict[str, Any]:
    schema_dir = repo_root / "config" / "schemas"
    case_state = _load_json(case_state_path)
    request_set = _load_json(requests_path)

    workflow = EvidenceGroundedAgentWorkflow(
        repo_root=repo_root,
        schema_dir=schema_dir,
        policy_path=(
            repo_root / "config" / "system"
            / "evidence_workflow_policy.json"
        ),
        corpus_registry_path=(
            repo_root / "config" / "system"
            / "evidence_corpus_registry.json"
        ),
    )

    upstream_reason_codes = sorted(
        {
            reason
            for prediction in case_state["clause_predictions"]
            for reason in prediction["reason_codes"]
        }
    )
    results = [
        workflow.run(
            request,
            upstream_reason_codes=upstream_reason_codes,
        ).result
        for request in request_set["requests"]
    ]

    evidence_by_id = {}
    assessments = []
    for result in results:
        for item in result["evidence_items"]:
            evidence_by_id[item["evidence_id"]] = item
        assessments.append(result["assessment"])

    prior_event_path = (
        repo_root / "audit"
        / "p4_03_clause_triage_event.jsonl"
    )
    prior_events = [
        json.loads(line)
        for line in prior_event_path.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    if not prior_events:
        raise RuntimeError(
            "P4-03 audit event is required before P4-04."
        )
    previous_hash = prior_events[-1]["event_hash"]

    versions = {
        **case_state["organization_context"],
        "evidence_workflow_policy": "1.0.0",
        "evidence_corpus": "1.0.0",
        "far_fac": "2026-01",
    }
    event_7 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="evidence_retrieved",
        event_time=event_time,
        sequence=7,
        component="official_evidence_retriever",
        action=(
            "Execute registered exact or bounded semantic retrieval "
            "without substituting semantic records for missing exact citations."
        ),
        status="succeeded",
        reason_codes=sorted(
            {
                reason
                for result in results
                for reason in result["reason_codes"]
                if reason
                in {
                    "CLAUSE_NOT_FOUND",
                    "SEARCH_NO_RESULTS",
                    "EXACT_CITATION_REQUIRED",
                    "SEMANTIC_MATCH_NOT_EXACT",
                }
            }
        ),
        input_artifact_ids=[
            f"ART-CASE-{case_state['case_id']}",
            "ART-P4-04-REGISTERED-FAR-SUBSET",
        ],
        output_artifact_ids=[
            f"ART-EVIDENCE-ITEMS-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "request_count": len(results),
            "evidence_item_count": len(evidence_by_id),
            "exact_citation_semantic_fallback_used": False,
            "external_actions_performed": 0,
        },
        previous_event_hash=previous_hash,
    )
    event_8 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="evidence_validated",
        event_time=event_time,
        sequence=8,
        component="evidence_validator",
        action=(
            "Validate citation metadata, source version, snapshot integrity, "
            "claim support, and evidence sufficiency."
        ),
        status=(
            "succeeded"
            if all(
                assessment["sufficiency_status"] == "sufficient"
                for assessment in assessments
            )
            else "warned"
        ),
        reason_codes=sorted(
            {
                reason
                for assessment in assessments
                for reason in assessment["reason_codes"]
            }
        ),
        input_artifact_ids=[
            f"ART-EVIDENCE-ITEMS-{case_state['case_id']}"
        ],
        output_artifact_ids=[
            f"ART-EVIDENCE-ASSESSMENTS-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "assessment_count": len(assessments),
            "sufficient_count": sum(
                assessment["sufficiency_status"] == "sufficient"
                for assessment in assessments
            ),
            "material_conflict_count": sum(
                assessment["conflict_status"] == "material_conflict"
                for assessment in assessments
            ),
        },
        previous_event_hash=event_7["event_hash"],
    )
    event_9 = build_audit_event(
        case_id=case_state["case_id"],
        event_type="case_escalated",
        event_time=event_time,
        sequence=9,
        component="risk_escalation_router",
        action=(
            "Route the public-sector consequential case and Project 4 "
            "domain-shift outputs to qualified human review."
        ),
        status="warned",
        reason_codes=sorted(
            set(upstream_reason_codes)
            | {"HUMAN_REVIEW_REQUIRED"}
        ),
        input_artifact_ids=[
            f"ART-EVIDENCE-ASSESSMENTS-{case_state['case_id']}"
        ],
        output_artifact_ids=[
            f"ART-HUMAN-ROUTE-{case_state['case_id']}"
        ],
        configuration_versions=versions,
        sanitized_details={
            "reviewer_role": "Contracts or Legal Reviewer",
            "supported_evidence_preserved": True,
            "legal_interpretation_performed": False,
            "external_actions_performed": 0,
        },
        previous_event_hash=event_8["event_hash"],
    )

    for event in [event_7, event_8, event_9]:
        validate_artifact(
            event,
            "audit_event.schema.json",
            schema_dir,
        )

    updated_case = {
        **case_state,
        "case_status": "escalated",
        "updated_at": event_time,
        "evidence_items": list(evidence_by_id.values()),
        "evidence_assessments": assessments,
        "audit_event_ids": (
            case_state["audit_event_ids"]
            + [
                event_7["event_id"],
                event_8["event_id"],
                event_9["event_id"],
            ]
        ),
    }
    validate_artifact(
        updated_case,
        "integrated_case_state.schema.json",
        schema_dir,
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)
    tool_trace_output_path.parent.mkdir(parents=True, exist_ok=True)

    result_bundle = {
        "bundle_schema_version": "1.0.0",
        "case_id": case_state["case_id"],
        "request_count": len(results),
        "results": results,
        "human_review_required": True,
        "reviewer_role": "Contracts or Legal Reviewer",
        "external_actions_performed": 0,
        "production_boundary": (
            "Controlled capstone prototype; nonbinding recommendations only; "
            "no autonomous external action; final human authority required."
        ),
    }
    (output_directory / "evidence_workflow_results.json").write_text(
        json.dumps(
            result_bundle,
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
            for event in [event_7, event_8, event_9]
        ),
        encoding="utf-8",
    )
    tool_trace_output_path.write_text(
        "".join(
            json.dumps(
                {
                    "request_id": result["request_id"],
                    **trace,
                },
                ensure_ascii=False,
            )
            + "\n"
            for result in results
            for trace in result["tool_trace"]
        ),
        encoding="utf-8",
    )
    return {
        "results": results,
        "updated_case_state": updated_case,
        "audit_events": [event_7, event_8, event_9],
    }
