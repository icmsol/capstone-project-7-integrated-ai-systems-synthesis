# Frozen Scenario Shared Fixtures

These shared fixtures support the original P3-03 `v1.0.0` frozen scenario package.

Important version context:

- `v1.0.0` is retained as historical evidence.
- Scenario-quality review identified corrections that were released as the `v1.0.1` scenario/evaluator package.
- The executed final evaluation uses the corrected lineage and does not rewrite the historical `v1.0.0` fixtures.
- Final evaluation/refinement results are frozen separately under [`../../../../../outputs/evaluation/`](../../../../../outputs/evaluation/).

Fixture rules:

- opportunity/document content is synthetic or explicitly identified as a controlled public/reference fixture;
- no credentials, confidential client information, or real personal information are intended to be included;
- fault-injection fixtures are evaluation controls, not claims about production failures;
- expected outcomes are controlled evaluation targets, not autonomous decisions.

See the [P3-04 v1.0.1 Correction and Evaluator Guide](../../../../../docs/P3_04_v1_0_1_Correction_and_Evaluator_Guide.md).
