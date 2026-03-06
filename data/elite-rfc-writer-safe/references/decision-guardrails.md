# Decision Guardrails (Project-Syn style)

Use this checklist while drafting RFCs. Do not change mandatory section headings.

## Status lifecycle

Use one status value in `Zusammenfassung`:
- speculative
- draft
- accepted
- rejected
- implemented
- obsolete

## Required decision metadata

Add in `Zusammenfassung`:
- Decision owner
- Decision date
- Review date (optional, recommended for high-risk changes)

## Evidence discipline

Add in `Motivation`:
- Baseline metric(s)
- Current failure mode / risk signal
- Why now

## Scope discipline

- `Ziele`: each goal should have a measurable success criterion.
- `Nicht-Ziele`: list explicit out-of-scope items to prevent scope creep.

## Proposal discipline

In `Vorschlag`, include when relevant:
- Migration plan
- Rollback strategy
- Constraint handling (tech/org/regulatory/financial)

## Risk discipline

In `Anhang`, include:
- Alternatives considered and rejection rationale
- Drawbacks and risks
- Mitigations
- Open questions (owner + due date)
- Source references (tickets, PRs, docs)
