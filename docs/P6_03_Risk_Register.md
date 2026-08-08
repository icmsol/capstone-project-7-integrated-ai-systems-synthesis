# P6-03 — Governance Risk Register

The canonical machine-readable register is [`P6_03_Risk_Register.csv`](P6_03_Risk_Register.csv).

| ID | Domain | Inherent | Residual | Owner | Status |
|---|---|---|---|---|---|
| `GR-01` | human_authority | Critical | **Low** | Executive Authority (RR-02) | Controlled in prototype |
| `GR-02` | source_provenance | High | **Medium** | Business Development or Pursuit Lead (RR-01) | Controlled with accepted human-input limitation |
| `GR-03` | alignment_interpretation | High | **Medium** | Business Development or Pursuit Lead (RR-01) | Controlled in prototype |
| `GR-04` | historical_data | High | **Low** | Business Development or Pursuit Lead (RR-01) | Controlled in prototype |
| `GR-05` | model_integrity | High | **Low** | Technical Reviewer | Controlled in prototype |
| `GR-06` | model_validity | Critical | **High** | Contracts or Procurement Specialist (RR-03) / Legal Counsel (RR-04) | Accepted limitation / production blocker |
| `GR-07` | document_completeness | Critical | **High** | Contracts or Procurement Specialist (RR-03) | Accepted limitation / production blocker |
| `GR-08` | evidence_quality | Critical | **High** | Contracts or Procurement Specialist (RR-03) | Accepted limitation / production blocker |
| `GR-09` | recommendation_quality | High | **Low** | Business Development or Pursuit Lead (RR-01) | Controlled in prototype |
| `GR-10` | privacy_security | Critical | **Medium** | Security or Privacy Reviewer (RR-05) | Controlled in prototype / production blocker |
| `GR-11` | prompt_injection | Critical | **Low** | Security or Privacy Reviewer (RR-05) | Controlled in prototype |
| `GR-12` | configuration_governance | Critical | **Low** | Project Owner / Executive Authority (RR-02) | Controlled in prototype |
| `GR-13` | reviewer_authorization | Critical | **Medium** | Executive Authority (RR-02) | Controlled in prototype / production blocker |
| `GR-14` | external_action | Critical | **Low** | Executive Authority (RR-02) | Controlled in prototype |
| `GR-15` | audit_reproducibility | High | **Low** | Technical Reviewer | Controlled in prototype / production blocker |
| `GR-16` | ethics_conflict_of_interest | High | **Medium** | Executive Authority (RR-02) / Legal Counsel (RR-04) | Controlled with human/legal review |
| `GR-17` | fairness_strategic_bias | Medium | **Medium** | Business Development or Pursuit Lead (RR-01) | Managed residual risk |
| `GR-18` | production_claims | Critical | **Low** | Project Owner | Controlled in documentation |
| `GR-19` | records_management | High | **High** | Project Owner / Legal Counsel (RR-04) | Production blocker |
| `GR-20` | production_security | Critical | **High** | Security or Privacy Reviewer (RR-05) / Project Owner | Production blocker |

## Interpretation

A High residual risk is retained where the prototype boundary genuinely leaves a material unresolved production concern. This is intentional and prevents the governance documentation from overstating readiness.

Every row in the CSV includes the full risk statement, impact, existing controls, accountable owner, required human oversight, and residual-risk statement.
