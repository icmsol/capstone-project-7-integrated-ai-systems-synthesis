# Data

Project 7 separates preserved inputs, derived data, reference assets, implementation fixtures, and frozen evaluation scenarios.

## Structure

```text
data/
  frozen_scenarios/   Legacy/frozen-scenario navigation retained for repository continuity
  implementation/     Controlled implementation inputs grouped by activity (P4/P5)
  processed/          Generated normalized or derived data
  raw/                Preserved approved/public source inputs
  reference/
    far/              Frozen FAR reference assets used by the bounded evidence workflow
    project2/         Frozen Project 2 historical procurement reference assets
  scenarios/
    frozen/           Versioned executable scenario sets and shared fixtures
```

The active frozen evaluation lineage is documented in the [P5-05 Final Evaluation Freeze](../docs/P5_05_Final_Evaluation_Freeze.md) and the [P5-12 Final Submission-Candidate Freeze](../docs/P5_12_Final_Submission_Candidate_Freeze.md).

## Data Handling Rules

- Do not commit credentials, secrets, confidential client material, or unapproved personal information.
- Preserve public/reference inputs with provenance and checksums.
- Treat processed outputs as reproducible derivatives, not new sources of truth.
- Do not silently modify frozen scenario inputs after evaluation freeze.
- Treat the FAR evidence set as a bounded registered corpus, not as a claim of complete current acquisition-law coverage.

See [Raw Data](raw/README.md), [Processed Data](processed/README.md), and [Frozen Scenarios](frozen_scenarios/README.md).
