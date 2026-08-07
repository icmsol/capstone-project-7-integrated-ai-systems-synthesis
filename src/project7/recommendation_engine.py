"""Deterministic nonbinding recommendation engine."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .schema_validation import validate_artifact


class RecommendationError(RuntimeError):
    """Recommendation-generation error with stable reason metadata."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        behavior: str = "fail_closed",
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = behavior


def _stable_id(case_id: str, suffix: str) -> str:
    digest = hashlib.sha256(
        f"{case_id}|{suffix}".encode("utf-8")
    ).hexdigest()[:20].upper()
    return f"REC-{digest}"


def _limitation(
    code: str,
    description: str,
    mitigation: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "description": description,
        "material": True,
        "mitigation": mitigation,
    }


def create_nonbinding_recommendation(
    *,
    case_state: dict[str, Any],
    policy: dict[str, Any],
    schema_dir: Path,
    audit_reference: str,
    created_at: str,
) -> dict[str, Any]:
    """Create an advisory recommendation without making a final decision."""

    required_nonempty_components = [
        "opportunity",
        "service_alignment",
        "historical_context",
        "clause_predictions",
        "evidence_assessments",
    ]
    missing = [
        component
        for component in required_nonempty_components
        if case_state.get(component) in (None, [], {})
    ]
    if (
        "evidence_items" not in case_state
        or case_state.get("evidence_items") is None
        or not isinstance(case_state.get("evidence_items"), list)
    ):
        missing.append("evidence_items")
    if missing:
        raise RecommendationError(
            "PACKET_COMPONENT_MISSING",
            "Recommendation input is incomplete: "
            + ", ".join(sorted(set(missing))),
        )

    alignment = case_state["service_alignment"]
    assessments = case_state["evidence_assessments"]
    predictions = case_state["clause_predictions"]
    evidence_items = case_state["evidence_items"]

    upstream_reasons = {
        reason
        for prediction in predictions
        for reason in prediction["reason_codes"]
    }
    upstream_reasons.update(
        reason
        for assessment in assessments
        for reason in assessment["reason_codes"]
    )

    specialized_review = bool(
        {
            "MODEL_DOMAIN_SHIFT",
            "MODEL_INPUT_TRUNCATED",
            "EVIDENCE_CONFLICT",
        }
        & upstream_reasons
    )
    all_evidence_sufficient = all(
        assessment["sufficiency_status"] == "sufficient"
        for assessment in assessments
    )
    minimum_evidence_score = min(
        assessment["evidence_score"]
        for assessment in assessments
    )

    if specialized_review:
        code = "R-05"
        label = "Escalate — Specialized Review Required"
        strength = 1.0
    elif not all_evidence_sufficient:
        code = "R-03"
        label = "Recommend Hold — Gather Information"
        strength = 0.95
    elif (
        alignment["alignment_score"]
        >= policy["minimum_alignment_for_directional_pursuit"]
        and minimum_evidence_score
        >= policy["minimum_evidence_score_for_directional_pursuit"]
    ):
        code = "R-02"
        label = "Recommend Pursue with Conditions"
        strength = 0.85
    else:
        code = "R-06"
        label = "No Recommendation"
        strength = 1.0

    supporting_evidence_ids = sorted(
        item["evidence_id"]
        for item in evidence_items
        if item["metadata_valid"]
        and item["citation_valid"]
        and item["supports_claim"]
        and not item["conflicts_with_claim"]
    )

    truncated_count = sum(
        bool(prediction.get("truncated"))
        for prediction in predictions
    )
    domain_warning_count = sum(
        bool(prediction.get("domain_warning"))
        for prediction in predictions
    )
    insufficient_assessments = [
        assessment
        for assessment in assessments
        if assessment["sufficiency_status"] != "sufficient"
    ]

    missing_information = [
        "Complete current solicitation, amendments, attachments, and incorporated terms.",
        "Mandatory eligibility, certification, insurance, security, and qualification requirements.",
        "Current named or role-based staffing availability and delivery capacity.",
        "Pricing, labor mix, subcontracting, cost, and margin feasibility.",
        "Proposal, mobilization, and delivery schedule feasibility.",
        "Qualified determination of clause applicability and contractual implications.",
    ]
    if insufficient_assessments:
        missing_information.append(
            "Registered authoritative evidence was insufficient for "
            f"{len(insufficient_assessments)} assessed claim(s); obtain and review "
            "the applicable current official source text."
        )
    if truncated_count:
        missing_information.append(
            "Complete review of the passage(s) that exceeded the model's 256-token limit."
        )

    conditions = [
        "A Contracts or Legal Reviewer reviews the current complete solicitation and official clause text.",
        "Leadership confirms eligibility, strategic fit, staffing capacity, delivery risk, and financial feasibility.",
        "The original recommendation remains separate from the authorized human disposition.",
    ]
    if insufficient_assessments:
        conditions.insert(
            1,
            "Do not treat absent or insufficient registered evidence as support for clause applicability, meaning, or compliance.",
        )
    if truncated_count:
        conditions.insert(
            -1,
            "Any truncated passage and its surrounding context are reviewed outside the bounded model input.",
        )

    reason_codes = {
        "RECOMMENDATION_NONBINDING",
        "HUMAN_REVIEW_REQUIRED",
        "FULL_SOLICITATION_NOT_REVIEWED",
        "ELIGIBILITY_UNVERIFIED",
        "CAPACITY_UNVERIFIED",
        "PRICING_AND_MARGIN_UNVERIFIED",
        "SCHEDULE_UNVERIFIED",
        "CLAUSE_APPLICABILITY_UNVERIFIED",
        "HUMAN_DISPOSITION_PENDING",
    }
    if code == "R-05":
        reason_codes.add(
            "RECOMMENDATION_ESCALATE_SPECIALIZED_REVIEW"
        )
    reason_codes.update(
        upstream_reasons
        & {
            "MODEL_DOMAIN_SHIFT",
            "MODEL_INPUT_TRUNCATED",
            "SUPPORTED_WITH_EVIDENCE",
            "SEARCH_NO_RESULTS",
            "EVIDENCE_INSUFFICIENT",
            "EVIDENCE_CONFLICT",
        }
    )

    if code == "R-05":
        recommended_next_action = (
            "Route the integrated packet to a Contracts or Legal Reviewer, then "
            "to authorized business leadership for a documented human disposition "
            "after the identified information gaps are resolved."
        )
    elif code == "R-03":
        recommended_next_action = (
            "Gather the identified missing information and applicable official "
            "evidence, then return the packet to the required authorized human reviewer."
        )
    elif code == "R-02":
        recommended_next_action = (
            "Route the conditional pursuit recommendation to authorized business "
            "leadership for a separate documented human disposition."
        )
    else:
        recommended_next_action = (
            "Route the packet to the required authorized human reviewer for a "
            "documented disposition; the system does not make the final decision."
        )

    recommendation = {
        "recommendation_schema_version": "1.0.0",
        "recommendation_id": _stable_id(
            case_state["case_id"],
            "P4-05-RECOMMENDATION",
        ),
        "case_id": case_state["case_id"],
        "organization_id": case_state[
            "organization_context"
        ]["organization_id"],
        "profile_version": case_state[
            "organization_context"
        ]["profile_version"],
        "recommendation_code": code,
        "recommendation_label": label,
        "nonbinding_disclosure": (
            "This is an advisory decision-support recommendation only. "
            "It is not a final pursuit, procurement, legal, contractual, "
            "staffing, pricing, or commitment decision."
        ),
        "recommendation_strength": strength,
        "supporting_evidence_ids": supporting_evidence_ids,
        "counterevidence_ids": [],
        "missing_information": missing_information,
        "conditions": conditions,
        "limitations": [
            _limitation(
                "NONBINDING_RECOMMENDATION",
                (
                    "The recommendation prioritizes review and next actions; "
                    "it does not authorize pursuit or decline."
                ),
                (
                    "An authorized human reviewer must record a separate "
                    "disposition and rationale."
                ),
            ),
            _limitation(
                "EVIDENCE_SCOPE_LIMITED",
                (
                    "The evidence workflow used a representative three-record "
                    "FAR subset and accepted "
                    f"{len(evidence_items)} evidence item(s) across "
                    f"{len(assessments)} assessment(s); it is not the complete "
                    "current solicitation or a full authoritative corpus."
                ),
                (
                    "Review all current official acquisition documents and obtain "
                    "applicable authoritative evidence before a consequential disposition."
                ),
            ),
            _limitation(
                "MODEL_DOMAIN_LIMIT",
                (
                    "Project 4 clause-theme triage produced "
                    f"{domain_warning_count} domain warning(s) and "
                    f"{truncated_count} truncated passage(s). The model was trained "
                    "on commercial-contract language and is used for triage only."
                ),
                (
                    "Require qualified review of the original complete language; "
                    "review any truncated passage outside the bounded model input."
                ),
            ),
            _limitation(
                "BUSINESS_FEASIBILITY_UNVERIFIED",
                (
                    "Alignment and historical counts do not verify eligibility, "
                    "capacity, pricing, margin, schedule, or award probability."
                ),
                (
                    "Complete business, staffing, financial, and delivery review."
                ),
            ),
        ],
        "required_human_reviewer": policy[
            "required_human_reviewer"
        ],
        "recommended_next_action": recommended_next_action,
        "data_freshness_status": "acceptable",
        "reason_codes": sorted(reason_codes),
        "audit_reference": audit_reference,
        "created_at": created_at,
    }
    validate_artifact(
        recommendation,
        "recommendation.schema.json",
        schema_dir,
    )
    return recommendation
