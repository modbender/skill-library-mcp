---
name: consensus-publish-guard
description: Persona-weighted governance for outbound publishing (blog, social, announcements). Prevents unsafe public claims via hard-block checks, weighted consensus, rewrite paths, and board-native audit artifacts.
homepage: https://github.com/kaicianflone/consensus-publish-guard
source: https://github.com/kaicianflone/consensus-publish-guard
metadata:
  {"openclaw": {"requires": {"bins": ["node", "tsx"], "env": ["CONSENSUS_STATE_FILE", "CONSENSUS_STATE_ROOT"]}}}
---

# consensus-publish-guard

`consensus-publish-guard` protects public-facing content before release.

## What this skill does

- reviews content drafts with persona consensus
- flags policy/legal/sensitive-risk patterns
- decides `APPROVE | BLOCK | REWRITE`
- emits rewrite patch when fixable
- persists decision artifacts to board state

## Why this matters

Public content creates brand, legal, and trust exposure. Consensus review creates a safer publish gate than single-pass generation.

## Ecosystem role

Uses deterministic logic from `consensus-guard-core` and existing persona inputs, persisted via consensus board primitives.

## Good fit for

- AI-assisted social/media pipelines
- product launch copy checks
- policy-sensitive communications


## Runtime, credentials, and network behavior

- runtime binaries: `node`, `tsx`
- network calls: none in the guard decision path itself
- credentials: none required
- environment config read by this package: `CONSENSUS_STATE_FILE`, `CONSENSUS_STATE_ROOT`
- filesystem writes: board/state artifacts under the configured consensus state path

## Dependency trust model

- `consensus-guard-core` is the first-party consensus package used in guard execution
- versions are semver-pinned in `package.json` for reproducible installs
- this skill does not request host-wide privileges and does not mutate other skills

## Install assumptions

This repository currently expects a local sibling checkout of `consensus-guard-core`.

```bash
# from repos/ directory
# repos/
#   consensus-guard-core/
#   consensus-publish-guard/
```

Then install dependencies in this repo:

```bash
npm i
```

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
