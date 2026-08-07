"""P4-03 integrated clause-triage pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audit_utils import build_audit_event
from .clause_triage import (
    Project4InferencePackage,
    triage_passage,
)
from .schema_validation import validate_artifact


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run_clause_triage(
    *,
    repo_root: Path,
    case_state_path: Path,
    passage_set_path: Path,
    output_directory: Path,
    audit_output_path: Path,
    event_time: str,
    prior_audit_path: Path | None = None,
) -> dict[str, Any]:
    schema_dir = repo_root / "config" / "schemas"
    case_state = _load_json(case_state_path)
    passage_set = _load_json(passage_set_path)
    policy = _load_json(
        repo_root / "config" / "system"
        / "clause_triage_policy.json"
    )
    registry = _load_json(
        repo_root / "config" / "system"
        / "project4_model_registry.json"
    )
    passages = passage_set["passages"]
    if len(passages) > policy["maximum_passages_per_case"]:
        raise ValueError("Too many passages for one case.")

    package = Project4InferencePackage.load(
        repo_root / registry["model_directory"],
        registry=registry,
        device="cpu",
    )
    predictions = [
        triage_passage(
            inference_package=package,
            case_id=case_state["case_id"],
            passage_id=item["passage_id"],
            passage_text=item["text"],
            policy=policy,
            source_domain=passage_set["source_domain"],
            consequential_use=bool(
                passage_set["consequential_use"]
            ),
            schema_dir=schema_dir,
        )
        for item in passages
    ]

    prior_audit_path = (
        prior_audit_path
        if prior_audit_path is not None
        else repo_root / "audit" / "p4_02_alignment_history_events.jsonl"
    )
    prior_events = [
        json.loads(line)
        for line in prior_audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    previous_hash = prior_events[-1]["event_hash"]
    reason_codes = sorted(
        {
            reason
            for prediction in predictions
            for reason in prediction["reason_codes"]
        }
    )
    event = build_audit_event(
        case_id=case_state["case_id"],
        event_type="clause_triage_completed",
        event_time=event_time,
        sequence=6,
        component="clause_triage_model",
        action=(
            "Produce bounded Project 4 clause-theme triage outputs."
        ),
        status=(
            "warned"
            if any(
                item["decision"] in {"abstain", "escalate"}
                for item in predictions
            )
            else "succeeded"
        ),
        reason_codes=reason_codes,
        input_artifact_ids=[
            f"ART-CASE-{case_state['case_id']}",
            "ART-PROJECT4-CLAUSE-CLASSIFIER",
        ],
        output_artifact_ids=[
            f"ART-CLAUSE-PREDICTIONS-{case_state['case_id']}"
        ],
        configuration_versions={
            **case_state["organization_context"],
            "clause_triage_policy": "1.0.0",
            "project4_model": registry["model_version"],
        },
        sanitized_details={
            "passage_count": len(predictions),
            "classify_count": sum(
                item["decision"] == "classify"
                for item in predictions
            ),
            "abstain_count": sum(
                item["decision"] == "abstain"
                for item in predictions
            ),
            "escalate_count": sum(
                item["decision"] == "escalate"
                for item in predictions
            ),
            "legal_interpretation_performed": False,
            "external_action_performed": False,
        },
        previous_event_hash=previous_hash,
    )
    validate_artifact(
        event,
        "audit_event.schema.json",
        schema_dir,
    )

    updated_case = {
        **case_state,
        "updated_at": event_time,
        "clause_predictions": predictions,
        "audit_event_ids": (
            case_state["audit_event_ids"]
            + [event["event_id"]]
        ),
    }
    validate_artifact(
        updated_case,
        "integrated_case_state.schema.json",
        schema_dir,
    )

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)
    (output_directory / "clause_predictions.json").write_text(
        json.dumps(
            {
                "case_id": case_state["case_id"],
                "prediction_count": len(predictions),
                "predictions": predictions,
                "production_boundary": (
                    policy["production_boundary"]
                ),
            },
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
        json.dumps(event, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "predictions": predictions,
        "updated_case_state": updated_case,
        "audit_event": event,
    }
