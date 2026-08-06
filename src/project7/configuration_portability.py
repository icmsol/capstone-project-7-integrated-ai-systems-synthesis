"""Configuration-only portability comparison for Project 7."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .profile_loader import load_organization_profile
from .schema_validation import validate_artifact
from .service_alignment import assess_service_alignment

PRODUCTION_BOUNDARY = (
    "Controlled capstone prototype; nonbinding recommendations only; "
    "no autonomous external action; final human authority required."
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def derive_screening_recommendation(
    *,
    alignment: dict[str, Any],
    thresholds: dict[str, Any],
    reviewer_roles: dict[str, Any],
) -> dict[str, Any]:
    """Map transparent alignment score to a nonbinding profile threshold outcome."""

    score = float(alignment["alignment_score"])
    selected: dict[str, Any] | None = None
    for outcome in thresholds["outcomes"]:
        if outcome["minimum_score"] <= score <= outcome["maximum_score"]:
            selected = outcome
            break
    if selected is None:
        raise RuntimeError(f"No configured threshold outcome for score {score}.")

    roles = reviewer_roles["roles"]
    pursuit_reviewer = roles[0]
    final_authority = next(
        (
            role
            for role in roles
            if "executive" in role["role_name"].lower()
            or any(
                "final pursuit decision" in authority.lower()
                for authority in role.get("authorities", [])
            )
        ),
        roles[-1],
    )
    return {
        "recommendation_code": selected["code"],
        "recommendation_label": selected["label"],
        "recommendation_strength": score,
        "nonbinding_disclosure": (
            "Configuration-driven screening recommendation only; not a final "
            "pursuit decision, eligibility determination, capacity commitment, "
            "legal opinion, or award-probability estimate."
        ),
        "required_human_reviewer": {
            "role_id": pursuit_reviewer["role_id"],
            "role_name": pursuit_reviewer["role_name"],
        },
        "final_authority": {
            "role_id": final_authority["role_id"],
            "role_name": final_authority["role_name"],
        },
        "final_decision": None,
        "external_actions_performed": 0,
    }


def run_portability_comparison(
    *,
    repo_root: Path,
    opportunities_path: Path,
    output_directory: Path,
    audit_output_path: Path,
) -> dict[str, Any]:
    schema_dir = repo_root / "config" / "schemas"
    profiles = [
        repo_root / "config" / "profiles" / "icm_solutions.json",
        repo_root / "config" / "profiles" / "fictional_small_business.json",
    ]
    alignment_policy_path = (
        repo_root / "config" / "system" / "service_alignment_policy.json"
    )
    alignment_policy = read_json(alignment_policy_path)
    opportunity_artifact = read_json(opportunities_path)
    source_path = repo_root / "src" / "project7" / "configuration_portability.py"
    source_hash_before = sha256_file(source_path)

    runs: list[dict[str, Any]] = []
    audit_events: list[dict[str, Any]] = []
    sequence = 0
    for opportunity in opportunity_artifact["opportunities"]:
        validate_artifact(
            opportunity,
            "opportunity_record.schema.json",
            schema_dir,
        )
        for profile_path in profiles:
            sequence += 1
            bundle = load_organization_profile(
                profile_path,
                schema_dir=schema_dir,
            )
            alignment = assess_service_alignment(
                opportunity,
                bundle,
                alignment_policy,
                schema_dir=schema_dir,
            )
            recommendation = derive_screening_recommendation(
                alignment=alignment,
                thresholds=bundle.recommendation_thresholds,
                reviewer_roles=bundle.reviewer_roles,
            )
            safeguard_path = profile_path.parent / bundle.profile[
                "fixed_safeguards_file"
            ]
            run = {
                "opportunity_id": opportunity["opportunity_id"],
                "case_id": opportunity["case_id"],
                "opportunity_title": opportunity["title"],
                "organization_id": bundle.profile["organization_id"],
                "organization_name": bundle.profile["organization_name"],
                "fictional_profile": bundle.profile["fictional"],
                "profile_path": profile_path.relative_to(repo_root).as_posix(),
                "profile_version": bundle.profile["profile_version"],
                "alignment": alignment,
                "screening_recommendation": recommendation,
                "invariants": {
                    "opportunity_sha256": hashlib.sha256(
                        json.dumps(
                            opportunity,
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode("utf-8")
                    ).hexdigest(),
                    "executable_source_sha256": source_hash_before,
                    "alignment_policy_sha256": sha256_file(alignment_policy_path),
                    "fixed_safeguards_sha256": sha256_file(safeguard_path),
                    "organization_profile_schema_sha256": sha256_file(
                        schema_dir / "organization_profile.schema.json"
                    ),
                    "service_alignment_schema_sha256": sha256_file(
                        schema_dir / "service_alignment.schema.json"
                    ),
                    "fixed_safeguards_version": bundle.fixed_safeguards[
                        "artifact_version"
                    ],
                    "human_final_decision_required": bundle.fixed_safeguards[
                        "controls"
                    ]["human_final_decision_required"],
                    "autonomous_external_actions_prohibited": bundle.fixed_safeguards[
                        "controls"
                    ]["autonomous_external_actions_prohibited"],
                },
            }
            runs.append(run)
            audit_events.append(
                {
                    "sequence": sequence,
                    "event_type": "configuration_portability_run_completed",
                    "case_id": opportunity["case_id"],
                    "organization_id": bundle.profile["organization_id"],
                    "profile_version": bundle.profile["profile_version"],
                    "alignment_label": alignment["alignment_label"],
                    "alignment_score": alignment["alignment_score"],
                    "recommendation_code": recommendation["recommendation_code"],
                    "final_decision_created": False,
                    "external_actions_performed": 0,
                }
            )

    comparisons: list[dict[str, Any]] = []
    for opportunity in opportunity_artifact["opportunities"]:
        relevant = [
            run
            for run in runs
            if run["opportunity_id"] == opportunity["opportunity_id"]
        ]
        by_org = {run["organization_id"]: run for run in relevant}
        icm = by_org["ICMSOL"]
        fictional = by_org["RCALABS"]
        comparisons.append(
            {
                "opportunity_id": opportunity["opportunity_id"],
                "opportunity_title": opportunity["title"],
                "icm_alignment_label": icm["alignment"]["alignment_label"],
                "icm_alignment_score": icm["alignment"]["alignment_score"],
                "icm_recommendation_code": icm["screening_recommendation"][
                    "recommendation_code"
                ],
                "fictional_alignment_label": fictional["alignment"][
                    "alignment_label"
                ],
                "fictional_alignment_score": fictional["alignment"][
                    "alignment_score"
                ],
                "fictional_recommendation_code": fictional[
                    "screening_recommendation"
                ]["recommendation_code"],
                "alignment_changed": (
                    icm["alignment"]["alignment_label"]
                    != fictional["alignment"]["alignment_label"]
                ),
                "recommendation_changed": (
                    icm["screening_recommendation"]["recommendation_code"]
                    != fictional["screening_recommendation"]["recommendation_code"]
                ),
                "source_code_unchanged": (
                    icm["invariants"]["executable_source_sha256"]
                    == fictional["invariants"]["executable_source_sha256"]
                ),
                "fixed_safeguards_unchanged": (
                    icm["invariants"]["fixed_safeguards_sha256"]
                    == fictional["invariants"]["fixed_safeguards_sha256"]
                ),
                "schemas_unchanged": (
                    icm["invariants"]["organization_profile_schema_sha256"]
                    == fictional["invariants"]["organization_profile_schema_sha256"]
                    and icm["invariants"]["service_alignment_schema_sha256"]
                    == fictional["invariants"]["service_alignment_schema_sha256"]
                ),
            }
        )

    source_hash_after = sha256_file(source_path)
    report = {
        "report_schema_version": "1.0.0",
        "report_id": "PROJECT7-P5-04-CONFIGURATION-PORTABILITY",
        "opportunity_count": len(opportunity_artifact["opportunities"]),
        "profile_count": len(profiles),
        "run_count": len(runs),
        "profile_runs": runs,
        "comparisons": comparisons,
        "invariant_summary": {
            "source_code_unchanged_between_profile_runs": (
                source_hash_before == source_hash_after
                and all(item["source_code_unchanged"] for item in comparisons)
            ),
            "fixed_safeguards_unchanged": all(
                item["fixed_safeguards_unchanged"] for item in comparisons
            ),
            "schemas_unchanged": all(item["schemas_unchanged"] for item in comparisons),
            "alignment_changed_for_every_opportunity": all(
                item["alignment_changed"] for item in comparisons
            ),
            "recommendation_changed_for_every_opportunity": all(
                item["recommendation_changed"] for item in comparisons
            ),
            "final_decisions_created": 0,
            "external_actions_performed": 0,
        },
        "production_boundary": PRODUCTION_BOUNDARY,
    }

    output_directory.mkdir(parents=True, exist_ok=True)
    audit_output_path.parent.mkdir(parents=True, exist_ok=True)
    (output_directory / "portability_comparison.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for run in runs:
        name = f"{run['case_id']}__{run['organization_id']}.json"
        (output_directory / name).write_text(
            json.dumps(run, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    audit_output_path.write_text(
        "".join(json.dumps(event, ensure_ascii=False) + "\n" for event in audit_events),
        encoding="utf-8",
    )
    return report
