# P5-12 Final Submission-Candidate Freeze

## Freeze decision

**Candidate:** `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0`  
**Status:** Frozen  
**Freeze date:** 2026-08-08  
**Source hosted CI:** Project 7 Quality Gate run #15 — PASS on commit `18faa3a` (41 seconds; 1 artifact)

The final technical/evaluation submission candidate is frozen after successful hosted regression testing and targeted operator visual acceptance.

## Evidence chain

1. `PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.0` — P5-05 frozen evaluation baseline.
2. `PROJECT7-FINAL-EVALUATION-BASELINE-v1.0.1` — P5-06 explicitly versioned manual-acceptance correction.
3. P5-06 historical overlay `1.0.1` — retained unchanged.
4. Active post-freeze overlay `1.0.2` — governs the P5-12 ICM alignment configuration correction.
5. `PROJECT7-SUBMISSION-CANDIDATE-v1.0.0` — final operator-accepted technical/evaluation candidate.

## Final operator acceptance

### P5-10 — same RFO
RFO 3485A completed through the no-code operator interface, including a separate authorized human disposition and successful bundle export/restore.

### P5-11 — fresh request
Covered California RFP 2026-01 completed through the same interface without code changes. The test surfaced alignment/model/presentation findings while safeguards continued to require human review and zero external actions.

### P5-12 — targeted visual regression
The final visual regression passed:

- generic `Request for Proposal` metadata no longer creates an `RFP and RFQ Preparation` capability match;
- Covered California renders as `weak_alignment`, score `0.3333`, with only `ICM-PM-004 — Risk, Issue, Dependency, and Change Control`;
- the operator explicitly states that domain-shift confidence does not establish semantic correctness;
- the packet is table-free/readable in Colab;
- estimated value renders as `$12,500,000 USD`;
- evidence remains fail-safe and the recommendation remains nonbinding.

## Accepted limitations

The frozen Project 4 model is not retrained. The observed high-confidence public-sector semantic misclassification is retained as bounded-model error-analysis evidence. `MODEL_DOMAIN_SHIFT` forces escalation and the UI explicitly prevents confidence from being interpreted as semantic or legal correctness.

The evidence corpus is bounded. No retrieval result is automatically treated as sufficient support. The exploratory fresh-request retrieval count differed between the P5-11 smoke test (one insufficient item) and the P5-12 visual regression (zero items), while both remained 0/3 sufficient and escalated; that count is not a frozen benchmark metric.

## Change control

Technical, configuration, model, safeguard, schema, operator-interface, test, or evaluation changes after this freeze require an explicitly new candidate version.

Phase 6 may update reviewer documentation and defense materials (`README.md`, appropriate `docs/`, `reports/`, `presentation/`, and paper/defense `figures/`) provided those edits do not alter frozen technical/evaluation artifacts.

## Verification

```bash
python scripts/verify_p5_12_final_submission_candidate.py
python -m unittest tests.test_p5_12_final_submission_candidate -v
```

The GitHub quality gate also runs these checks.

## Production boundary

Controlled capstone prototype; recommendations are nonbinding; autonomous external actions are prohibited; final authority remains human.
