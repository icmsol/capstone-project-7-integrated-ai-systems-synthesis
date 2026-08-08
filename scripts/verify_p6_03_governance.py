#!/usr/bin/env python3
"""Verify P6-03 governance, ethics, risk, oversight, records, and production-boundary evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = ROOT / "outputs/evaluation/p6_03"

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    risks = read_csv(DOCS / "P6_03_Risk_Register.csv")
    safeguards = read_csv(DOCS / "P6_03_Safeguard_Matrix.csv")
    records = read_csv(DOCS / "P6_03_Records_Expectations.csv")
    gates = read_csv(DOCS / "P6_03_Production_Readiness_Gates.csv")
    policy = json.loads((ROOT / "config/system/safeguard_policy.json").read_text(encoding="utf-8"))
    roles = json.loads((ROOT / "config/profiles/icm_reviewer_roles.json").read_text(encoding="utf-8"))
    summary = json.loads((OUT / "governance_risk_summary.json").read_text(encoding="utf-8"))

    if len(risks) != 20:
        raise RuntimeError(f"Expected 20 major risks, found {len(risks)}")
    required_risk_fields = [
        "risk_statement", "ethical_or_operational_impact", "existing_controls",
        "accountable_owner", "required_human_oversight", "residual_risk",
        "residual_risk_statement", "status",
    ]
    for row in risks:
        for field in required_risk_fields:
            if not row.get(field, "").strip():
                raise RuntimeError(f"{row.get('risk_id')} missing {field}")

    control_ids = {c["control_id"] for c in policy["controls"]}
    if len(control_ids) != 30:
        raise RuntimeError("Fixed safeguard count changed.")
    if {row["control_id"] for row in safeguards} != control_ids:
        raise RuntimeError("P6-03 safeguard matrix does not cover all 30 fixed controls.")
    if any(row["organization_override_permitted"] != "false" for row in safeguards):
        raise RuntimeError("A fixed safeguard is represented as organization-overridable.")

    role_ids = {r["role_id"] for r in roles["roles"]}
    if role_ids != {"RR-01","RR-02","RR-03","RR-04","RR-05","RR-06","RR-07"}:
        raise RuntimeError("Configured ICM reviewer-role set changed.")
    if roles.get("constraint") != "No AI component is an authorized final decision-maker.":
        raise RuntimeError("Human-authority constraint changed.")

    oversight = (DOCS / "P6_03_Human_Oversight_and_Accountability.md").read_text(encoding="utf-8")
    for role_id in sorted(role_ids):
        if role_id not in oversight:
            raise RuntimeError(f"Human-oversight document missing {role_id}")
    if "No AI component is an authorized final decision-maker." not in oversight:
        raise RuntimeError("Human-authority statement missing.")

    records_doc = (DOCS / "P6_03_Records_Audit_and_Retention_Expectations.md").read_text(encoding="utf-8")
    if "does not prescribe a numeric retention period" not in records_doc:
        raise RuntimeError("Records document must not invent a retention period.")
    if len(records) < 10:
        raise RuntimeError("Records expectation inventory is incomplete.")

    prod = (DOCS / "P6_03_Production_Readiness_Boundary.md").read_text(encoding="utf-8")
    if "NOT PRODUCTION READY" not in prod:
        raise RuntimeError("Production boundary is not explicit.")
    if len(gates) != 15:
        raise RuntimeError(f"Expected 15 production gates, found {len(gates)}")
    if not any(row["current_status"] == "NOT SATISFIED" for row in gates):
        raise RuntimeError("Production gate inventory incorrectly implies readiness.")

    if summary["candidate_id"] != "PROJECT7-SUBMISSION-CANDIDATE-v1.0.0":
        raise RuntimeError("Frozen candidate identity changed.")
    if summary["major_risks"] != 20 or summary["fixed_safeguards"] != 30:
        raise RuntimeError("Governance summary counts changed.")
    if summary["configured_icm_reviewer_roles"] != 7:
        raise RuntimeError("Governance reviewer-role count changed.")
    if summary["production_ready"]:
        raise RuntimeError("Governance summary incorrectly claims production readiness.")
    if summary["external_actions_performed"] != 0:
        raise RuntimeError("External-action boundary changed.")

    print("Major governance/ethical/operational risks: 20")
    print("Risks with owner, control, oversight, and residual statement: 20/20 PASS")
    print("Fixed safeguards mapped: 30/30 PASS")
    print("Configured ICM reviewer roles documented: 7/7 PASS")
    print(f"Records expectation classes: {len(records)}")
    print("Production-readiness gates: 15")
    print("Production-ready claim: FALSE / PASS")
    print("External actions performed: 0")
    print("P6-03 governance verification: PASS")

if __name__ == "__main__":
    main()
