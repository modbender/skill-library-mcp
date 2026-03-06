# consensus-publish-guard

Pre-publish policy governance for outward-facing content.

`consensus-publish-guard` evaluates content before it goes live (social posts, announcements, release notes, outbound statements) and returns:

- `ALLOW`
- `BLOCK`
- `REQUIRE_REWRITE`

## Why it exists

Publishing errors are hard to undo. This guard reduces legal, trust, and brand risk by enforcing deterministic checks before distribution.

## What it evaluates

- policy-sensitive claims and guarantees
- confidentiality leakage risks
- harmful/abusive language categories
- unsupported certainty statements
- quality and rewrite readiness

## Core capabilities

- strict input schema validation
- hard-block taxonomy handling
- persona-weighted voting or external votes
- idempotent retry behavior
- board-native artifact trail for replay and audit

## Decision semantics

- `BLOCK`: do not publish
- `REQUIRE_REWRITE`: revise and resubmit with guardrails
- `ALLOW`: safe to proceed under configured policy

## Quick start

```bash
npm i
node --import tsx run.js --input ./examples/input.json
```

## Test

```bash
npm test
```

## Related docs

- `SKILL.md`
- `AI-SELF-IMPROVEMENT.md`
