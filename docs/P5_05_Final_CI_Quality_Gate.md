# P5-05 — Final CI Quality Gate

> **P6-02 historical-record notice (2026-08-08):** This is a point-in-time CI/freeze record. Later overlays preserve it as historical evidence while the live gate verifies the allowed overlay chain.

The final workflow is continuous integration only. It has read-only repository
permissions and performs no deployment, publishing, release, purchase, proposal
submission, staffing commitment, or other external write operation.

## Maintenance change

```text
actions/upload-artifact@v4
```

was replaced with:

```text
actions/upload-artifact@v7
```

The workflow validates P5-01 through P5-05, generates non-secret hosted-run
metadata, and retains the final evaluation evidence for 30 days.

## Completion evidence

P5-05 closes when the updated workflow succeeds on `main` and retains at least
one artifact without the prior Node.js 20 deprecation annotation.
