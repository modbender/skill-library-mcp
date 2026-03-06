# consensus-deployment-guard

Pre-deployment governance for release and infrastructure rollout decisions.

`consensus-deployment-guard` evaluates a proposed deployment and returns:

- `ALLOW`
- `BLOCK`
- `REQUIRE_REWRITE`

before rollout execution.

## What it protects

- production reliability
- release safety
- rollback readiness
- error-budget discipline

## Core capabilities

- strict schema validation (Ajv 2020)
- deterministic deployment policy flags
- persona mode + external-agent vote mode
- idempotent retries with stable decision replay
- board-native audit artifacts

## Example policy checks

Hard block examples:
- tests failed
- CI failed
- rollback artifact missing
- schema incompatibility
- error budget breached

Rewrite examples:
- production rollout not canary (when policy requires)
- initial rollout percentage too high
- production deploy missing explicit human confirmation gate
- CI pending / schema compatibility unknown

## Environment + state path

This package reads state-path configuration from:
- `CONSENSUS_STATE_FILE`
- `CONSENSUS_STATE_ROOT`

Use a dedicated non-privileged directory for state; do not point state paths at system or secrets directories.

## Quick start

```bash
npm i
node --import tsx run.js --input ./examples/input.json
```

## Test

```bash
npm test
```

## Notes

- Uses the same deterministic orchestration model as other Consensus guard skills
- Optimized for auditable release decisions in agent-assisted CI/CD pipelines
