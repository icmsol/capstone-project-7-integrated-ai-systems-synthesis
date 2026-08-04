# P1-02 — Projects 1 and 2 Reusable Asset Review

## Decision Summary

Project 2 will provide the primary structured-data runtime foundation. Project 1 remains valuable as an earlier, simpler provenance and cleaning baseline, but its Cal eProcure-only ingestion and hard-coded ICM screen are superseded by Project 2 and the new configurable organization profile.

## Project 1

### Adapt

- `standardize_columns_and_text`
- deadline parsing and original-value retention
- one-table ingestion validation
- explicit record-group and source labeling

### Reference, but do not copy into runtime

- `ICM_SERVICE_RULES`
- `flag_icm_alignment`
- the one-year/current processed dataset
- the original raw exports and figures

The Project 1 screening rules will be retained as historical regression examples. Runtime matching will load positive phrases and exclusions from the active organization's service catalog.

## Project 2

### Adapt into runtime modules

- `parse_caleprocure`
- `parse_planetbids`
- `normalize_title`
- `normalize_status`
- `fiscal_year_label`
- `fiscal_quarter`
- the SHA-256 composite `record_key`
- exclusion-first classification behavior from `classify_title`
- explicit classification evidence through `classification_basis`

### Convert to configuration

- hard-coded `CATEGORY_RULES`
- hard-coded `EXCLUDE_PATTERNS`
- hard-coded Technology Delivery versus Advisory, Assurance & Change mapping

The configurable framework will load services, positive terms, exclusions, staffing families, reviewer roles, and recommendation thresholds from the active organization profile.

### Copy or derive for Project 7

- `analysis_summary.json` as frozen historical context
- `data_dictionary.csv` as the basis for the opportunity-record schema
- selected `classification_audit_sample.csv` rows as regression scenarios
- compact aggregates and selected cases derived from `icm_relevant_historical_bids.csv`
- selected, clearly dated cases from `current_public_procurement_snapshot.csv`

### Reference rather than duplicate

- the complete 29,646-record historical dataset
- all original raw exports
- Project 2's complete environment file
- all four original figures

## Key Boundary

Project 2 found 176 title-screened ICM-relevant opportunities among 29,646 historical records. Those classifications and the statistical results are directional historical evidence. They do not establish contract value, staffing hours, capacity, eligibility, scope fit, award probability, or a final pursuit decision.

## Planned Project 7 Modules

```text
src/opportunity_ingestion.py
src/opportunity_normalization.py
src/service_alignment.py
config/schemas/opportunity_record.schema.json
data/processed/project2_analysis_summary.json
data/processed/historical_service_context.csv
data/frozen_scenarios/project2_classification_regression.csv
audit/prior_project_source_registry.json
```

## Sources

- https://github.com/icmsol/ai-programming-foundations-project
- https://github.com/icmsol/Capstone-project-2-statistical-analysis
