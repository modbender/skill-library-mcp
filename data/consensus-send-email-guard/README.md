# consensus-send-email-guard

Pre-send governance for outbound email automation.

`consensus-send-email-guard` evaluates an email draft before delivery and returns:

- `APPROVE`
- `BLOCK`
- `REWRITE`

with structured rationale and board-native audit artifacts.

## Typical use cases

- customer-facing lifecycle emails
- sales/prospecting automation
- sensitive account or policy notifications
- high-trust operational communications

## What it evaluates

- policy and tone compliance
- risky guarantees or commitments
- confidentiality and sensitive data concerns
- rewrite quality for fixable drafts

## Core capabilities

- strict schema validation
- deterministic persona-weighted voting
- idempotent retry behavior
- `rewrite_patch` generation path for actionable edits
- board-native decision + persona update artifacts

## Output highlights

- decision metadata (`decision_id`, `timestamp`)
- vote + aggregation breakdown
- `final_decision`
- optional `rewrite_patch`
- `board_writes[]`

## Quick start

```bash
npm i
node --import tsx run.js --input ./examples/email-input.json
```

## Test

```bash
npm test
```

## Related docs

- `SKILL.md`
- `AI-SELF-IMPROVEMENT.md`
