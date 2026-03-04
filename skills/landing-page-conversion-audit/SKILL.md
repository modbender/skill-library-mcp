---
name: landing-page-conversion-audit
description: >
  Perform a structured conversion rate optimization (CRO) audit of a landing page.
  Use when a user shares a landing page URL, pastes their page copy, describes their
  page content, or uploads a screenshot and asks for a conversion audit, CRO review,
  conversion analysis, landing page feedback, or wants to know why their page isn't
  converting. Produces a scored 8-factor audit (0–80 total), prioritized fix list with
  quick wins and strategic recommendations, and an executive summary. Covers: headline
  clarity, supporting copy, social proof, CTA effectiveness, visual hierarchy, trust
  signals, mobile/speed signals, and offer clarity.
---

# Landing Page Conversion Audit

You are performing a professional conversion rate optimization (CRO) audit. Your job is
to evaluate the landing page across 8 conversion factors, score each one, identify the
highest-leverage fixes, and deliver a clear, actionable report.

---

## Step 1: Gather Input

Determine what the user has provided:

**A) URL** — Fetch the page using the `web_fetch` tool. Extract: headline, subheadline,
body copy, CTA text and placement, social proof elements, pricing/offer details, trust
signals, and any structural/design cues visible in the HTML or copy.

**B) Pasted copy or content** — Work directly from what's provided. Note any gaps where
visual or structural information would normally inform scoring.

**C) Screenshot or description** — Analyze from visual layout and described elements.
Note limitations where copy details aren't available.

If information is ambiguous or missing for a factor, score conservatively and note the
assumption. Do not ask clarifying questions — do the audit with what you have and flag
gaps in your rationale.

---

## Step 2: Score the 8 Conversion Factors

Evaluate each factor on a **0–10 scale** using the rubric below. Be honest — a
mediocre page should score mediocre. Reserve 9–10 for genuinely exceptional execution.

---

### Factor 1: Headline Clarity & Value Proposition (0–10)

What to evaluate:
- Does the headline immediately communicate what the product/service does and who it's for?
- Is the value proposition specific (outcomes, numbers, comparisons) or vague ("better,"
  "easier," "more powerful")?
- Would a first-time visitor understand the offer within 3 seconds?
- Is the headline benefit-led or feature-led?

**Scoring guide:**
- 0–3: Headline is generic, unclear, or says nothing meaningful about the offer
- 4–6: Partially clear; value exists but is buried, vague, or requires prior context
- 7–8: Clear value proposition with specific benefit; minor improvements possible
- 9–10: Instantly clear, specific, differentiated, benefit-led — reader knows exactly what they get

---

### Factor 2: Subheadline & Supporting Copy (0–10)

What to evaluate:
- Does the subheadline expand on the headline without repeating it?
- Does supporting body copy address the reader's problem, desire, or situation?
- Is the copy scannable (short paragraphs, bullets, bolded phrases) or dense walls of text?
- Does it build desire before asking for action?

**Scoring guide:**
- 0–3: No subheadline; body copy is absent, generic, or feature-focused
- 4–6: Subheadline present but weak; copy is functional but not compelling
- 7–8: Good flow between headline and copy; scannable; builds context well
- 9–10: Subheadline perfectly bridges headline to offer; copy is punchy, problem-aware, scannable

---

### Factor 3: Social Proof (0–10)

What to evaluate:
- Are testimonials present? Are they specific (results, names, roles, companies) or generic ("great product!")?
- Are logos, case studies, review counts, or user numbers shown?
- Is social proof placed near decision points (above the fold, near CTAs)?
- Is proof recent, credible, and relevant to the target buyer?

**Scoring guide:**
- 0–3: No social proof visible
- 4–5: Generic testimonials or proof present but weak (no specifics, names, or results)
- 6–7: Solid testimonials with names/roles; or strong numbers; not optimally placed
- 8–9: Specific, credible proof with results data; well-placed near CTAs
- 10: Multiple proof formats (testimonials + logos + numbers), highly specific, strategically positioned

---

### Factor 4: Call-to-Action (0–10)

What to evaluate:
- Is the primary CTA clear, specific, and action-oriented? (Not just "Submit" or "Click here")
- Does the CTA copy reflect the visitor's desired outcome? ("Start my free trial" > "Sign up")
- Is the CTA visually prominent (contrast, size, whitespace)?
- Is it placed above the fold and repeated at logical scroll intervals?
- Is there a single primary CTA, or is attention fragmented across multiple competing actions?

**Scoring guide:**
- 0–3: CTA is missing, buried, or uses weak generic text
- 4–5: CTA exists but copy is weak, placement is poor, or visually blends into page
- 6–7: Clear CTA with reasonable copy; may lack repetition or visual contrast
- 8–9: Strong action-oriented copy, high contrast, well-placed, repeated appropriately
- 10: Frictionless, benefit-led CTA copy, optimal placement, visually dominant, single focus

---

### Factor 5: Visual Hierarchy & Scan Path (0–10)

What to evaluate (infer from copy structure and HTML heading tags):
- Is there a clear reading path: headline → proof → CTA, without detours?
- Are heading tags (H1, H2, H3) used to guide scanning?
- Is the most important information above the fold?
- Does the layout direct attention toward conversion, or scatter it?
- Are there visual distractions (excessive nav links, popups described, sidebar clutter)?

**Scoring guide:**
- 0–3: No discernible hierarchy; key info buried; cluttered or confusing structure
- 4–5: Basic structure exists but important elements are below fold or hard to find
- 6–7: Reasonable hierarchy; scan path mostly works with minor friction
- 8–9: Clear F-pattern or Z-pattern flow; key elements prominent; minimal distractions
- 10: Laser-focused hierarchy; every element earns its place; conversion path is obvious

---

### Factor 6: Trust Signals & Objection Handling (0–10)

What to evaluate:
- Are risk reducers present: money-back guarantee, free trial, no credit card required?
- Is there a privacy statement near email/form fields?
- Are security badges, certifications, or press mentions visible?
- Does the copy proactively address common objections ("What if it doesn't work for me?")?
- Is contact info, a company name, or "real business" signals present?

**Scoring guide:**
- 0–3: No trust signals; nothing to reduce purchase anxiety
- 4–5: One or two generic trust signals present (e.g., padlock icon only)
- 6–7: Guarantee or trial offer present; some objection handling in copy
- 8–9: Multiple trust signals; objections addressed; clear risk reversal
- 10: Comprehensive trust architecture: guarantee + privacy + security + objection copy + social proof overlap

---

### Factor 7: Page Speed & Mobile Experience Signals (0–10)

Infer from: page structure, image descriptions, script mentions, mobile-specific copy,
responsive design indicators in HTML, or any user-provided context.

What to evaluate:
- Does the page appear to use heavy scripts, excessive images, or embed bloat?
- Is the layout described as mobile-responsive, or does it show signs of desktop-only design?
- Are forms short and finger-friendly, or long and complex?
- Do CTAs appear sized for tap targets?

**Scoring guide:**
- 0–3: Clear indicators of slow load (heavy embeds, no optimization), or obviously non-mobile layout
- 4–5: Some mobile consideration but likely issues remain; or insufficient signals to assess (score 5 with note)
- 6–7: Appears reasonably optimized; no obvious red flags
- 8–9: Lightweight structure, mobile-first signals evident, short forms
- 10: Demonstrably fast, mobile-optimized, minimal friction on all devices

*Note: If input is text-only with no structural signals, score this factor 5 and note the limitation.*

---

### Factor 8: Offer Clarity & Pricing Transparency (0–10)

What to evaluate:
- Is it immediately clear what the visitor gets if they convert?
- Is pricing shown, or is it hidden behind a form/sales call?
- If pricing is withheld, is there a compelling reason given?
- Is the offer specific (deliverables, timeline, features) or abstract?
- Are plan/tier differences clearly explained?

**Scoring guide:**
- 0–3: No offer details; visitor has no idea what they're getting or what it costs
- 4–5: Some offer description but vague; pricing hidden with no explanation
- 6–7: Reasonable offer description; pricing present but could be clearer
- 8–9: Clear deliverables + transparent pricing + plan differentiation
- 10: Crystal-clear offer with complete pricing, feature comparison, and delivery expectations

---

## Step 3: Compile the Audit Report

Deliver the report in this exact structure:

---

## 🔍 Landing Page Conversion Audit

**Page audited:** [URL or "Provided copy" or "Screenshot/Description"]
**Audit date:** [today's date]

---

### Overall Score: [X] / 80

| # | Factor | Score | 
|---|--------|-------|
| 1 | Headline Clarity & Value Proposition | X/10 |
| 2 | Subheadline & Supporting Copy | X/10 |
| 3 | Social Proof | X/10 |
| 4 | Call-to-Action | X/10 |
| 5 | Visual Hierarchy & Scan Path | X/10 |
| 6 | Trust Signals & Objection Handling | X/10 |
| 7 | Page Speed & Mobile Experience | X/10 |
| 8 | Offer Clarity & Pricing Transparency | X/10 |

---

### Factor Breakdown

**1. Headline Clarity & Value Proposition — [X]/10**
[1–2 sentences: what's working, what's not, specific to this page]

**2. Subheadline & Supporting Copy — [X]/10**
[1–2 sentences: specific observation]

**3. Social Proof — [X]/10**
[1–2 sentences: specific observation]

**4. Call-to-Action — [X]/10**
[1–2 sentences: specific observation]

**5. Visual Hierarchy & Scan Path — [X]/10**
[1–2 sentences: specific observation]

**6. Trust Signals & Objection Handling — [X]/10**
[1–2 sentences: specific observation]

**7. Page Speed & Mobile Experience — [X]/10**
[1–2 sentences: specific observation or note limitation]

**8. Offer Clarity & Pricing Transparency — [X]/10**
[1–2 sentences: specific observation]

---

### ⚡ Top 3 Quick Wins (Fix in Under 1 Hour)

These are the highest-ROI changes that require minimal effort. Prioritize these first.

1. **[Specific fix]** — [One sentence on why this matters and how to do it]
2. **[Specific fix]** — [One sentence on why this matters and how to do it]
3. **[Specific fix]** — [One sentence on why this matters and how to do it]

---

### 🏗️ Top 3 Strategic Fixes (Higher Effort, Higher Impact)

These require more work but will move the conversion needle significantly.

1. **[Specific fix]** — [One sentence on the impact and what it involves]
2. **[Specific fix]** — [One sentence on the impact and what it involves]
3. **[Specific fix]** — [One sentence on the impact and what it involves]

---

### Executive Summary

[One focused paragraph (4–6 sentences) that synthesizes the audit. Lead with the overall
conversion readiness assessment, name the single biggest drag on conversions, call out
the strongest existing element, and close with the most important next action. Write for
a founder or marketer who will read this first and may not read the rest.]

---

## Scoring Reference

| Score Range | Interpretation |
|-------------|----------------|
| 65–80 | Conversion-ready. Optimize for marginal gains. |
| 50–64 | Solid foundation with meaningful gaps. Address strategic fixes. |
| 35–49 | Below average. Quick wins will move the needle fast. |
| 20–34 | Significant conversion barriers. Structural rework needed. |
| 0–19 | Major overhaul required before meaningful conversion is possible. |

---

## Auditor Notes

- Be direct. Don't hedge observations to avoid offending — specific critique is the value.
- Ground every score in something observable from the provided content.
- Quick wins must be genuinely quick: copy edits, CTA text changes, adding a testimonial.
  Do not list quick wins that require design work or development.
- Strategic fixes should address root conversion problems, not cosmetic polish.
- If input is limited (pasted copy only, no design/layout info), say so in the relevant
  factor rationale. Never fabricate observations about elements you cannot see.
