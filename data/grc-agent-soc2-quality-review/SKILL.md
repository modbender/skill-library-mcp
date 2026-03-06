---
name: grc-agent-soc2-quality-review
description: Evaluate SOC 2 report quality using the SOC 2 Quality Guild rubric (Structure, Substance, Source). Use when reviewing a vendor SOC 2 Type 1/Type 2 report, triaging report credibility, producing a risk memo, or preparing diligence follow-up questions and evidence requests.
---

# SOC 2 Quality Review

## Project Background & Acknowledgment

This skill was built using the SOC 2 Quality Guild resources at **s2guild.org** as a baseline for quality-focused SOC 2 vendor attestation reviews.

This project was the first GRC agent I wanated to try creating with OpenClaw after setting up across multiple environments, including Raspberry Pi, Intel NUC, several LXC containers, and a cluster setup of 3 Mac Studios using EXO.

Big thanks to the **SOC 2 Quality Guild community** for sharing excellent, practical guidance that helped shape this agent.

## Maintainer

- Author: Simon Tin-Yul Kok
- LinkedIn: https://www.linkedin.com/in/simonkok/
- GitHub: https://github.com/mangopudding/

Review SOC 2 quality before trusting conclusions.

## When NOT to use this skill

Do not use this skill for:
- Legal advice or legal conclusions about regulatory compliance.
- Formal certification decisions (this is a quality review aid, not an issuing authority).
- Deep technical penetration testing or exploit validation.
- Historical incident forensics requiring endpoint/network-level evidence collection.
- Vendor contract drafting as a substitute for legal/procurement review.

## Workflow

1. Confirm review profile (audience, risk posture, strictness).
2. Confirm scope.
3. Score all 11 signals.
4. Run S12+ advanced diligence.
5. Summarize critical gaps.
6. Produce decision + follow-up requests.

## Review profile (required)

Before scoring, capture these user-selectable settings:
- **Primary audience:** Security, Procurement, Customer Trust, or All
- **Risk posture:** Conservative / Balanced / Lenient
- **Data sensitivity baseline:** High / Medium / Low
- **Evidence strictness:** Escalate on Unknown / Conditional acceptance with deadline / Case-by-case
- **Output style:** Executive memo, Full analyst report, or Both

Default to user-provided settings when available. If not provided, ask once before final verdict.

## 1) Confirm scope

Capture:
- Report type: Type 1 or Type 2
- Period covered
- Trust Services Categories in scope
- In-scope system boundary
- Auditor firm + signer
- Qualification status (unqualified/qualified/adverse/disclaimer)

If key sections are missing, stop and request a full report.

## 2) Score all 11 signals

Read `references/rubric.md` and score each signal:
- 2 = strong evidence
- 1 = partial or ambiguous
- 0 = missing, contradictory, or weak

Use a strict standard for Section 4 testing detail and source credibility checks.

## 2b) Run S12+ advanced diligence questions

After S1–S11 scoring, run `references/advanced-diligence.md` and collect answers for the additional diligence set.

Rules:
- Treat S12+ as decision-strengthening checks, not replacements for S1–S11.
- If an answer is unavailable, mark it explicitly as `Unknown` and create a follow-up request.
- Elevate risk when multiple S12+ items remain unknown for high-sensitivity data use cases.

## 3) Flag hard fails

Treat these as high-severity findings by default:
- Missing required auditor report structure (S1)
- Missing/incomplete unsigned management assertion (S2)
- Unlicensed or unverified CPA firm (S8)
- Pervasive testing vagueness on critical controls (S7)

If one or more hard fails exist, recommend compensating evidence even if the opinion is unqualified.

## 4) Produce outputs

Always return three artifacts.

### A) Executive verdict (short)

- Overall confidence: High / Medium / Low (use `references/confidence-rubric.md`)
- Decision: Accept / Accept with conditions / Escalate / Reject
- Top 3 reasons

### B) Scorecard

List S1–S11 with:
- Score (0/1/2)
- Evidence citation (use `references/evidence-citation-format.md`)
- Why it matters
- Follow-up request (if score <2)

### C) Follow-up request pack

Create a vendor-facing request list using `references/vendor-request-templates.md`:
- Direct evidence needed
- Clarifications required
- Deadline recommendation
- Decision gate (what must be resolved)

## Scoring guidance

- Prioritize evidence quality over report polish.
- Penalize boilerplate language that could apply to any company.
- Penalize weak control-to-criteria logic.
- Penalize mismatch between exceptions and opinion severity.
- Separate auditor credibility concerns from control design concerns.

## Decision rubric

Use `references/decision-matrix.md` with the selected risk posture and evidence strictness.

Baseline outcomes:
- **Accept**: no hard fails, most signals strong, no unresolved critical gaps.
- **Accept with conditions**: limited gaps, clear compensating evidence path.
- **Escalate**: mixed evidence, source credibility concerns, or unclear testing sufficiency.
- **Reject**: fundamental structure/source failures or severe unresolved substance failures.

## Required response format

Use this exact section order:
1. Executive verdict
2. Signal-by-signal scorecard (S1–S11)
3. Advanced diligence (S12+) findings
4. Critical risks
5. Vendor follow-up questions
6. Interim compensating controls (what your org should do now)

For structure and quality calibration, mirror `references/output-example.md`.

## Calibration rules

Apply thresholds using selected profile:
- **High sensitivity (PII/PHI/financial, including candidate resume and employer/company data):** require strong minimums on S4/S6/S7/S8 and tighter follow-up deadlines.
- **Medium sensitivity:** allow limited partials with compensating evidence.
- **Low sensitivity:** tolerate minor source/substance weaknesses with conditions.

Apply evidence strictness setting:
- **Escalate on Unknown:** unknowns on critical areas force Escalate.
- **Conditional acceptance with deadline:** permit temporary acceptance only with explicit due dates and owners.
- **Case-by-case:** weigh unknowns by control criticality and data sensitivity.
