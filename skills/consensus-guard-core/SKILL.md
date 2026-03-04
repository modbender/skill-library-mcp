---
name: consensus-guard-core
description: Shared deterministic guard primitives for the Consensus.Tools skill family: hard-block taxonomy, weighted vote aggregation, reputation updates, idempotency keys, strict schema enforcement, and indexed board artifact access.
homepage: https://github.com/kaicianflone/consensus-guard-core
source: https://github.com/kaicianflone/consensus-guard-core
upstream:
  consensus-tools: https://github.com/kaicianflone/consensus-tools
---

# consensus-guard-core

`consensus-guard-core` is the common policy engine behind the Consensus guard ecosystem.

## What this skill/package provides

- unified hard-block taxonomy
- deterministic `aggregateVotes()` policy function
- deterministic reputation update rules with clamping
- idempotency key generation for retry-safe execution
- strict-schema unknown-field rejection helpers
- indexed board read helpers for scalable artifact lookup

## Why this matters

Without a shared core, every guard drifts into incompatible policy logic. This package keeps behavior consistent, replayable, and comparable across domains.

## Ecosystem role

`consensus-guard-core` is consumed by publish/support/merge/action guards and should be treated as policy infrastructure, not an end-user workflow skill.

## Benefits for LLM orchestration

- lower integration drift
- consistent decision semantics across workflows
- easier auditing and cross-skill analytics


## Runtime, credentials, and network behavior

- runtime binaries: `node`, `tsx`
- network calls: none in this package's core decision/path helpers
- credentials: none required by this package
- environment config read by this package: `CONSENSUS_STATE_FILE`, `CONSENSUS_STATE_ROOT` (for board/state path resolution)
- filesystem writes: board/state artifacts under the configured consensus state path when callers use write helpers (for example `writeArtifact`)

## Dependency trust model

- `consensus-guard-core` is a first-party consensus package
- versions are semver-pinned in `package.json` for reproducible installs
- this skill does not request host-wide privileges and does not mutate other skills
- note: dependency trees should be audited separately by consumers for transitive packages

## Install

```bash
npm i consensus-guard-core
```

## Quick start

```bash
npm test
```

## Import contract

Use the package root import (stable public API):

```js
import { aggregateVotes, writeArtifact, resolveStatePath } from 'consensus-guard-core';
```

Do not import internal paths like `consensus-guard-core/src/index.mjs` in dependent skills.

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

`invoke()` is primitives-only and delegates to a caller-provided handler. It does not perform persona generation or model/provider calls.

See also: `SECURITY-ASSURANCE.md` for threat model, runtime boundaries, and hardening guidance.
