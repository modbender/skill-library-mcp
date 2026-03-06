---
name: action-suggester
description: "Generate non-binding follow-up action suggestions from lead summaries or lead lists. Use when users ask for next best actions, call list for hot leads, or follow-up draft plan without automatic execution. Recommended chain: summary-generator then action-suggester then supervisor approval. Do not use for parsing, storage, or autonomous action execution."
---

# Action Suggester

Produce ranked follow-up suggestions without taking any external action.

## Quick Triggers

- Suggest next actions for today's P1 leads.
- Build a call/email/visit plan from summary.
- Draft follow-up queue for unresolved high-priority leads.

## Recommended Chain

`summary-generator -> action-suggester -> supervisor confirmation`

## Execute Workflow

1. Accept input from Supervisor.
2. Validate input with `references/action-input.schema.json`.
3. Apply deterministic prioritization rules to propose follow-up items.
4. Emit actions with:
   - `action_type` in `call`, `email`, or `visit`
   - `lead_id`
   - `description`
5. Validate output with `references/action-output.schema.json`.
6. Return suggestions for human or Supervisor review only.

## Enforce Boundaries

- Never execute suggested actions.
- Never send messages, emails, or calendar invites.
- Never write to database or stateful systems.
- Never parse raw chat exports.
- Never approve its own output for execution.

## Handle Errors

1. Return an empty action list when evidence is insufficient.
2. Reject inputs that fail schema validation.
3. Surface deterministic rule conflicts in plain text diagnostics.
