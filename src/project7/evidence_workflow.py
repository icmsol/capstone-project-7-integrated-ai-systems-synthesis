"""Bounded evidence-grounded agent workflow.

The workflow implements plan-act-observe-validate-escalate behavior using
deterministic tools. It does not make legal, procurement, approval, or final
organizational decisions.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence_retrieval import (
    EvidenceToolError,
    RegisteredEvidenceCorpus,
)
from .schema_validation import validate_artifact


PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore (?:all|the|previous|prior) instructions", re.I),
    re.compile(r"reveal (?:the )?(?:system|hidden) prompt", re.I),
    re.compile(r"bypass (?:the )?(?:safeguard|policy|rules?)", re.I),
    re.compile(r"do not follow (?:the )?(?:policy|rules|instructions)", re.I),
]
PRIVACY_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
]
OUT_OF_SCOPE_PATTERNS = [
    re.compile(r"\b(?:approve|reject|accept)\b.*\b(?:contract|procurement|clause)\b", re.I),
    re.compile(r"\bfinal legal (?:decision|interpretation|advice)\b", re.I),
    re.compile(r"\bacting as (?:the )?(?:contracting officer|attorney)\b", re.I),
    re.compile(r"\bmust we (?:accept|sign|approve|reject)\b", re.I),
]


@dataclass(frozen=True)
class WorkflowExecution:
    result: dict[str, Any]


def _normalize_title(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(
        re.findall(r"[a-z0-9]+", value.lower())
    )


def _evidence_id(
    case_id: str,
    claim_id: str,
    clause_number: str,
) -> str:
    seed = f"{case_id}|{claim_id}|{clause_number}".encode("utf-8")
    return "EVID-" + hashlib.sha256(seed).hexdigest()[:20].upper()


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


class EvidenceGroundedAgentWorkflow:
    """Structured deterministic workflow based on Project 6 governance."""

    def __init__(
        self,
        *,
        repo_root: Path,
        schema_dir: Path,
        policy_path: Path,
        corpus_registry_path: Path,
    ) -> None:
        self.repo_root = repo_root
        self.schema_dir = schema_dir
        self.policy = json.loads(
            policy_path.read_text(encoding="utf-8")
        )
        self.corpus = RegisteredEvidenceCorpus(
            repo_root=repo_root,
            registry_path=corpus_registry_path,
        )

    def _trace(
        self,
        trace: list[dict[str, Any]],
        tool: str,
        status: str,
        reason_codes: list[str],
        sanitized_details: dict[str, Any],
    ) -> None:
        trace.append(
            {
                "sequence": len(trace) + 1,
                "tool": tool,
                "status": status,
                "reason_codes": reason_codes,
                "sanitized_details": sanitized_details,
            }
        )

    def _blocked_result(
        self,
        request: dict[str, Any],
        *,
        reason_code: str,
        status: str,
        trace: list[dict[str, Any]],
        missing_information: list[str],
    ) -> dict[str, Any]:
        required_action = (
            "escalate"
            if status == "escalated"
            else "abstain"
        )
        assessment = {
            "assessment_schema_version": "1.0.0",
            "case_id": request["case_id"],
            "claim_id": request["claim_id"],
            "evidence_ids": [],
            "sufficiency_status": "insufficient",
            "conflict_status": "none",
            "evidence_score": 0.0,
            "missing_information": missing_information,
            "reason_codes": [reason_code],
            "required_action": required_action,
        }
        result = {
            "result_schema_version": "1.0.0",
            "request_id": request["request_id"],
            "case_id": request["case_id"],
            "claim_id": request["claim_id"],
            "response_status": status,
            "route": (
                "qualified_human_review"
                if status == "escalated"
                else "fail_closed"
            ),
            "human_review_required": True,
            "reviewer_role": self.policy["required_reviewer_role"],
            "supported_observation": None,
            "evidence_items": [],
            "assessment": assessment,
            "reason_codes": sorted(
                {reason_code, "HUMAN_REVIEW_REQUIRED"}
            ),
            "tool_trace": trace,
            "limitations": [
                _limitation(
                    reason_code,
                    missing_information[0],
                    "Use a qualified reviewer and approved evidence path.",
                )
            ],
            "external_actions_performed": 0,
            "production_boundary": self.policy[
                "production_boundary"
            ],
        }
        validate_artifact(
            assessment,
            "evidence_assessment.schema.json",
            self.schema_dir,
        )
        validate_artifact(
            result,
            "evidence_workflow_result.schema.json",
            self.schema_dir,
        )
        return result

    def run(
        self,
        request: dict[str, Any],
        *,
        upstream_reason_codes: list[str] | None = None,
    ) -> WorkflowExecution:
        validate_artifact(
            request,
            "evidence_workflow_request.schema.json",
            self.schema_dir,
        )
        trace: list[dict[str, Any]] = []
        text = request["request_text"]

        if any(pattern.search(text) for pattern in PROMPT_INJECTION_PATTERNS):
            self._trace(
                trace,
                "preflight_screen",
                "blocked",
                ["PROMPT_INJECTION_DETECTED"],
                {"request_id": request["request_id"]},
            )
            return WorkflowExecution(
                self._blocked_result(
                    request,
                    reason_code="PROMPT_INJECTION_DETECTED",
                    status="failed_closed",
                    trace=trace,
                    missing_information=[
                        "The request attempted to override fixed workflow rules."
                    ],
                )
            )

        if any(pattern.search(text) for pattern in PRIVACY_PATTERNS):
            self._trace(
                trace,
                "preflight_screen",
                "blocked",
                ["PRIVACY_SENSITIVE_INPUT"],
                {"request_id": request["request_id"]},
            )
            return WorkflowExecution(
                self._blocked_result(
                    request,
                    reason_code="PRIVACY_SENSITIVE_INPUT",
                    status="failed_closed",
                    trace=trace,
                    missing_information=[
                        "Sensitive or credential-like content must not enter the evidence workflow."
                    ],
                )
            )

        if any(pattern.search(text) for pattern in OUT_OF_SCOPE_PATTERNS):
            self._trace(
                trace,
                "preflight_screen",
                "blocked",
                ["SCOPE_OUT_OF_BOUNDS"],
                {"request_id": request["request_id"]},
            )
            return WorkflowExecution(
                self._blocked_result(
                    request,
                    reason_code="SCOPE_OUT_OF_BOUNDS",
                    status="escalated",
                    trace=trace,
                    missing_information=[
                        "The request seeks a prohibited legal, approval, or authority decision."
                    ],
                )
            )

        self._trace(
            trace,
            "preflight_screen",
            "succeeded",
            [],
            {
                "retrieval_mode": request["retrieval_mode"],
                "consequential_use": request["consequential_use"],
            },
        )

        candidates: list[dict[str, Any]] = []
        if request["retrieval_mode"] == "exact":
            clause_number = request["exact_clause_number"]
            if not clause_number:
                self._trace(
                    trace,
                    "retrieve_exact_clause",
                    "blocked",
                    ["EXACT_CITATION_REQUIRED"],
                    {},
                )
                return WorkflowExecution(
                    self._blocked_result(
                        request,
                        reason_code="EXACT_CITATION_REQUIRED",
                        status="failed_closed",
                        trace=trace,
                        missing_information=[
                            "Exact retrieval requires a clause number."
                        ],
                    )
                )

            record = self.corpus.exact_lookup(clause_number)
            if record is None:
                self._trace(
                    trace,
                    "retrieve_exact_clause",
                    "blocked",
                    ["CLAUSE_NOT_FOUND", "EXACT_CITATION_REQUIRED"],
                    {
                        "requested_clause": clause_number,
                        "semantic_fallback_used": False,
                    },
                )
                return WorkflowExecution(
                    self._blocked_result(
                        request,
                        reason_code="CLAUSE_NOT_FOUND",
                        status="failed_closed",
                        trace=trace,
                        missing_information=[
                            "The exact requested clause is not present in the registered corpus; semantic substitution is prohibited."
                        ],
                    )
                )
            candidates = [
                {
                    "record": record,
                    "relevance_score": 1.0,
                    "retrieval_method": "exact_lookup",
                }
            ]
            self._trace(
                trace,
                "retrieve_exact_clause",
                "succeeded",
                [],
                {
                    "requested_clause": clause_number,
                    "records_returned": 1,
                },
            )
        else:
            scored = self.corpus.semantic_search(
                text,
                top_k=request["top_k"],
                minimum_score=self.policy[
                    "minimum_semantic_relevance"
                ],
            )
            if not scored:
                self._trace(
                    trace,
                    "search_official_corpus",
                    "warned",
                    ["SEARCH_NO_RESULTS"],
                    {"records_returned": 0},
                )
                return WorkflowExecution(
                    self._blocked_result(
                        request,
                        reason_code="SEARCH_NO_RESULTS",
                        status="abstained",
                        trace=trace,
                        missing_information=[
                            "No registered evidence record met the semantic retrieval threshold."
                        ],
                    )
                )
            candidates = [
                {
                    **item,
                    "retrieval_method": "semantic_search",
                }
                for item in scored
            ]
            self._trace(
                trace,
                "search_official_corpus",
                "succeeded",
                [],
                {
                    "records_returned": len(candidates),
                    "top_score": candidates[0]["relevance_score"],
                },
            )

        evidence_items: list[dict[str, Any]] = []
        validation_reasons: set[str] = set()
        for candidate in candidates:
            record = candidate["record"]
            claimed_title = request["claimed_title"]
            title_valid = (
                claimed_title is None
                or _normalize_title(claimed_title)
                == _normalize_title(record["title"])
            )
            metadata_valid = (
                title_valid
                and record["fac_number"]
                == self.corpus.registry["fac_number"]
                and record["fac_effective_date"]
                == self.corpus.registry["fac_effective_date"]
                and record["approved_for_use"]
                and not record["reserved"]
            )
            reason_codes = []
            if not title_valid:
                reason_codes.append("TITLE_MISMATCH")
                validation_reasons.add("TITLE_MISMATCH")
            if (
                record["fac_number"]
                != self.corpus.registry["fac_number"]
                or record["fac_effective_date"]
                != self.corpus.registry["fac_effective_date"]
            ):
                reason_codes.append("SOURCE_VERSION_UNVERIFIED")
                validation_reasons.add("SOURCE_VERSION_UNVERIFIED")
            if not reason_codes:
                reason_codes.append("SUPPORTED_WITH_EVIDENCE")

            supports_claim = (
                metadata_valid
                and candidate["relevance_score"]
                >= (
                    1.0
                    if candidate["retrieval_method"] == "exact_lookup"
                    else self.policy["minimum_semantic_relevance"]
                )
            )
            item = {
                "evidence_schema_version": "1.0.0",
                "evidence_id": _evidence_id(
                    request["case_id"],
                    request["claim_id"],
                    record["clause_number"],
                ),
                "case_id": request["case_id"],
                "claim_id": request["claim_id"],
                "source": {
                    "source_id": record["record_id"],
                    "source_type": "frozen_snapshot",
                    "source_location": record["snapshot_path"],
                    "retrieved_at": record["retrieved_at"],
                    "snapshot_date": record["snapshot_date"],
                    "sha256": record["snapshot_sha256"],
                    "approved_for_use": record["approved_for_use"],
                    "approval_basis": record["approval_basis"],
                    "notes": (
                        "Representative official-source subset; review the current official page before consequential use."
                    ),
                },
                "citation": {
                    "citation_text": (
                        f"FAR {record['clause_number']} "
                        f"{record['title']} ({record['clause_date']})"
                    ),
                    "source_locator": record["source_url"],
                    "clause_number": record["clause_number"],
                    "section_heading": record["title"],
                },
                "quoted_or_paraphrased_text": record["summary"],
                "retrieval_method": candidate["retrieval_method"],
                "metadata_valid": metadata_valid,
                "citation_valid": True,
                "relevance_score": candidate["relevance_score"],
                "supports_claim": supports_claim,
                "conflicts_with_claim": False,
                "freshness_status": "current",
                "validation_reason_codes": reason_codes,
                "limitations": [
                    _limitation(
                        "REPRESENTATIVE_SUBSET_ONLY",
                        (
                            "The registered corpus is a representative three-record "
                            "subset rather than the complete FAR Part 52 corpus."
                        ),
                        (
                            "Review the current official Acquisition.gov clause and "
                            "complete acquisition context before consequential use."
                        ),
                    ),
                    _limitation(
                        "APPLICABILITY_NOT_DETERMINED",
                        (
                            "Record retrieval and metadata validation do not determine "
                            "whether the clause applies to a specific acquisition."
                        ),
                        "Route applicability and legal interpretation to a qualified reviewer.",
                    ),
                ],
            }
            validate_artifact(
                item,
                "evidence_item.schema.json",
                self.schema_dir,
            )
            evidence_items.append(item)

        self._trace(
            trace,
            "validate_clause_metadata",
            (
                "warned"
                if validation_reasons
                else "succeeded"
            ),
            sorted(validation_reasons),
            {
                "records_validated": len(evidence_items),
                "metadata_valid_count": sum(
                    item["metadata_valid"] for item in evidence_items
                ),
            },
        )

        valid_support = [
            item
            for item in evidence_items
            if item["metadata_valid"]
            and item["citation_valid"]
            and item["supports_claim"]
            and not item["conflicts_with_claim"]
        ]
        evidence_score = (
            round(
                sum(item["relevance_score"] for item in valid_support)
                / len(valid_support),
                6,
            )
            if valid_support
            else 0.0
        )
        sufficient = (
            len(valid_support)
            >= self.policy["minimum_evidence_items"]
            and evidence_score
            >= self.policy["minimum_evidence_score"]
            and not validation_reasons
        )
        upstream_reason_codes = sorted(
            set(upstream_reason_codes or [])
        )
        mandatory_escalation = (
            request["consequential_use"]
            or request["source_domain"] == "public_sector"
            or bool(
                {"MODEL_DOMAIN_SHIFT", "MODEL_INPUT_TRUNCATED"}
                & set(upstream_reason_codes)
            )
        )

        if sufficient:
            assessment_reasons = ["SUPPORTED_WITH_EVIDENCE"]
            sufficiency_status = "sufficient"
            required_action = (
                "escalate" if mandatory_escalation else "continue"
            )
            response_status = (
                "escalated" if mandatory_escalation else "supported"
            )
            route = (
                "qualified_human_review"
                if mandatory_escalation
                else "continue_with_evidence"
            )
            supported_observation = (
                f"Registered evidence identifies FAR "
                f"{valid_support[0]['citation']['clause_number']} as "
                f"{valid_support[0]['citation']['section_heading']} and supports "
                "only the bounded subject summary preserved in the evidence item."
            )
        else:
            assessment_reasons = sorted(
                validation_reasons or {"EVIDENCE_INSUFFICIENT"}
            )
            sufficiency_status = "insufficient"
            required_action = "escalate"
            response_status = "escalated"
            route = "qualified_human_review"
            supported_observation = None

        if mandatory_escalation:
            assessment_reasons = sorted(
                set(assessment_reasons)
                | {"HUMAN_REVIEW_REQUIRED"}
                | (
                    set(upstream_reason_codes)
                    & {"MODEL_DOMAIN_SHIFT", "MODEL_INPUT_TRUNCATED"}
                )
            )

        assessment = {
            "assessment_schema_version": "1.0.0",
            "case_id": request["case_id"],
            "claim_id": request["claim_id"],
            "evidence_ids": [
                item["evidence_id"] for item in evidence_items
            ],
            "sufficiency_status": sufficiency_status,
            "conflict_status": "none",
            "evidence_score": evidence_score,
            "missing_information": (
                []
                if sufficient
                else [
                    "Validated evidence directly supporting the bounded claim is incomplete or mismatched."
                ]
            ),
            "reason_codes": assessment_reasons,
            "required_action": required_action,
        }
        validate_artifact(
            assessment,
            "evidence_assessment.schema.json",
            self.schema_dir,
        )
        self._trace(
            trace,
            "assess_evidence_sufficiency",
            (
                "succeeded"
                if sufficient
                else "warned"
            ),
            assessment_reasons,
            {
                "evidence_score": evidence_score,
                "sufficient": sufficient,
                "required_action": required_action,
            },
        )

        result = {
            "result_schema_version": "1.0.0",
            "request_id": request["request_id"],
            "case_id": request["case_id"],
            "claim_id": request["claim_id"],
            "response_status": response_status,
            "route": route,
            "human_review_required": True,
            "reviewer_role": self.policy["required_reviewer_role"],
            "supported_observation": supported_observation,
            "evidence_items": evidence_items,
            "assessment": assessment,
            "reason_codes": sorted(
                set(assessment_reasons)
                | {"HUMAN_REVIEW_REQUIRED"}
            ),
            "tool_trace": trace,
            "limitations": [
                _limitation(
                    "DECISION_SUPPORT_ONLY",
                    (
                        "The workflow retrieves and validates bounded evidence; "
                        "it does not issue legal, procurement, approval, or final decisions."
                    ),
                    "Use a qualified reviewer with the complete current source and acquisition context.",
                ),
                _limitation(
                    "REPRESENTATIVE_SUBSET_ONLY",
                    (
                        "P4-04 validates a representative three-record FAR subset, "
                        "not the full Project 6 corpus or live FAR."
                    ),
                    "Reintegrate and revalidate the complete approved corpus before broader use.",
                ),
            ],
            "external_actions_performed": 0,
            "production_boundary": self.policy[
                "production_boundary"
            ],
        }
        validate_artifact(
            result,
            "evidence_workflow_result.schema.json",
            self.schema_dir,
        )
        return WorkflowExecution(result)
