---
name: consensus-permission-escalation-guard
description: Pre-execution governance for IAM and permission escalation changes. Use when an agent or workflow proposes granting, expanding, or assuming higher privileges and you need deterministic ALLOW/BLOCK/REQUIRE_REWRITE decisions with strict schema validation, idempotency, and board-native audit artifacts.
version: 0.1.12
homepage: https://github.com/kaicianflone/consensus-permission-escalation-guard
source: https://github.com/kaicianflone/consensus-permission-escalation-guard
upstream:
  consensus-guard-core: https://github.com/kaicianflone/consensus-guard-core
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
        package: consensus-permission-escalation-guard
        bins:
          - node
          - tsx
---

# consensus-permission-escalation-guard

`consensus-permission-escalation-guard` is the final safety gate before privilege elevation is applied.

## What this skill does

- validates escalation requests against a strict input schema (reject unknown fields)
- evaluates hard-block and rewrite policy flags for IAM risk patterns
- runs persona-weighted voting (or aggregates external votes)
- returns one of: `ALLOW | BLOCK | REQUIRE_REWRITE`
- writes decision artifacts for replay/audit

## Decision policy shape

Hard-block examples:
- wildcard permissions (`*`, `: *`, broad owner/admin jumps)
- missing ticket reference when required
- break-glass escalation without incident reference
- separation-of-duties conflicts (e.g., create + approve authority)

Rewrite examples:
- weak or non-actionable justification
- temporary duration exceeds policy limit
- production escalation requires explicit human confirmation gate

## Runtime and safety model

- runtime binaries: `node`, `tsx`
- network behavior: none in deterministic guard logic
- environment config read by this package: `CONSENSUS_STATE_FILE`, `CONSENSUS_STATE_ROOT`
- filesystem writes: consensus board/state artifacts under configured state path

## Invoke contract

- `invoke(input, opts?) -> Promise<OutputJson | ErrorJson>`

Modes:
- `mode="persona"` (default): uses local deterministic persona defaults for internal voting
- `mode="external_agent"`: consume `external_votes[]`, then aggregate and enforce policy deterministically

## Install

```bash
npm i consensus-permission-escalation-guard
```

## Quick start

```bash
node --import tsx run.js --input ./examples/input.json
```

## Tests

```bash
npm test
```

Test coverage includes schema rejection, hard-block paths, rewrite paths, allow paths, idempotent retries, and external-agent aggregation behavior.

Note: this skill depends on `consensus-guard-core` for aggregation/state helpers; review that package alongside this one for full runtime auditability.

See also: `SECURITY-ASSURANCE.md` for threat model, runtime boundaries, and deployment hardening guidance.
