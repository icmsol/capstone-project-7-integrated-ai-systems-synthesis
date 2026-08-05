"""Transparent exclusion-first service alignment."""

from __future__ import annotations

import re
from typing import Any

from .profile_loader import OrganizationProfileBundle
from .schema_validation import validate_artifact


class AlignmentError(RuntimeError):
    """Service-alignment error with stable behavior metadata."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        behavior: str,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.behavior = behavior


def _normalize(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _terms(value: str) -> list[str]:
    return [
        _normalize(term)
        for term in str(value or "").split(";")
        if _normalize(term)
    ]


def _contains(text: str, term: str) -> bool:
    if not term:
        return False
    if len(term.split()) == 1:
        return bool(
            re.search(
                rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])",
                text,
            )
        )
    return term in text


def _alignment_label(
    *,
    score: float,
    matched_capabilities: list[dict[str, Any]],
    policy: dict[str, Any],
) -> str:
    thresholds = policy["alignment_thresholds"]
    strong_count = sum(
        match["match_strength"] == "strong"
        for match in matched_capabilities
    )
    if (
        score >= thresholds["strong_alignment"]
        and strong_count
        >= policy["strong_alignment_minimum_capabilities"]
    ):
        return "strong_alignment"
    if score >= thresholds["conditional_alignment"]:
        return "conditional_alignment"
    if score >= thresholds["weak_alignment"]:
        return "weak_alignment"
    return "no_alignment"


def assess_service_alignment(
    opportunity: dict[str, Any],
    profile_bundle: OrganizationProfileBundle,
    policy: dict[str, Any],
    *,
    schema_dir,
) -> dict[str, Any]:
    """Assess one opportunity using only the active configuration bundle."""

    source_text = _normalize(
        " ".join(
            [
                opportunity.get("title") or "",
                opportunity.get("description") or "",
                opportunity.get("place_of_performance") or "",
                opportunity.get("procurement_method") or "",
                opportunity.get("contract_vehicle") or "",
            ]
        )
    )

    if (
        len(source_text)
        < policy["minimum_meaningful_text_characters"]
    ):
        result = {
            "alignment_schema_version": "1.0.0",
            "case_id": opportunity["case_id"],
            "organization_id": (
                profile_bundle.profile["organization_id"]
            ),
            "profile_version": (
                profile_bundle.profile["profile_version"]
            ),
            "service_catalog_version": (
                profile_bundle.service_catalog[0]["profile_version"]
            ),
            "matched_capabilities": [],
            "excluded_matches": [],
            "alignment_score": 0.0,
            "alignment_label": "insufficient_information",
            "staffing_families": [],
            "reason_codes": ["ALIGNMENT_INPUT_INSUFFICIENT"],
            "limitations": [
                {
                    "code": "ALIGNMENT_INPUT_INSUFFICIENT",
                    "description": (
                        "The title and description are insufficient for "
                        "meaningful configuration-driven screening."
                    ),
                    "material": True,
                    "mitigation": (
                        "Request the missing opportunity scope before "
                        "using service alignment downstream."
                    ),
                }
            ],
        }
        validate_artifact(
            result,
            "service_alignment.schema.json",
            schema_dir,
        )
        return result

    matched_capabilities = []
    excluded_matches = []

    for capability in profile_bundle.service_catalog:
        exclusions = [
            term
            for term in _terms(capability["exclusion_keywords"])
            if _contains(source_text, term)
        ]
        if exclusions:
            for term in exclusions:
                excluded_matches.append(
                    {
                        "term": term,
                        "reason": (
                            "Exclusion-first rule blocked capability "
                            f"{capability['capability_id']}."
                        ),
                    }
                )
            continue

        strong_terms = [
            term
            for term in _terms(
                capability["strong_match_phrases"]
            )
            if _contains(source_text, term)
        ]
        positive_terms = [
            term
            for term in _terms(
                capability["positive_keywords"]
            )
            if _contains(source_text, term)
        ]

        matched_terms = sorted(
            set(strong_terms + positive_terms)
        )
        if not matched_terms:
            continue

        if (
            strong_terms
            or len(positive_terms) >= 3
            or (
                policy.get(
                    "multiword_positive_keyword_is_strong",
                    False,
                )
                and any(
                    len(term.split()) >= 2
                    for term in positive_terms
                )
            )
        ):
            strength = "strong"
        elif len(positive_terms) >= 2:
            strength = "moderate"
        else:
            strength = "weak"

        matched_capabilities.append(
            {
                "capability_id": capability["capability_id"],
                "capability_name": capability["capability_name"],
                "service_family_id": (
                    capability["service_family_id"]
                ),
                "matched_terms": matched_terms,
                "match_strength": strength,
                "evidence_text": (
                    "Opportunity text matched configured terms for "
                    f"{capability['capability_name']}: "
                    + ", ".join(matched_terms)
                ),
            }
        )

    matched_capabilities = sorted(
        matched_capabilities,
        key=lambda item: (
            {
                "strong": 3,
                "moderate": 2,
                "weak": 1,
            }[item["match_strength"]],
            len(item["matched_terms"]),
            item["capability_id"],
        ),
        reverse=True,
    )[: policy["maximum_matched_capabilities"]]

    weights = policy["match_strength_weights"]
    if matched_capabilities:
        strongest = [
            weights[item["match_strength"]]
            for item in matched_capabilities[:3]
        ]
        base_score = sum(strongest) / 3
        family_count = len(
            {
                item["service_family_id"]
                for item in matched_capabilities
            }
        )
        diversity_bonus = min(0.20, max(0, family_count - 1) * 0.04)
        alignment_score = round(
            min(1.0, base_score + diversity_bonus),
            4,
        )
    else:
        alignment_score = 0.0

    label = _alignment_label(
        score=alignment_score,
        matched_capabilities=matched_capabilities,
        policy=policy,
    )

    staffing_lookup = {
        row["service_family_id"]: row["staffing_family"]
        for row in profile_bundle.staffing_map
    }
    staffing_families = sorted(
        {
            staffing_lookup[item["service_family_id"]]
            for item in matched_capabilities
            if item["service_family_id"] in staffing_lookup
        }
    )

    reason_code = {
        "strong_alignment": "ALIGNMENT_STRONG",
        "conditional_alignment": "ALIGNMENT_CONDITIONAL",
        "weak_alignment": "ALIGNMENT_WEAK",
        "no_alignment": "ALIGNMENT_NONE",
    }[label]

    limitations = [
        {
            "code": "SCREENING_NOT_DECISION",
            "description": (
                "Configuration-driven term alignment is a transparent "
                "screening input, not a complete scope, capacity, eligibility, "
                "award-probability, or final pursuit decision."
            ),
            "material": True,
            "mitigation": (
                "Review the full solicitation, qualifications, current "
                "availability, and authoritative evidence before a human decision."
            ),
        },
        {
            "code": "TEXT_MATCH_LIMIT",
            "description": (
                "The assessment evaluates configured terms in normalized "
                "opportunity text and may miss implied or differently worded scope."
            ),
            "material": True,
            "mitigation": (
                "Use human review and later evidence retrieval to confirm "
                "or reject the preliminary service alignment."
            ),
        },
    ]

    result = {
        "alignment_schema_version": "1.0.0",
        "case_id": opportunity["case_id"],
        "organization_id": (
            profile_bundle.profile["organization_id"]
        ),
        "profile_version": (
            profile_bundle.profile["profile_version"]
        ),
        "service_catalog_version": (
            profile_bundle.service_catalog[0]["profile_version"]
        ),
        "matched_capabilities": matched_capabilities,
        "excluded_matches": excluded_matches,
        "alignment_score": alignment_score,
        "alignment_label": label,
        "staffing_families": staffing_families,
        "reason_codes": [reason_code],
        "limitations": limitations,
    }
    validate_artifact(
        result,
        "service_alignment.schema.json",
        schema_dir,
    )
    return result
