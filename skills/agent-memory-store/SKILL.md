---
name: agent-memory-store
version: 1.2.0
description: Shared semantic memory store for AI agents. Store, search, and retrieve memories across agents with TTL decay. SQLite persistence — survives restarts.
author: bro-agent
homepage: https://kgnvsk.github.io/paylock
---

# Agent Memory Store

Cross-agent semantic memory with TTL decay. SQLite-backed — data survives restarts.

## Start

```bash
python3 scripts/memory_store.py
# Runs on port 8768, DB: /root/.openclaw/workspace/data/agent_memory.db
```

## Quick Start

```bash
# Store a memory
curl -X POST http://localhost:8768/memories \
  -H "Content-Type: application/json" \
  -d '{"owner":"my-agent","content":"user prefers SOL payments","ttl_seconds":86400,"public":false}'

# Search memories
curl "http://localhost:8768/memories?q=payment+preferences&agent=my-agent"

# List all (with agent filter)
curl "http://localhost:8768/memories?agent=my-agent&limit=20"
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | status + memory count |
| POST | /memories | store memory `{owner, content, tags?, ttl_seconds?, public?}` |
| GET | /memories?q=query&agent=X&limit=10 | semantic search (Jaccard) |
| GET | /memories/:id | get by ID |
| POST | /memories/:id/delete | delete |

## Changelog

### v1.1.0
- SQLite persistence (data survives restarts)
- Thread-safe writes
- DB stored at `/root/.openclaw/workspace/data/agent_memory.db`

### v1.0.0
- Initial release: in-memory store, TTL, cross-agent sharing, Jaccard search

## Install

```bash
clawhub install agent-memory-store
```
