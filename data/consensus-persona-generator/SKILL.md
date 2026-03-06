---
name: consensus-persona-generator
description: Generate and persist reusable persona panels (persona_set artifacts) for consensus decision workflows. This skill initializes evaluator diversity for downstream guards; ongoing reputation updates are owned by consensus-persona-engine.
version: 1.1.14
homepage: https://github.com/kaicianflone/consensus-persona-generator
source: https://github.com/kaicianflone/consensus-persona-generator
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
        package: consensus-persona-generator
---

# consensus-persona-generator

`consensus-persona-generator` is the entrypoint for evaluator diversity in the Consensus.Tools ecosystem.

## What this skill does

- creates N distinct decision personas (role, bias, risk posture, voting style)
- assigns initial reputation baselines for weighted arbitration (ongoing updates handled by consensus-persona-engine)
- persists a versioned `persona_set` artifact to board state
- reuses compatible persona sets when possible to reduce churn

## Why this matters

Most agent pipelines fail because one model self-approves its own output. This skill injects structured disagreement first, so later guards operate over explicit multi-perspective review.

## Ecosystem role

Stack position:

`consensus-tools -> consensus-interact pattern -> consensus-persona-generator -> domain guards -> consensus-persona-engine`

- **consensus-tools**: board/job/submission ledger substrate
- **consensus-interact**: board-native orchestration contract
- **persona-generator**: lightweight multi-agent initialization layer
- **persona-engine**: reputation update and persona lifecycle state transition layer

## Inputs / outputs (automation-friendly)

- strict JSON input contract (`board_id`, `task_context`, `n_personas`, etc.)
- strict JSON output with `persona_set_id`, `personas[]`, and board write refs
- deterministic/replayable behavior where feasible

## Typical use cases

- bootstrap evaluators for email/publish/support/merge/action guards
- regenerate persona cohorts by domain or risk profile
- establish reusable governance personas for long-running automation


## Runtime, credentials, and network behavior

- runtime binaries: `node`, `tsx`
- network calls: none in shipped generator logic
- environment config read by this package: `CONSENSUS_STATE_FILE`, `CONSENSUS_STATE_ROOT`
- filesystem writes: board/state artifacts under the configured consensus state path

## Dependency trust model

- `consensus-guard-core` is the first-party consensus runtime dependency for this package
- versions are semver-pinned in `package.json` for reproducible installs
- this skill does not request host-wide privileges and does not mutate other skills

## Install

```bash
npm i consensus-persona-generator
```

## Quick start

```bash
node --import tsx run.js --input ./examples/persona-input.json
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

`invoke()` initializes or reuses persona sets and executes board operations via shared guard-core wrappers. It does not perform ongoing reputation mutation; that belongs to consensus-persona-engine.
