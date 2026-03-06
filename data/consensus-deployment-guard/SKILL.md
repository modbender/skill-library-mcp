---
name: consensus-deployment-guard
description: Pre-deployment governance for release and infrastructure rollout requests. Use when an agent or workflow proposes shipping code/config/infrastructure changes to staging or production and you need deterministic ALLOW/BLOCK/REQUIRE_REWRITE decisions with strict schema validation, idempotency, and board-native audit artifacts.
version: 0.1.9
homepage: https://github.com/kaicianflone/consensus-deployment-guard
source: https://github.com/kaicianflone/consensus-deployment-guard
upstream:
  consensus-guard-core: https://github.com/kaicianflone/consensus-guard-core

requires:
  bins:
    - node
    - tsx
  env:
    - CONSENSUS_STATE_FILE
    - CONSENSUS_STATE_ROOT
metadata:
  openclaw:
    requires:
      bins:
        - node
        - tsx
      env:
        - CONSENSUS_STATE_FILE
        - CONSENSUS_STATE_ROOT
    install:
      - kind: node
        package: consensus-deployment-guard
        bins:
          - node
          - tsx
---

# consensus-deployment-guard

`consensus-deployment-guard` is the final safety gate before deployment execution.

## What this skill does

- validates deployment requests against a strict JSON schema (reject unknown fields)
- evaluates hard-block and rewrite policy flags for release risk patterns
- runs deterministic persona-weighted voting (or aggregates external votes)
- returns one of: `ALLOW | BLOCK | REQUIRE_REWRITE`
- writes decision artifacts for replay/audit

## Decision policy shape

Hard-block examples:
- required tests not passing
- CI status failed
- rollback artifact missing when required
- incompatible schema migration
- error budget already breached

Rewrite examples:
- production rollout not using canary when policy requires it
- initial rollout percentage above policy limit
- production deploy missing explicit human confirmation gate
- CI still pending
- schema compatibility unknown

## Runtime and safety model

- runtime binaries: `node`, `tsx`
- network behavior: none in guard decision logic
- environment config read by this package: `CONSENSUS_STATE_FILE`, `CONSENSUS_STATE_ROOT`
- filesystem writes: consensus board/state artifacts under configured state path

## Invoke contract

- `invoke(input, opts?) -> Promise<OutputJson | ErrorJson>`

Modes:
- `mode="persona"` (default): use local deterministic persona defaults for internal voting
- `mode="external_agent"`: consume `external_votes[]`, aggregate deterministically, and enforce policy

## Install

```bash
npm i consensus-deployment-guard
```

## Quick start

```bash
node --import tsx run.js --input ./examples/input.json
```

## Tests

```bash
npm test
```

Coverage includes schema rejection, hard-block paths, rewrite paths, allow paths, idempotent retries, and external-agent aggregation behavior.

See also: `SECURITY-ASSURANCE.md` for threat model, runtime boundaries, and deployment hardening guidance.
