---
name: consensus-persona-engine
description: Deterministic persona reputation engine that applies guard decision effects to persona_set state and emits explicit reputation_delta artifacts.
homepage: https://github.com/kaicianflone/consensus-persona-engine
source: https://github.com/kaicianflone/consensus-persona-engine
metadata:
  {"openclaw": {"requires": {"bins": ["node"]}}}
---

# consensus-persona-engine

`consensus-persona-engine` is the state transition layer for persona reputation updates.

## What this skill does

- takes `decision`, `vote_batch`, and current `persona_set`
- applies deterministic reputation rules
- emits `reputation_delta`
- returns updated `persona_set` with lineage-safe fields

## Invoke contract

- `invoke(input, opts?) -> Promise<OutputJson | ErrorJson>`

Required input:
- `board_id`
- `decision`
- `vote_batch`
- `persona_set`
- optional `ruleset`

No provider credentials required.
