---
name: Clude Memory MCP
description: MCP server for Clude's 4-tier cognitive memory system — store, recall, search, and dream. Built on Supabase + pgvector with type-specific decay, Hebbian association graphs, and on-chain commitment via Solana.
metadata:
  openclaw:
    requires:
      env:
        - SUPABASE_URL
        - SUPABASE_SERVICE_KEY
      bins:
        - node
    primaryEnv: SUPABASE_URL
---

# Clude Memory MCP

MCP server exposing a 4-tier cognitive memory architecture inspired by Stanford's Generative Agents (Park et al. 2023).

## Tools

### `recall_memories`
Search the memory system. Returns scored memories ranked by relevance, importance, recency, and vector similarity.

- `query` — text to search against memory summaries
- `tags` — filter by tags
- `related_user` — filter by user/agent ID
- `memory_types` — filter by type: `episodic`, `semantic`, `procedural`, `self_model`
- `limit` — max results (1-20, default 5)
- `min_importance` — minimum importance threshold (0-1)

### `store_memory`
Store a new memory. Memories persist across conversations, decay over time if not accessed, and get committed to Solana.

- `type` — `episodic` (events), `semantic` (knowledge), `procedural` (behaviors), `self_model` (identity)
- `content` — full memory content
- `summary` — short summary for recall matching
- `tags` — tags for filtering
- `importance` — importance score 0-1
- `source` — origin identifier (e.g. `mcp:my-agent`)

### `get_memory_stats`
Get statistics: counts by type, average importance/decay, dream session history, top tags.

### `get_market_mood`
Get current market mood and price state (no LLM call).

### `ask_clude`
Ask Clude a question and get an in-character response. Calls Claude API.

## Setup

```bash
npm install clude-bot
```

Requires a Supabase project with the schema from `supabase-schema.sql`. Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` environment variables.

## Architecture

- **4-tier memory**: episodic (7%/day decay), semantic (2%/day), procedural (3%/day), self_model (1%/day)
- **Hybrid retrieval**: pgvector cosine similarity + keyword matching + tag scoring
- **Dream cycles**: consolidation, reflection, emergence — every 6 hours
- **On-chain commitment**: SHA-256 hashed memories committed to Solana via memo transactions
- **Granular decomposition**: per-fragment embeddings for precise sub-memory retrieval

## License

MIT
