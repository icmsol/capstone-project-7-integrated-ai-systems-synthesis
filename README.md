# Configurable Small-Business Opportunity-to-Contract Intelligence and Assurance Framework

**ICM Solutions Reference Implementation**

This repository supports Capstone Project 7 — Industry Integrated AI Systems Synthesis. It will integrate prior capstone work into a configurable, evidence-grounded decision-support framework for small public-sector consulting businesses.

## Current Status

Phase 1 repository and configuration scaffold.

## Purpose

The framework will help an authorized human reviewer:

1. intake and validate a public-sector opportunity;
2. compare the opportunity with an active organization's configured services and capabilities;
3. attach historical procurement and staffing context;
4. triage selected solicitation or contract passages;
5. retrieve and validate authoritative supporting evidence;
6. generate a nonbinding, evidence-linked recommendation;
7. route the recommendation and supporting packet to an authorized human decision-maker.

The system may recommend. It may not approve, execute, externally communicate, or represent a recommendation as the organization's final decision.

## Configurable Design

Organization-specific business knowledge is loaded from JSON and CSV files. Switching from ICM Solutions to another small business must not require model retraining or source-code modification.

Configurable content includes:

- organization identity and markets;
- services and capabilities;
- positive and exclusion terms;
- procurement preferences;
- staffing families;
- reviewer roles;
- recommendation thresholds.

The following safeguards are framework-controlled and cannot be disabled through an organization profile:

- evidence traceability;
- counterevidence and missing-information disclosure;
- abstention when evidence is insufficient;
- mandatory escalation;
- audit logging;
- privacy and secrets protection;
- explicit human approval;
- prohibition of autonomous external actions.

## Prior-Project Integration

- **Project 1:** opportunity intake, normalization, and provenance
- **Project 2:** service alignment, statistical context, and staffing-family context
- **Project 4:** bounded clause-theme triage, subject to verified inference assets
- **Project 6:** evidence retrieval, deterministic validation, state, safeguards, audit, and escalation
- **Projects 3 and 5:** bounded modeling, failure-mode, evaluation, and responsible-AI evidence

## Repository Structure

```text
audit/                      Audit manifests and traceability records
config/
  profiles/                 ICM and fictional organization configurations
  schemas/                  JSON Schema validation contracts
  system/                   Fixed framework safeguards
  templates/                Blank tailoring templates
data/
  raw/                      Preserved source inputs
  processed/                Generated normalized data
  frozen_scenarios/         Versioned evaluation scenarios
docs/                       Architecture, use cases, governance, and traceability
figures/                    Paper and presentation visuals
notebooks/                  Executable Colab notebook
outputs/
  case_packets/             Integrated decision-support packets
  evaluation/               Metrics and failure-analysis outputs
presentation/               Mentor presentation and defense materials
reports/                    Reflective synthesis paper and supporting reports
src/                        Reusable Python modules
tests/                      Configuration, safeguard, and workflow tests
```

## Configuration Entry Point

The initial reference implementation uses:

```text
config/profiles/icm_solutions.json
```

The portability test will use:

```text
config/profiles/fictional_small_business.json
```

## Production Boundary

This is a controlled capstone prototype. It is not a production procurement, legal, compliance, security, financial, staffing, or contract-approval system.
