# consensus-persona-respawn

Lifecycle management for persona quality in long-running consensus systems.

`consensus-persona-respawn` replaces dead or degraded personas with lineage-aware successors informed by decision artifacts, ledger history, and persona-engine reputation outcomes.

## Why this matters

Static persona sets decay over time. Respawn mechanisms preserve governance quality by adapting poor performers while keeping decision history auditable.

## Core capabilities

- strict schema validation
- idempotent respawn execution
- successor generation tied to historical performance
- board-native artifact writes with lineage metadata

## Ideal use cases

- long-lived guard deployments
- repeated policy domains with quality drift
- governance systems that require explicit adaptation history

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
