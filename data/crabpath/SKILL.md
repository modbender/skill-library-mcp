---
name: crabpath
description: Memory graph engine with caller-provided embed and LLM callbacks; core is pure, with real-time correction flow and optional OpenAI integration.
metadata:
  openclaw:
    emoji: "🦀"
    requires:
      python: ">=3.10"
---

# CrabPath

Pure graph core: zero required deps and no network calls. Caller provides callbacks.

## Design Tenets

- No network calls in core
- No secret discovery (no dotfiles, keychain, or env probing)
- No subprocess provider wrappers
- Embedder identity in state metadata; dimension mismatches are errors
- One canonical state format (`state.json`)

## Quick Start

```python
from crabpath import split_workspace, HashEmbedder, VectorIndex

graph, texts = split_workspace("./workspace")
embedder = HashEmbedder()
index = VectorIndex()
for nid, content in texts.items():
    index.upsert(nid, embedder.embed(content))
```

## Embeddings and LLM callbacks

- Default: `HashEmbedder` (hash-v1, 1024-dim)
- Real: callback `embed_fn` / `embed_batch_fn` (e.g., `text-embedding-3-small`)
- LLM routing: callback `llm_fn` using `gpt-5-mini` (example)

## Session Replay

`replay_queries(graph, queries)` can warm-start from historical turns.

## CLI

`--state` is preferred:

`crabpath query TEXT --state S [--top N] [--json]`
`crabpath query TEXT --state S --chat-id CID`

`crabpath doctor --state S`
`crabpath info --state S`
`crabpath init --workspace W --output O --embedder openai`
`crabpath query TEXT --state S --llm openai`
`crabpath inject --state S --type TEACHING [--type DIRECTIVE]`

Real-time correction flow:
`python3 query_brain.py --chat-id CHAT_ID`
`python3 learn_correction.py --chat-id CHAT_ID`

## Quick Reference
- `crabpath init/query/learn/inject/health/doctor/info`
- `query_brain.py --chat-id` and `learn_correction.py` for real-time correction pipelines
- `query_brain.py` traversal limits: `beam_width=8`, `max_hops=30`, `fire_threshold=0.01`
- Hard traversal caps: `max_fired_nodes` and `max_context_chars` (defaults `None`; `query_brain.py` defaults `max_context_chars=20000`)
- `examples/correction_flow/`, `examples/cold_start/`, `examples/openai_embedder/`

## API Reference

- Core lifecycle:
  - `split_workspace`
  - `load_state`
  - `save_state`
  - `ManagedState`
  - `VectorIndex`
- Traversal and learning:
  - `traverse`
  - `TraversalConfig`
  - `TraversalConfig.beam_width`, `.max_hops`, `.fire_threshold`, `.max_fired_nodes`, `.max_context_chars`, `.reflex_threshold`, `.habitual_range`, `.inhibitory_threshold`
  - `TraversalResult`
  - `apply_outcome`
- Runtime injection APIs:
  - `inject_node`
  - `inject_correction`
  - `inject_batch`
- Maintenance helpers:
  - `suggest_connections`, `apply_connections`
  - `suggest_merges`, `apply_merge`
  - `measure_health`, `autotune`, `replay_queries`
- Embedding utilities:
  - `HashEmbedder`
  - `OpenAIEmbedder`
  - `default_embed`
  - `default_embed_batch`
  - `openai_llm_fn`
- LLM routing callbacks:
  - `chat_completion`
- Graph primitives:
  - `Node`
  - `Edge`
  - `Graph`
  - `split_workspace`
  - `generate_summaries`

## CLI Commands

- `crabpath init --workspace W --output O [--sessions S] [--embedder openai]`
- `crabpath query TEXT --state S [--top N] [--json] [--chat-id CHAT_ID]`
- `crabpath learn --state S --outcome N --fired-ids a,b,c [--json]`
- `crabpath inject --state S --id NODE_ID --content TEXT [--type CORRECTION|TEACHING|DIRECTIVE] [--json] [--connect-min-sim 0.0]`
- `crabpath inject --state S --id NODE_ID --content TEXT --type TEACHING`
- `crabpath inject --state S --id NODE_ID --content TEXT --type DIRECTIVE`
- `crabpath health --state S`
- `crabpath doctor --state S`
- `crabpath info --state S`
- `crabpath replay --state S --sessions S`
- `crabpath merge --state S [--llm openai]`
- `crabpath connect --state S [--llm openai]`
- `crabpath journal [--stats]`
- `query_brain.py --chat-id CHAT_ID`
- `learn_correction.py --chat-id CHAT_ID`

## Traversal defaults

- `beam_width=8`
- `max_hops=30`
- `fire_threshold=0.01`
- `reflex_threshold=0.6`
- `habitual_range=0.2-0.6`
- `inhibitory_threshold=-0.01`
- `max_fired_nodes` (hard node-count cap, default `None`)
- `max_context_chars` (hard context cap, default `None`; `query_brain.py` default is `20000`)

## Paper

https://jonathangu.com/crabpath/
