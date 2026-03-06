---
name: Valence Memory
description: Persistent knowledge substrate for OpenClaw. Replaces flat-file
  memory with confidence-scored beliefs, semantic search, pattern recognition,
  and federated knowledge sharing.
---

# Valence Memory

Persistent knowledge substrate for OpenClaw. Replaces flat-file memory with confidence-scored beliefs, semantic search, pattern recognition, and federated knowledge sharing.

## What It Does

Valence gives your agent **real memory** — not conversation logs, but a structured knowledge base that grows smarter over time:

- **Beliefs** — Factual statements with dimensional confidence scores, domain classification, and provenance tracking
- **Auto-recall** — Relevant beliefs are injected into context before the agent runs, no manual searching needed
- **Auto-capture** — Insights from conversations are extracted as beliefs automatically
- **Patterns** — Recurring behaviors and preferences are detected across sessions
- **Entities** — People, tools, projects, and concepts tracked with relationships
- **Tensions** — Contradictions between beliefs are surfaced for resolution
- **Sessions** — Full conversation lifecycle tracking with exchange recording
- **MEMORY.md sync** — Disaster-recovery fallback so you lose nothing if you uninstall

## Prerequisites

Valence requires a running server with PostgreSQL + pgvector:

```bash
# Install Valence
pip install ourochronos-valence

# Start PostgreSQL with pgvector (Docker is easiest)
docker run -d --name valence-db \
  -e POSTGRES_DB=valence \
  -e POSTGRES_USER=valence \
  -e POSTGRES_PASSWORD=valence \
  -p 5432:5432 \
  pgvector/pgvector:pg17

# Run migrations
valence-server migrate up

# Start the server
valence-server
```

The server runs at `http://127.0.0.1:8420` by default.

## Install the Plugin

```bash
openclaw plugins install @ourochronos/memory-valence
```

## Configure

Add to your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "plugins": {
    "slots": {
      "memory": "memory-valence"
    },
    "entries": {
      "memory-valence": {
        "enabled": true,
        "config": {
          "serverUrl": "http://127.0.0.1:8420",
          "autoRecall": true,
          "autoCapture": true,
          "sessionTracking": true,
          "memoryMdSync": true
        }
      }
    }
  }
}
```

Or use the OpenClaw Control UI to configure via the web interface.

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `serverUrl` | `http://127.0.0.1:8420` | Valence server URL |
| `authToken` | — | Bearer token (or set `VALENCE_AUTH_TOKEN` env var) |
| `autoRecall` | `true` | Inject relevant beliefs before agent runs |
| `autoCapture` | `true` | Extract insights from conversations |
| `sessionTracking` | `true` | Track OpenClaw sessions in Valence |
| `exchangeRecording` | `false` | Record individual conversation turns |
| `memoryMdSync` | `true` | Sync beliefs to MEMORY.md as DR fallback |
| `recallMaxResults` | `10` | Max beliefs injected on auto-recall |
| `recallMinScore` | `0.5` | Minimum relevance score for recall (0-1) |

## Agent Tools

The plugin exposes 58 tools organized by category:

### Core (used most often)
- `belief_create` / `belief_query` / `belief_search` / `belief_get` — Create and find beliefs
- `belief_supersede` — Update a belief while preserving history
- `belief_archive` — Archive a belief (GDPR-compliant, maintains chain)
- `confidence_explain` — Understand why a belief has its confidence score
- `entity_search` / `entity_get` — Find and inspect entities
- `tension_list` / `tension_resolve` — Surface and resolve contradictions
- `insight_extract` — Extract an insight from conversation into a belief
- `pattern_search` / `pattern_record` / `pattern_reinforce` — Behavioral patterns
- `memory_search` / `memory_get` — Search and read MEMORY.md (DR fallback)

### Sharing & Federation
- Share beliefs with trusted peers, query across federated nodes
- Trust verification, reputation tracking, dispute resolution
- Backup export/import for portability

### VKB (Virtual Knowledge Base)
- Session lifecycle management
- Exchange recording
- Advanced pattern and insight tools

## How It Works

1. **On each agent turn**, auto-recall searches Valence for beliefs relevant to the current conversation and injects them as context
2. **During conversations**, the agent uses belief tools to capture decisions, preferences, and insights
3. **After conversations**, auto-capture extracts any uncaptured insights
4. **Over time**, beliefs accumulate confidence through corroboration, patterns emerge from repeated observation, and the agent's understanding deepens
5. **MEMORY.md** is kept in sync as a human-readable snapshot and safety net

## Architecture

```
OpenClaw Agent
    ↕ (plugin tools + hooks)
memory-valence plugin
    ↕ (REST API)
Valence Server (http://127.0.0.1:8420)
    ↕ (SQL + pgvector)
PostgreSQL + pgvector
```

The plugin is a thin REST client. All intelligence lives in the Valence server — embeddings, confidence scoring, pattern detection, and federation protocol.

## Links

- **Valence**: [github.com/ourochronos/valence](https://github.com/ourochronos/valence) | [PyPI](https://pypi.org/project/ourochronos-valence/)
- **Plugin**: [github.com/ourochronos/valence-openclaw](https://github.com/ourochronos/valence-openclaw) | [npm](https://www.npmjs.com/package/@ourochronos/memory-valence)
- **Issues**: [github.com/ourochronos/valence/issues](https://github.com/ourochronos/valence/issues)
