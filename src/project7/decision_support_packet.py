"""Integrated human decision-support packet assembler."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .schema_validation import validate_artifact


class PacketAssemblyError(RuntimeError):
    """Fail-closed packet assembly exception."""

    def __init__(
        self,
        reason_code: str,
        message: str,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = "fail_closed"


def _canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _issue(
    *,
    issue_id: str,
    category: str,
    severity: str,
    description: str,
    source_components: list[str],
    reason_codes: list[str],
    required_action: str,
    blocks_final_disposition: bool,
) -> dict[str, Any]:
    return {
        "issue_id": issue_id,
        "category": category,
        "severity": severity,
        "description": description,
        "source_components": source_components,
        "reason_codes": reason_codes,
        "required_action": required_action,
        "blocks_final_disposition": blocks_final_disposition,
    }


def assemble_decision_support_packet(
    *,
    case_state: dict[str, Any],
    recommendation: dict[str, Any],
    packet_policy: dict[str, Any],
    schema_dir: Path,
    packet_id: str,
    generated_at: str,
    audit_event_ids: list[str],
) -> dict[str, Any]:
    """Assemble one coherent review packet from all prior components."""

    required_nonempty = [
        "opportunity",
        "service_alignment",
        "historical_context",
        "clause_predictions",
        "evidence_assessments",
    ]
    missing = [
        name
        for name in required_nonempty
        if case_state.get(name) in (None, [], {})
    ]
    if (
        "evidence_items" not in case_state
        or case_state.get("evidence_items") is None
        or not isinstance(case_state.get("evidence_items"), list)
    ):
        missing.append("evidence_items")
    if missing:
        raise PacketAssemblyError(
            "PACKET_COMPONENT_MISSING",
            "Required packet components are absent: "
            + ", ".join(sorted(set(missing))),
        )

    opportunity = case_state["opportunity"]
    alignment = case_state["service_alignment"]
    historical = case_state["historical_context"]
    predictions = case_state["clause_predictions"]
    evidence_items = case_state["evidence_items"]
    assessments = case_state["evidence_assessments"]

    prediction_reason_codes = sorted(
        {
            reason
            for prediction in predictions
            for reason in prediction["reason_codes"]
        }
    )
    assessment_reason_codes = sorted(
        {
            reason
            for assessment in assessments
            for reason in assessment["reason_codes"]
        }
    )

    escalation_count = sum(
        item["decision"] == "escalate"
        for item in predictions
    )
    domain_warning_count = sum(
        bool(item.get("domain_warning"))
        for item in predictions
    )
    truncation_count = sum(
        bool(item.get("truncated"))
        for item in predictions
    )
    sufficient_assessment_count = sum(
        item["sufficiency_status"] == "sufficient"
        for item in assessments
    )
    insufficient_assessment_count = (
        len(assessments) - sufficient_assessment_count
    )
    material_conflict_count = sum(
        item["conflict_status"] == "material_conflict"
        for item in assessments
    )

    prediction_categories = list(
        dict.fromkeys(
            item["predicted_category"]
            for item in predictions
        )
    )
    prediction_summary = ", ".join(prediction_categories)
    if not prediction_summary:
        prediction_summary = "no clause themes"

    alignment_phrase = alignment["alignment_label"].replace("_", " ")
    evidence_phrase = (
        f"{len(evidence_items)} accepted evidence item(s) and "
        f"{sufficient_assessment_count}/{len(assessments)} sufficient assessment(s)"
    )
    warning_phrase = (
        f"{domain_warning_count} domain warning(s) and "
        f"{truncation_count} truncated passage(s)"
    )
    executive_summary = (
        f"The opportunity has {alignment_phrase} configuration-driven alignment "
        f"(score {alignment['alignment_score']:.2f}) and descriptive historical "
        f"context. Project 4 triage identified {prediction_summary}; the bounded "
        f"model produced {warning_phrase}. The evidence workflow produced "
        f"{evidence_phrase}. The nonbinding system recommendation is "
        f"'{recommendation['recommendation_label']}'. No pursuit, decline, legal, "
        "contractual, staffing, pricing, or other final decision is made by the system."
    )

    unresolved_issues = [
        _issue(
            issue_id="ISSUE-P4-05-001",
            category="document_completeness",
            severity="critical",
            description=(
                "The controlled case does not contain the complete current "
                "solicitation, amendments, attachments, and incorporated terms."
            ),
            source_components=[
                "opportunity_intake",
                "official_evidence",
            ],
            reason_codes=["FULL_SOLICITATION_NOT_REVIEWED"],
            required_action=(
                "Obtain and review the complete current solicitation package."
            ),
            blocks_final_disposition=True,
        ),
        _issue(
            issue_id="ISSUE-P4-05-005",
            category="eligibility",
            severity="high",
            description=(
                "Mandatory eligibility, certification, security, insurance, and "
                "qualification requirements have not been verified."
            ),
            source_components=["opportunity_intake"],
            reason_codes=["ELIGIBILITY_UNVERIFIED"],
            required_action=(
                "Complete an eligibility and mandatory-requirements checklist."
            ),
            blocks_final_disposition=True,
        ),
        _issue(
            issue_id="ISSUE-P4-05-006",
            category="capacity",
            severity="high",
            description=(
                "Matched service capabilities do not establish current staffing "
                "availability, subcontractor availability, or delivery capacity."
            ),
            source_components=[
                "organization_alignment",
                "historical_context",
            ],
            reason_codes=["CAPACITY_UNVERIFIED"],
            required_action=(
                "Confirm role-level staffing, availability, and delivery capacity."
            ),
            blocks_final_disposition=True,
        ),
        _issue(
            issue_id="ISSUE-P4-05-007",
            category="financial",
            severity="high",
            description=(
                "Pricing, labor mix, costs, rates, subcontracting, and margin "
                "feasibility have not been evaluated."
            ),
            source_components=[
                "opportunity_intake",
                "historical_context",
            ],
            reason_codes=["PRICING_AND_MARGIN_UNVERIFIED"],
            required_action=(
                "Complete pricing, cost, and margin analysis before a pursuit decision."
            ),
            blocks_final_disposition=True,
        ),
        _issue(
            issue_id="ISSUE-P4-05-008",
            category="schedule",
            severity="medium",
            description=(
                "Proposal preparation, mobilization, transition, and delivery "
                "schedule feasibility have not been verified."
            ),
            source_components=["opportunity_intake"],
            reason_codes=["SCHEDULE_UNVERIFIED"],
            required_action=(
                "Validate proposal and delivery schedule feasibility."
            ),
            blocks_final_disposition=True,
        ),
        _issue(
            issue_id="ISSUE-P4-05-009",
            category="human_authority",
            severity="critical",
            description=(
                "No authorized human disposition has been recorded; the system "
                "recommendation cannot become the final decision."
            ),
            source_components=[
                "nonbinding_recommendation",
                "human_review_boundary",
            ],
            reason_codes=["HUMAN_DISPOSITION_PENDING"],
            required_action=(
                "An authorized reviewer must record a disposition and rationale."
            ),
            blocks_final_disposition=True,
        ),
    ]

    if domain_warning_count:
        unresolved_issues.insert(
            1,
            _issue(
                issue_id="ISSUE-P4-05-002",
                category="model_domain",
                severity="high",
                description=(
                    f"{domain_warning_count} Project 4 prediction(s) carry a "
                    "domain warning because the bounded model was trained on "
                    "commercial-contract language."
                ),
                source_components=["clause_triage"],
                reason_codes=["MODEL_DOMAIN_SHIFT"],
                required_action=(
                    "Use the classifications only as triage and require qualified "
                    "review of the original complete language."
                ),
                blocks_final_disposition=True,
            ),
        )

    if truncation_count:
        unresolved_issues.insert(
            2 if domain_warning_count else 1,
            _issue(
                issue_id="ISSUE-P4-05-003",
                category="model_input",
                severity="critical",
                description=(
                    f"{truncation_count} passage(s) exceeded the bounded model "
                    "input and were truncated before inference."
                ),
                source_components=["clause_triage"],
                reason_codes=["MODEL_INPUT_TRUNCATED"],
                required_action=(
                    "Review each complete passage and surrounding text outside the model."
                ),
                blocks_final_disposition=True,
            ),
        )

    evidence_issue_position = 1 + int(bool(domain_warning_count)) + int(bool(truncation_count))
    if insufficient_assessment_count or not evidence_items:
        evidence_reason_codes = sorted(
            set(assessment_reason_codes)
            or {"CLAUSE_APPLICABILITY_UNVERIFIED"}
        )
        unresolved_issues.insert(
            evidence_issue_position,
            _issue(
                issue_id="ISSUE-P4-05-004",
                category="evidence_sufficiency",
                severity="high",
                description=(
                    f"The registered evidence workflow accepted {len(evidence_items)} "
                    f"evidence item(s), and {insufficient_assessment_count} of "
                    f"{len(assessments)} assessment(s) remain insufficient. "
                    "Absence of registered evidence is not evidence of clause "
                    "inapplicability, compliance, or acceptable risk."
                ),
                source_components=["official_evidence"],
                reason_codes=evidence_reason_codes,
                required_action=(
                    "Obtain and review the applicable current official authority and "
                    "have a Contracts or Legal Reviewer determine applicability."
                ),
                blocks_final_disposition=True,
            ),
        )
    else:
        unresolved_issues.insert(
            evidence_issue_position,
            _issue(
                issue_id="ISSUE-P4-05-004",
                category="contract_applicability",
                severity="high",
                description=(
                    "Evidence retrieval validates metadata and bounded subject matter "
                    "but does not determine whether the clauses apply to this procurement."
                ),
                source_components=["official_evidence"],
                reason_codes=["CLAUSE_APPLICABILITY_UNVERIFIED"],
                required_action=(
                    "Have a Contracts or Legal Reviewer determine applicability using "
                    "the complete current acquisition context."
                ),
                blocks_final_disposition=True,
            ),
        )

    evidence_limitations = [
        limitation
        for item in evidence_items
        for limitation in item["limitations"]
    ]
    if not evidence_items:
        evidence_limitations.append(
            {
                "code": "EVIDENCE_SCOPE_LIMITED",
                "description": (
                    "No registered evidence record met the configured acceptance "
                    "criteria for the assessed claims."
                ),
                "material": True,
                "mitigation": (
                    "Obtain and review applicable current official authority before "
                    "a consequential human disposition."
                ),
            }
        )

    packet = {
        "packet_schema_version": "1.0.0",
        "packet_id": packet_id,
        "case_id": case_state["case_id"],
        "generated_at": generated_at,
        "packet_status": packet_policy["packet_status"],
        "source_case_state_sha256": _canonical_sha256(
            case_state
        ),
        "executive_summary": executive_summary,
        "opportunity_summary": {
            "agency": opportunity["agency"],
            "solicitation_id": opportunity["solicitation_id"],
            "title": opportunity["title"],
            "status": opportunity["status"],
            "due_at": opportunity["due_at"],
            "jurisdiction": opportunity["jurisdiction"],
            "procurement_method": opportunity[
                "procurement_method"
            ],
            "estimated_value": opportunity.get(
                "estimated_value"
            ),
        },
        "organization_fit_summary": {
            "organization_id": alignment["organization_id"],
            "alignment_label": alignment["alignment_label"],
            "alignment_score": alignment["alignment_score"],
            "matched_capability_ids": [
                item["capability_id"]
                for item in alignment["matched_capabilities"]
            ],
            "matched_capability_names": [
                item["capability_name"]
                for item in alignment["matched_capabilities"]
            ],
            "staffing_families": alignment["staffing_families"],
            "limitations": alignment["limitations"],
        },
        "historical_context_summary": {
            "source_period": historical["source_period"],
            "source_records": historical["source_records"],
            "matched_historical_records": historical[
                "matched_historical_records"
            ],
            "service_category_counts": historical[
                "service_category_counts"
            ],
            "interpretation": historical["interpretation"],
            "limitations": historical["limitations"],
        },
        "clause_triage_summary": {
            "prediction_count": len(predictions),
            "escalation_count": escalation_count,
            "domain_warning_count": domain_warning_count,
            "truncation_count": truncation_count,
            "predictions": [
                {
                    "passage_id": item["passage_id"],
                    "predicted_category": item[
                        "predicted_category"
                    ],
                    "confidence": item["confidence"],
                    "decision": item["decision"],
                    "domain_warning": item["domain_warning"],
                    "truncated": item["truncated"],
                    "reason_codes": item["reason_codes"],
                }
                for item in predictions
            ],
            "reason_codes": prediction_reason_codes,
        },
        "evidence_summary": {
            "evidence_item_count": len(evidence_items),
            "sufficient_assessment_count": sufficient_assessment_count,
            "material_conflict_count": material_conflict_count,
            "citations": [
                {
                    "evidence_id": item["evidence_id"],
                    "citation_text": item["citation"][
                        "citation_text"
                    ],
                    "source_locator": item["citation"][
                        "source_locator"
                    ],
                    "supports_claim": item[
                        "supports_claim"
                    ],
                    "freshness_status": item[
                        "freshness_status"
                    ],
                }
                for item in evidence_items
            ],
            "assessment_reason_codes": assessment_reason_codes,
            "limitations": evidence_limitations,
        },
        "recommendation": recommendation,
        "unresolved_issues": unresolved_issues,
        "human_review": {
            "required": True,
            "status": "pending",
            "required_reviewer": recommendation[
                "required_human_reviewer"
            ],
            "allowed_dispositions": packet_policy[
                "allowed_human_dispositions"
            ],
            "decision_authority": (
                "Only an authorized human reviewer may accept, modify, reject, "
                "defer, or escalate the recommendation. The automated packet "
                "cannot finalize the case or bind the organization."
            ),
            "original_recommendation_immutable": True,
            "human_disposition": None,
        },
        "component_artifacts": [
            {
                "component_id": "opportunity_intake",
                "component_status": "completed",
                "source_artifacts": [
                    "outputs/p4_01/normalized_opportunity.json",
                    "outputs/p4_01/initial_case_state.json",
                ],
                "audit_event_ids": case_state[
                    "audit_event_ids"
                ][0:2],
            },
            {
                "component_id": "organization_alignment",
                "component_status": "completed_with_limitations",
                "source_artifacts": [
                    "outputs/p4_02/service_alignment.json"
                ],
                "audit_event_ids": case_state[
                    "audit_event_ids"
                ][2:4],
            },
            {
                "component_id": "historical_context",
                "component_status": "completed_with_limitations",
                "source_artifacts": [
                    "outputs/p4_02/historical_context.json"
                ],
                "audit_event_ids": [
                    case_state["audit_event_ids"][4]
                ],
            },
            {
                "component_id": "clause_triage",
                "component_status": "escalated",
                "source_artifacts": [
                    "outputs/p4_03/clause_predictions.json"
                ],
                "audit_event_ids": [
                    case_state["audit_event_ids"][5]
                ],
            },
            {
                "component_id": "official_evidence",
                "component_status": "completed_with_limitations",
                "source_artifacts": [
                    "outputs/p4_04/evidence_workflow_results.json",
                    "outputs/p4_04/updated_case_state.json",
                ],
                "audit_event_ids": case_state[
                    "audit_event_ids"
                ][6:9],
            },
            {
                "component_id": "nonbinding_recommendation",
                "component_status": "escalated",
                "source_artifacts": [
                    "outputs/p4_05/recommendation.json"
                ],
                "audit_event_ids": [audit_event_ids[0]],
            },
            {
                "component_id": "human_review_packet",
                "component_status": "escalated",
                "source_artifacts": [
                    "outputs/p4_05/decision_support_packet.json",
                    "outputs/p4_05/decision_support_packet.md",
                    "outputs/p4_05/human_disposition_template.json",
                ],
                "audit_event_ids": [audit_event_ids[1]],
            },
        ],
        "audit_event_ids": (
            case_state["audit_event_ids"]
            + audit_event_ids
        ),
        "final_decision": None,
        "external_actions_performed": 0,
        "production_boundary": packet_policy[
            "production_boundary"
        ],
    }

    validate_artifact(
        packet,
        "decision_support_packet.schema.json",
        schema_dir,
    )
    return packet


def render_packet_markdown(packet: dict[str, Any]) -> str:
    """Render a reviewable Markdown representation of the packet."""

    opportunity = packet["opportunity_summary"]
    alignment = packet["organization_fit_summary"]
    history = packet["historical_context_summary"]
    triage = packet["clause_triage_summary"]
    evidence = packet["evidence_summary"]
    recommendation = packet["recommendation"]

    capability_rows = "\n".join(
        f"- `{capability_id}` — {capability_name}"
        for capability_id, capability_name in zip(
            alignment["matched_capability_ids"],
            alignment["matched_capability_names"],
        )
    )
    prediction_rows = "\n".join(
        (
            f"| `{item['passage_id']}` | {item['predicted_category']} | "
            f"{item['confidence']:.6f} | `{item['decision']}` | "
            f"{item['domain_warning']} | {item['truncated']} |"
        )
        for item in triage["predictions"]
    )
    citation_rows = "\n".join(
        (
            f"- `{item['evidence_id']}` — {item['citation_text']}  \n"
            f"  {item['source_locator']}"
        )
        for item in evidence["citations"]
    )
    if not citation_rows:
        citation_rows = (
            "No registered evidence record met the configured acceptance criteria "
            "for the assessed claims."
        )
    issue_rows = "\n".join(
        (
            f"| `{item['issue_id']}` | **{item['severity']}** | "
            f"{item['category']} | {item['description']} | "
            f"{item['required_action']} |"
        )
        for item in packet["unresolved_issues"]
    )
    conditions = "\n".join(
        f"- {item}" for item in recommendation["conditions"]
    )
    missing = "\n".join(
        f"- {item}"
        for item in recommendation["missing_information"]
    )

    return f"""# Integrated Human Decision-Support Packet

## Packet Control

| Field | Value |
|---|---|
| Packet ID | `{packet['packet_id']}` |
| Case ID | `{packet['case_id']}` |
| Status | `{packet['packet_status']}` |
| Generated | `{packet['generated_at']}` |
| Final decision | **Pending authorized human disposition** |
| External actions | `{packet['external_actions_performed']}` |

## Executive Summary

{packet['executive_summary']}

## Opportunity

| Field | Value |
|---|---|
| Agency | {opportunity['agency']} |
| Solicitation | `{opportunity['solicitation_id']}` |
| Title | {opportunity['title']} |
| Status | `{opportunity['status']}` |
| Due | `{opportunity['due_at']}` |
| Jurisdiction | {opportunity['jurisdiction']} |
| Procurement method | {opportunity['procurement_method']} |
| Estimated value | {opportunity['estimated_value']} |

## Configurable Organization Alignment

- Alignment: **{alignment['alignment_label']}**
- Alignment score: `{alignment['alignment_score']:.2f}`
- Staffing families: {', '.join(alignment['staffing_families'])}

### Matched capabilities

{capability_rows}

This alignment is screening evidence—not proof of eligibility, capacity, award probability, or final strategic fit.

## Historical Context

- Frozen source period: `{history['source_period']['start_date']}` through `{history['source_period']['end_date']}`
- Source records: `{history['source_records']:,}`
- Matched historical records: `{history['matched_historical_records']}`

{history['interpretation']}

## Clause-Theme Triage

| Passage | Predicted theme | Confidence | Decision | Domain warning | Truncated |
|---|---|---:|---|---|---|
{prediction_rows}

The model output is triage only. It is not legal interpretation, applicability, compliance, or contract approval.

## Validated Evidence

{citation_rows}

- Evidence items: `{evidence['evidence_item_count']}`
- Sufficient assessments: `{evidence['sufficient_assessment_count']}`
- Material conflicts: `{evidence['material_conflict_count']}`

The registered FAR evidence is a representative subset and does not replace review of the complete current official acquisition record.

## Nonbinding Recommendation

### {recommendation['recommendation_label']}

- Recommendation code: `{recommendation['recommendation_code']}`
- Recommendation strength: `{recommendation['recommendation_strength']:.2f}`
- Required reviewer: **{recommendation['required_human_reviewer']['role_name']}**
- Next action: {recommendation['recommended_next_action']}

> {recommendation['nonbinding_disclosure']}

### Required conditions

{conditions}

### Missing information

{missing}

## Unresolved Issues

| Issue | Severity | Category | Description | Required action |
|---|---|---|---|---|
{issue_rows}

## Authorized Human Disposition — Pending

Required reviewer: **{packet['human_review']['required_reviewer']['role_name']}**

Select and document one authorized disposition:

- [ ] Accept the nonbinding recommendation
- [ ] Accept with modified conditions
- [ ] Reject the recommendation
- [ ] Defer pending information
- [ ] Escalate to another authorized reviewer

Required disposition record:

- Reviewer identity and authorized role
- Selected disposition
- Rationale of at least 20 characters
- Any modified conditions
- Escalation target, when applicable
- Decision timestamp

**The original system recommendation must remain separate and immutable.**

## Audit and Integrity

- Source case-state SHA-256: `{packet['source_case_state_sha256']}`
- Packet audit events: `{', '.join(packet['audit_event_ids'][-2:])}`
- Total case audit events: `{len(packet['audit_event_ids'])}`
- Final decision in packet: `null`
- External actions performed: `0`

## Production Boundary

{packet['production_boundary']}
"""
