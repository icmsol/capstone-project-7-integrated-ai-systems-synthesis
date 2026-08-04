# Configuration

This directory separates organization-specific business criteria from fixed framework safeguards.

## Profiles

`profiles/` contains complete organization-specific configurations. The active profile references its service catalog, opportunity rules, staffing map, reviewer roles, and recommendation thresholds.

## Templates

`templates/` contains blank examples that another small business can tailor.

## Schemas

`schemas/` contains the JSON Schema used to validate organization profiles.

## System

`system/fixed_safeguards.json` contains responsible-AI controls that ordinary organization profiles cannot override.

## Versioning

Every configuration artifact must include or be associated with:

- an organization ID;
- a profile or artifact version;
- an effective date;
- a source or owner;
- a checksum in the run manifest.
