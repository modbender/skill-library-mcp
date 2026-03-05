# consensus-persona-generator

Generate reusable persona sets for consensus-based decision workflows.

`consensus-persona-generator` creates and persists `persona_set` artifacts that guard packages use for weighted multi-perspective voting. Ongoing reputation mutation is owned by `consensus-persona-engine`.

## Why this package exists

High-quality governance needs diverse perspectives (security, reliability, ops, user impact). This package makes those perspectives explicit and reusable instead of implicit and ad hoc.

## Core capabilities

- strict schema validation
- deterministic generation path (reproducible baseline)
- board-native artifact writes (`persona_set`)
- indexed retrieval helpers for latest/by-id persona sets

## Typical output

- `persona_set_id`
- `personas[]` with initial reputation baselines (later updated by `consensus-persona-engine`)
- board write reference for audit trail

## Environment + state path

This package reads state-path configuration from:
- `CONSENSUS_STATE_FILE`
- `CONSENSUS_STATE_ROOT`

Use a dedicated non-privileged directory for state; do not point state paths at system or secrets directories.

## Quick start

```bash
npm i
node --import tsx run.js --input ./examples/persona-input.json
```

## Test

```bash
npm test
```

## Related docs

- `SKILL.md`
- `AI-SELF-IMPROVEMENT.md`
