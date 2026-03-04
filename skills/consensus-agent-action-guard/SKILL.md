---
name: consensus-agent-action-guard
description: Pre-execution governance for high-risk agent actions. Uses persona-weighted consensus to decide ALLOW/BLOCK/REQUIRE_REWRITE before external or irreversible side effects occur, with board-native audit artifacts.
version: 1.1.13
homepage: https://github.com/kaicianflone/consensus-agent-action-guard
source: https://github.com/kaicianflone/consensus-agent-action-guard
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
        package: consensus-agent-action-guard
        bins:
          - node
          - tsx
---

# consensus-agent-action-guard

`consensus-agent-action-guard` is the final safety gate before autonomous action execution.

## What this skill does

- evaluates proposed agent actions (risk, irreversibility, side effects)
- applies hard-block and weighted consensus logic
- returns one of: `ALLOW | BLOCK | REQUIRE_REWRITE`
- emits required follow-up actions (e.g., human confirmation)
- writes decision and persona updates to board artifacts

## Why this matters

Most catastrophic automation failures happen at execution time. This skill inserts explicit governance before side effects.

## Ecosystem role

Built on the same consensus stack as communication and merge guards, giving one policy language across agent operations.

## Typical usage

- gating destructive operations
- controlling external messaging/posting actions
- requiring human confirmation for irreversible high-risk tasks


## Runtime, credentials, and network behavior

- runtime binaries: `node`, `tsx`
- network calls: none in the guard decision path itself
- filesystem writes: board/state artifacts under the configured consensus state path

## Dependency trust model

- `consensus-guard-core` is the first-party consensus package used in guard execution
- versions are semver-pinned in `package.json` for reproducible installs
- this skill does not request host-wide privileges and does not mutate other skills

## Quick start

```bash
node --import tsx run.js --input ./examples/input.json
```

## Tool-call integration

This skill is wired to the consensus-interact contract boundary (via shared consensus-guard-core wrappers where applicable):
- readBoardPolicy
- getLatestPersonaSet / getPersonaSet
- writeArtifact / writeDecision
- idempotent decision lookup

This keeps board orchestration standardized across skills.

## Invoke Contract

This skill exposes a canonical entrypoint:

- `invoke(input, opts?) -> Promise<OutputJson | ErrorJson>`

`invoke()` starts the guard flow and executes deterministic policy evaluation with board operations via shared guard-core wrappers.

## external_agent mode

Guards support two modes:
- `mode="external_agent"`: caller supplies `external_votes[]` from agents/humans/models for deterministic aggregation.
- `mode="persona"`: requires an existing `persona_set_id`; guard will not generate persona sets internally.
