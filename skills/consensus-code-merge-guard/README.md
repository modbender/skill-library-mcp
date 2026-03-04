# consensus-code-merge-guard

Deterministic merge governance for pull requests and release branches.

`consensus-code-merge-guard` evaluates a proposed merge and returns:

- `ALLOW`
- `BLOCK`
- `REQUIRE_REWRITE`

so merge decisions are policy-backed, auditable, and replayable.

## What this package protects

- production reliability
- security posture
- CI discipline
- release quality under shipping pressure

## Evaluation dimensions

Common policy lanes include:
- security findings severity
- test/CI health
- rollback readiness
- performance/regression risk
- unresolved reviewer or policy gates

## Core mechanics

- strict schema validation (unknown fields rejected)
- persona-weighted voting or external vote ingestion
- deterministic weighted aggregation via `consensus-guard-core`
- idempotency keys for retry-safe workflows
- board-native decision artifacts for traceability

## Typical integration point

Run this guard after CI checks are available and before merge automation executes.

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
