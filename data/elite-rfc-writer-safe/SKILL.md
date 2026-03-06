---
name: elite-rfc-writer
description: "Write decision-oriented engineering RFCs with strict template enforcement. Use when the user asks for an RFC, architecture decision proposal, or structured decision document that must follow the exact headings: Zusammenfassung, Motivation, Ziele, Nicht-Ziele, Vorschlag, Anhang."
---

# Elite RFC Writer

Produce precise, decision-enabling RFCs for engineering and architecture decisions.

## Skill contract

- **Name:** `elite-rfc-writer`
- **Problem solved:** Convert ambiguous requests into clear, decision-oriented RFCs with explicit scope and trade-offs.
- **Required input categories (must collect before drafting):**
  1. Problem to solve
  2. Stakeholders affected
  3. Constraints (technical/organizational/regulatory/financial)
  4. Alternatives considered
  5. Risks and open questions
- **Output:** RFC in exact mandatory structure and headings (German)
- **Safety boundaries:**
  - Never deviate from mandatory headings/order.
  - Never hide uncertainties; state assumptions explicitly.
  - Never omit risks/trade-offs.
  - Never use marketing language or vague claims.

## Mandatory workflow

Use references as needed:
- Read `references/rfc-intake-checklist.md` during intake.
- Read `references/decision-guardrails.md` before finalizing.

### 1) Intake validation (hard gate)

Before writing, verify all five required input categories are present.

If data is missing:
- Ask concise clarifying questions.
- Do not draft a final RFC yet.

### 2) Drafting rules

- Use short paragraphs.
- Prefer bullet points.
- Keep tone neutral and analytical.
- Avoid unnecessary implementation details.
- Ensure statements are testable/falsifiable where possible.
- Explicitly state assumptions and uncertainty.
- Add concrete success criteria for each goal when possible.
- Keep content decision-oriented; remove educational filler.

### 3) Template enforcement (no deviation)

Always output RFCs with this exact structure and headings:

# Zusammenfassung
[ Absatz 1: Problemzusammenfassung ]
[ Absatz 2: Zusammenfassung des Lösungsvorschlags ]

# Motivation
[ Welches Problem müssen wir adressieren? ]

# Ziele
* [ Ziel ]: [ Erläuterung (welche Ziele sollte der Lösungsvorschlag unterstützen?) ]

# Nicht-Ziele
* [ Nicht-Ziel ]: [ Erläuterung (Nebenpfade / Zeitfresser / No-Go-Bereiche / Scope Creep vermeiden) ]

# Vorschlag
[ Wie lösen wir das oben beschriebene Problem? ]

# Anhang
[ Alles Weitere, einschließlich FAQ, betrachtete Alternativen, Nachteile, Daten, Referenzen, ... ]

### 4) Decision guardrails (Project-Syn inspired)

Keep the mandatory heading structure unchanged, but enforce these guardrails inside the sections:

- In **Zusammenfassung**:
  - State decision status (`speculative`, `draft`, `accepted`, `rejected`, `implemented`, `obsolete`).
  - State decision owner and decision date.
- In **Motivation**:
  - Add measurable evidence that the problem exists.
  - List assumptions explicitly.
- In **Ziele**:
  - Add measurable success criteria for each goal.
- In **Nicht-Ziele**:
  - Explicitly mark out-of-scope work and no-go areas.
- In **Vorschlag**:
  - Include migration path and rollback strategy when operationally relevant.
  - List key constraints (technical, organizational, regulatory, financial).
- In **Anhang**:
  - Include alternatives considered and why rejected.
  - Include drawbacks/risks with mitigations.
  - Include open questions with owner and due date.
  - Include references to tickets/PRs/docs used as evidence.

### 5) Quality gate before finalizing

Confirm all checks:
- Problem clearly defined and measurable
- Goals and non-goals reduce scope creep
- Proposal actionable and realistic
- Risks and alternatives documented
- Assumptions explicit and testable
- Migration/rollback defined when relevant
- Document supports a concrete decision

If any check fails, revise before final output.

## Response style requirements

Use descriptive language with precise terminology and concrete trade-off statements.
