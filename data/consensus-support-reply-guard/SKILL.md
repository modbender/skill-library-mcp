---
name: consensus-support-reply-guard
description: Risk-aware support response governance with persona-weighted consensus. Detects legal/sensitive/confidentiality issues, applies hard-block policy checks, and writes auditable decision artifacts for customer-facing automation.
version: 1.1.14
homepage: https://github.com/kaicianflone/consensus-support-reply-guard
source: https://github.com/kaicianflone/consensus-support-reply-guard
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
        package: consensus-support-reply-guard
        bins:
          - node
          - tsx
---

# consensus-support-reply-guard

`consensus-support-reply-guard` is a customer-trust guard for support workflows.

## What this skill does

- evaluates support drafts before sending
- detects high-risk claim patterns
- blocks or rewrites responses when policy violations appear
- updates persona reputations based on final decision alignment
- preserves decision history in board artifacts

## Why this matters

Support replies are high-frequency and brand-critical. This skill prevents overconfident legal/PII mistakes at scale.

## Ecosystem role

Composes with consensus board state using explicit vote inputs and deterministic guard decisions.

## Ideal scenarios

- automated ticket triage replies
- L1/L2 AI response review gates
- regulated or enterprise support channels


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
