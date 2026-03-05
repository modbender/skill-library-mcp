# consensus-support-reply-guard

Governance layer for customer support replies (human- or agent-authored).

`consensus-support-reply-guard` reviews a proposed support response before send and returns:

- `ALLOW`
- `BLOCK`
- `REQUIRE_REWRITE`

## Best-fit scenarios

- billing/refund communication
- policy-sensitive support channels
- high-severity incidents and escalations
- regulated or enterprise support environments

## What this package checks

- hard-block taxonomy categories (safety/compliance/trust)
- risky commitments and over-promises
- inappropriate legal/medical certainty
- confidentiality violations
- rewrite opportunities for safe resolution

## Core mechanics

- strict schema validation
- deterministic weighted consensus
- idempotent replays under retries
- board-native decision artifacts

## Why this matters

Support messaging is a high-trust surface. This guard reduces silent failure propagation and creates an auditable decision log for every high-impact reply.

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
