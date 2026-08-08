# Configuration

This directory separates organization-specific business criteria from framework-controlled contracts, schemas, policies, and safeguards.

## Directory Structure

```text
config/
  contracts/      Component contracts and the contract registry
  profiles/       Organization profiles and linked CSV/JSON configuration
  schemas/        JSON Schema validation contracts
  system/         Framework policies, registries, safeguards, and freeze controls
  templates/      Blank configuration templates for another organization
```

## Profiles

The two included profiles are:

- [ICM Solutions](profiles/icm_solutions.json) — real reference implementation.
- [Redwood Civic Analytics](profiles/fictional_small_business.json) — explicitly fictional portability-test profile.

Each organization profile references separate artifacts for services, opportunity rules, staffing mappings, reviewer roles, and recommendation thresholds.

ICM configuration:

- [Service catalog](profiles/icm_service_catalog.csv)
- [Opportunity rules](profiles/icm_opportunity_rules.json)
- [Historical-context map](profiles/icm_historical_context_map.csv)
- [Staffing map](profiles/icm_staffing_map.csv)
- [Reviewer roles](profiles/icm_reviewer_roles.json)
- [Recommendation thresholds](profiles/icm_recommendation_thresholds.json)

The fictional profile has the corresponding `fictional_*` artifacts in the same directory.

## Contracts

[`contracts/`](contracts/) contains the component interface definitions plus the component contract registry. The implemented contract set covers profile loading, intake normalization, service alignment, historical context, passage selection, clause triage, evidence retrieval/validation, risk routing, recommendations, packet assembly, human disposition, audit writing, and orchestration.

See [Orchestration and Component Contracts](../docs/Orchestration_and_Component_Contracts.md).

## Schemas

[`schemas/`](schemas/) contains the JSON Schemas for opportunities, alignment, evidence, recommendations, case state, audit events, human disposition, evaluation/freeze artifacts, and related system contracts.

See [Shared Data Contracts](../docs/Shared_Data_Contracts.md).

## System-Controlled Configuration

[`system/`](system/) contains framework policies and registries, including:

- `fixed_safeguards.json`
- `safeguard_policy.json`
- `safeguard_reason_codes.json`
- `mandatory_review_triggers.json`
- `orchestration_policy.json`
- `recommendation_policy.json`
- `evidence_workflow_policy.json`
- `clause_triage_policy.json`
- `project4_model_registry.json`
- `final_evaluation_freeze_policy.json`
- scenario/evaluation indexes and version-control policies

Organization profiles do **not** have authority to disable fixed safeguards.

## Tailoring for Another Small Business

Start from [`templates/`](templates/), not by editing Python source.

1. Copy `organization_profile.template.json`.
2. Create a service catalog from `service_catalog.template.csv`.
3. Define opportunity screening rules.
4. Map service families to staffing families.
5. Define authorized reviewer roles.
6. Define organization-specific recommendation thresholds.
7. Point the organization profile to those files.
8. Validate the profile and linked artifacts.
9. Run the portability and regression tests before using the profile in the operator interface.

Do not modify `fixed_safeguards.json` merely to make an organization profile produce a desired recommendation.

## Version and Source Control

Configuration artifacts are versioned and checksum-governed in evaluation/freeze manifests. The final accepted technical/evaluation candidate is documented in:

- [Final submission-candidate manifest](../outputs/evaluation/p5_12/final_submission_candidate_manifest.json)
- [Strict inventory](../outputs/evaluation/p5_12/final_submission_candidate_strict_inventory.json)

Changes to frozen technical configuration after that candidate require explicit versioned change control.
