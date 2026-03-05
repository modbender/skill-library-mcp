---
name: consensus-send-email-guard
description: Persona-weighted pre-send email governance for AI systems. Produces APPROVE/BLOCK/REWRITE decisions, writes decision artifacts to the board ledger, updates persona reputation over time, and returns strict machine-parseable JSON.
homepage: https://github.com/kaicianflone/consensus-send-email-guard
source: https://github.com/kaicianflone/consensus-send-email-guard
metadata:
  {"openclaw": {"requires": {"bins": ["node", "tsx"]}}}
---

# consensus-send-email-guard

`consensus-send-email-guard` is a production-style outbound communication guardrail.

## What this skill does

- evaluates an email draft with a persona panel
- aggregates votes by reputation (weighted approval policy)
- enforces hard-block categories (sensitive data, legal/medical certainty, disallowed guarantees)
- returns final decision: `APPROVE | BLOCK | REWRITE`
- writes `decision` and updated `persona_set` artifacts to board state

## Why this matters

Email is high-impact and irreversible once sent. This skill reduces hallucinated promises and policy-violating claims before external side effects occur.

## Ecosystem role

Stack position:

`consensus-tools -> consensus-interact pattern -> persona_set -> send-email-guard`

It converts raw generation into governed action with auditability.

## Governance and learning

- strict JSON contracts for automation pipelines
- idempotent retries to prevent duplicate reputation mutation
- reputation updates calibrate evaluator influence over time

## Use cases

- customer-facing outbound messaging
- partner/legal-sensitive communications
- automated campaign quality gates


## Runtime, credentials, and network behavior

- runtime binaries: `node`, `tsx`
- network calls: none in the guard decision path itself
- credentials: none required
- filesystem writes: board/state artifacts under the configured consensus state path

## Dependency trust model

- `consensus-guard-core` is the first-party consensus package used in guard execution
- versions are semver-pinned in `package.json` for reproducible installs
- this skill does not request host-wide privileges and does not mutate other skills

## Quick start

```bash
node --import tsx run.js --input ./examples/email-input.json
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
