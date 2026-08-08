# P6-03 — Human Oversight and Accountability

## Governing Principle

**No AI component is an authorized final decision-maker.**

The system may screen, triage, retrieve evidence, expose uncertainty, assemble a packet, and issue a nonbinding recommendation. Final organizational authority remains with an authorized human.

## ICM Reviewer Roles

| Role | Name | Configured authorities | Issue types | Final pursuit authority |
|---|---|---|---|---|
| `RR-01` | Business Development or Pursuit Lead | accept, modify, reject, defer, or escalate opportunity recommendation; make final bid/no-bid recommendation to executive authority where applicable | opportunity alignment; pursuit conditions; missing opportunity information | No — specialist/advisory authority within configured scope |
| `RR-02` | Executive Authority | make final pursuit decision; approve organizational commitments within delegated authority | final bid/no-bid; strategic risk; material commitment; production pilot approval | Yes — final pursuit decision |
| `RR-03` | Contracts or Procurement Specialist | interpret procurement process and contract-administration implications; recommend clarification or negotiation topics | solicitation terms; procurement path; contract vehicle; compliance matrix | No — specialist/advisory authority within configured scope |
| `RR-04` | Legal Counsel | provide legal interpretation and advice; approve legal position where authorized | indemnification; liability; intellectual property; legal dispute; regulatory interpretation | No — specialist/advisory authority within configured scope |
| `RR-05` | Security or Privacy Reviewer | assess security, privacy, and restricted-data obligations; approve or reject security or privacy approach where authorized | cybersecurity; privacy; confidential data; access control; incident obligations | No — specialist/advisory authority within configured scope |
| `RR-06` | Staffing or Delivery Lead | assess staffing feasibility; approve named staffing and delivery commitments where authorized | required labor categories; availability; delivery schedule; skills gap | No — specialist/advisory authority within configured scope |
| `RR-07` | Finance or Pricing Authority | approve rates, pricing, cost assumptions, and financial commitments | pricing; cost reasonableness; cash flow; financial risk; payment terms | No — specialist/advisory authority within configured scope |

The current ICM configuration places the final pursuit decision with **Executive Authority (RR-02)**. Specialist roles provide domain review and may recommend, condition, defer, reject, or escalate within their configured authority.

## Required Human Decision Sequence

1. The system completes bounded analysis and generates a **nonbinding** recommendation.
2. Mandatory specialist routes are displayed when triggered.
3. The qualified reviewer examines the original source, evidence sufficiency, unresolved issues, and limitations.
4. An authorized human records a disposition and rationale.
5. The system stores the human disposition **separately** from the original recommendation.
6. Any external communication, submission, acceptance, signature, purchase, staffing commitment, or other action occurs **outside** the AI workflow under normal organizational authority.

## Mandatory Review Triggers

- legal interpretation or contract enforceability
- privacy or restricted personal data
- cybersecurity or credential exposure
- pricing, financial commitment, or payment terms
- staffing commitment or named-person availability
- contract acceptance, rejection, or modification
- material conflicting evidence
- low-confidence or out-of-domain model output
- unverified or stale official source
- conflict of interest or ethical concern
- external communication, submission, or transaction
- production deployment or production-readiness claim

## Accountability Rules

- Reviewer identity and role must be recorded.
- Rationale is required for the disposition.
- Modified conditions must be explicit when used.
- Escalation target must be explicit when the case is escalated.
- Original recommendation remains immutable.
- Audit actor type for the human disposition is `human`.
- External actions remain `0` inside Project 7.
- A system recommendation cannot silently become a final organizational decision.

## Small-Business Role Concentration

A small business may have one individual serving multiple organizational roles. The prototype therefore records the **role being exercised**, not just a person name.

This does **not** establish a production separation-of-duties model. Before production, ICM must define:

- which decisions require independent review;
- when Legal Counsel, Security/Privacy, Contracts, Finance, or Delivery review cannot be self-approved;
- delegation thresholds;
- conflict-of-interest handling;
- temporary-role coverage;
- identity/authentication requirements.

## Contestability

A human reviewer may:

- accept the recommendation;
- accept with modified conditions;
- reject it;
- defer pending information;
- escalate to another authorized reviewer.

The ability to disagree with the system is a required control, not an exception.

## Demonstrated Acceptance Behavior

The operator acceptance work demonstrated both:

- an **accepted** R-05 recommendation with human disposition recorded separately; and
- a fresh request **escalated** to another authorized reviewer.

In both cases the recommendation remained unchanged and external actions remained zero.

## Production Boundary

The capstone validates role-aware human disposition recording, but it does not implement enterprise IAM, MFA, digital signatures, delegated-authority services, or production segregation of duties.
