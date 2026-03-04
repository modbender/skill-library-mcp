---
name: mnemo-memory
version: 0.2.0
description: "Cloud-persistent memory for AI agents. Stateless plugins + TiDB Serverless = cross-session recall, multi-agent sharing, and hybrid vector + keyword search. Works with OpenClaw, Claude Code, and OpenCode."
author: qiffang
keywords: [memory, agent-memory, persistent-memory, tidb, tidb-serverless, vector-search, hybrid-search, auto-embedding, cloud-memory, multi-agent, crdt, conflict-resolution, cross-session, openclaw, claude-code, opencode, stateless, ai-agent, developer-tools]
metadata:
  openclaw:
    emoji: "\U0001F9E0"
---

# mnemo — Cloud-Persistent Memory for AI Agents \U0001F9E0

**Your agents are stateless. Your memory shouldn't be.**

Every AI agent session starts from zero. Context is lost, decisions are forgotten, and your agents keep rediscovering what they already knew. mnemo externalizes agent memory into TiDB Cloud Serverless — so agents stay disposable, but memory persists forever.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Claude Code  │     │  OpenCode   │     │  OpenClaw   │
│   Plugin     │     │   Plugin    │     │   Plugin    │
└──────┬───────┘     └──────┬──────┘     └──────┬──────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────┴────────┐
                    │  mnemo-server  │  ← optional (team mode)
                    └───────┬────────┘
                            │
                    ┌───────┴────────┐
                    │   TiDB Cloud   │  ← zero-ops, free tier
                    │   Serverless   │
                    │                │
                    │  • VECTOR type │
                    │  • EMBED_TEXT  │
                    │  • HTTP API    │
                    └────────────────┘
```

## What Problem Does This Solve?

| Pain Point | Without mnemo | With mnemo |
|---|---|---|
| **Session amnesia** | Agent forgets everything on restart | Memory persists in the cloud |
| **Machine-locked** | Memory in local files, lost on device switch | Same memory from any machine |
| **Agent silos** | Claude can't see what OpenCode learned | All agents share one memory pool |
| **Team isolation** | Teammate's agent starts from scratch | Shared spaces with per-agent tokens |
| **No semantic search** | Grep through flat files | Hybrid vector + keyword search |
| **Concurrent conflicts** | Last write silently overwrites | CRDT vector clocks detect & resolve |

## Why TiDB Cloud Serverless?

mnemo chose [TiDB Cloud Serverless](https://tidbcloud.com) because it uniquely combines everything agent memory needs — in one service, at zero cost:

- **Native `VECTOR` type** — Semantic search in the same table as your metadata. No separate vector database.
- **`EMBED_TEXT()` auto-embedding** — TiDB generates embeddings server-side (e.g. `tidbcloud_free/amazon/titan-embed-text-v2`). No OpenAI API key required for semantic search.
- **HTTP Data API** — Agents talk to TiDB via `fetch`/`curl`. No database drivers, no connection pools.
- **Free tier** — 25 GiB storage, 250M Request Units/month. More than enough for individual use.
- **MySQL compatible** — Migrate to self-hosted TiDB or MySQL anytime.

One database gives you relational storage + vector search + auto-embedding + HTTP access. No glue code. No infra.

## Hybrid Search: Vector + Keyword

```
              Embedding configured?
              ┌─────────┴─────────┐
             Yes                  No
              │                    │
        Hybrid search        Keyword only
        (vector + keyword)   (LIKE '%q%')
              │                    │
    ┌─────────┴─────────┐         │
 Vector results     Keyword       │
 (ANN cosine)       results       │
    └─────────┬─────────┘         │
         Merge & rank         Direct results
```

**Three embedding options — pick one or none:**
1. **TiDB auto-embedding** — `EMBED_TEXT()` generates vectors server-side. Zero config. Free.
2. **OpenAI / compatible API** — Set `MNEMO_EMBED_API_KEY`. Works with Ollama too.
3. **No embedding** — Keyword search works immediately. Add vectors later, no migration needed.

## Multi-Agent Conflict Resolution (CRDT)

When multiple agents write to the same memory, mnemo uses **vector clocks** — no coordination required:

```
Agent A: clock {A:3, B:1}        Agent B: clock {A:2, B:2}
         \                                /
          └──── Server compares ─────────┘
                       │
               Neither dominates →
               Concurrent conflict!
                       │
            Deterministic tie-break
                       │
               Winner saved, clocks merged: {A:3, B:2}
```

| Scenario | Result |
|---|---|
| A's clock dominates B's | A wins — B's write is stale |
| B's clock dominates A's | B wins — A's write is outdated |
| Concurrent (neither dominates) | Deterministic tie-break — no data loss |
| No clock sent (legacy client) | LWW fast path — backward compatible |

Deletes are soft (tombstone + clock increment) — no ghost resurrection from agents that missed the delete.

## Install for OpenClaw

```bash
npm install mnemo-openclaw
```

Add to `openclaw.json`:

```json
{
  "plugins": {
    "slots": { "memory": "mnemo" },
    "entries": {
      "mnemo": {
        "enabled": true,
        "config": {
          "host": "<your-tidb-host>",
          "username": "<your-tidb-user>",
          "password": "<your-tidb-pass>"
        }
      }
    }
  }
}
```

Get a free cluster in 30 seconds at [tidbcloud.com](https://tidbcloud.com).

**Optional — enable auto-embedding (no API key needed):**

```json
{
  "config": {
    "host": "...",
    "username": "...",
    "password": "...",
    "autoEmbedModel": "tidbcloud_free/amazon/titan-embed-text-v2",
    "autoEmbedDims": 1024
  }
}
```

## Also Works With

| Platform | Install |
|---|---|
| **Claude Code** | `/plugin marketplace add qiffang/mnemos` → `/plugin install mnemo-memory@mnemos` |
| **OpenCode** | `"plugin": ["mnemo-opencode"]` in `opencode.json` |
| **Any HTTP client** | REST API or TiDB HTTP Data API directly |

## 5 Memory Tools

| Tool | What it does |
|---|---|
| `memory_store` | Store a memory (upsert by key, with optional CRDT clock) |
| `memory_search` | Hybrid vector + keyword search across all memories |
| `memory_get` | Retrieve a single memory by ID |
| `memory_update` | Update an existing memory |
| `memory_delete` | Soft delete with tombstone (CRDT-aware) |

## Two Modes, One Plugin

| | Direct Mode | Server Mode |
|---|---|---|
| **For** | Individual developers | Teams with multiple agents |
| **Backend** | Plugin → TiDB Serverless | Plugin → mnemo-server → TiDB |
| **Deploy** | Nothing — free tier | Self-host Go binary |
| **Features** | Hybrid search, auto-embedding | + Space isolation, per-agent tokens, CRDT |

Mode is inferred from config. Start personal, scale to team — no code change.

## Links

- **GitHub**: [github.com/qiffang/mnemos](https://github.com/qiffang/mnemos)
- **Design Doc**: [docs/DESIGN.md](https://github.com/qiffang/mnemos/blob/main/docs/DESIGN.md)
- **CRDT Proposal**: [crdt-memory-proposal.md](https://github.com/qiffang/mnemos/blob/main/claude-notes/crdt-memory-proposal.md)
- **TiDB Cloud Serverless**: [tidbcloud.com](https://tidbcloud.com) (free tier)

---

*Built for agents that need to remember. Powered by [TiDB Cloud Serverless](https://tidbcloud.com).*
