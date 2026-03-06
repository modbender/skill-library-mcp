# Jasper Recall - OpenClaw Plugin

Semantic search over indexed memory using ChromaDB. Automatically injects relevant context before agent processing.

## Features

- **`recall` tool** — Manual semantic search over memory
- **`/recall` command** — Quick lookups from chat
- **`/index` command** — Re-index memory files
- **Auto-recall** — Automatically inject relevant memories before processing

---

## Auto-Recall (The Magic ✨)

When `autoRecall` is enabled, jasper-recall hooks into the agent lifecycle and automatically searches your memory before every message is processed.

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. Message arrives from user                               │
│  2. before_agent_start hook fires                           │
│  3. jasper-recall searches ChromaDB with message as query   │
│  4. Results filtered by minScore (default: 30%)             │
│  5. Relevant memories injected via prependContext           │
│  6. Agent sees memories + original message                  │
│  7. Agent responds with full context                        │
└─────────────────────────────────────────────────────────────┘
```

### What Gets Injected

```xml
<relevant-memories>
The following memories may be relevant to this conversation:
- [memory/2026-02-05.md] Worker orchestration decisions...
- [MEMORY.md] Git workflow: feature → develop → main...
- [memory/sops/codex-integration-sop.md] Codex Cloud sync...
</relevant-memories>
```

### What's Skipped

Auto-recall won't run for:
- Heartbeat polls (`HEARTBEAT...`)
- System prompts containing `NO_REPLY`
- Messages shorter than 10 characters

---

## Configuration

In `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "jasper-recall": {
        "enabled": true,
        "config": {
          "autoRecall": true,
          "minScore": 0.3,
          "defaultLimit": 5,
          "publicOnly": false
        }
      }
    }
  }
}
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable plugin |
| `autoRecall` | boolean | `false` | Auto-inject memories before processing |
| `minScore` | number | `0.3` | Minimum similarity score (0-1) for auto-recall |
| `defaultLimit` | number | `5` | Default number of results |
| `publicOnly` | boolean | `false` | Only search public memory (sandboxed agents) |

### Score Tuning

- `minScore: 0.3` — Include loosely related memories (more context, may include noise)
- `minScore: 0.5` — Only moderately relevant (balanced)
- `minScore: 0.7` — Only highly relevant (precise, may miss useful context)

---

## Tools

### `recall`

Manual semantic search over memory.

**Parameters:**
- `query` (string, required): Natural language search query
- `limit` (number, optional): Max results (default: 5)

**Example:**
```
recall query="what did we decide about the API design" limit=3
```

**Returns:** Formatted markdown with matching memories, scores, and sources.

---

## Commands

### `/recall <query>`

Quick memory search from chat.

```
/recall worker orchestration decisions
```

### `/index`

Re-index memory files into ChromaDB. Run after updating notes.

```
/index
```

---

## RPC Methods

For external integrations:

### `recall.search`

```json
{ "query": "search terms", "limit": 5 }
```

### `recall.index`

Re-index memory files (no params).

---

## Requirements

- `recall` command in `~/.local/bin/`
- ChromaDB index at `~/.openclaw/chroma-db`
- Python venv at `~/.openclaw/rag-env`

## Installation

```bash
npx jasper-recall setup
```

This sets up:
1. Python venv with ChromaDB + sentence-transformers
2. `recall`, `index-digests`, `digest-sessions` scripts
3. Initial index of memory files

---

## When Auto-Recall Helps

✅ **Great for:**
- Questions about past decisions ("what did we decide about X?")
- Following up on previous work ("where were we with the worker setup?")
- Context about people, preferences, projects
- Finding SOPs and procedures

⚠️ **Less useful for:**
- Brand new topics with no memory
- Simple commands ("list files")
- Real-time data (weather, time)

---

## Sandboxed Agents

For agents processing untrusted input, use `publicOnly`:

```json
{
  "jasper-recall": {
    "config": {
      "publicOnly": true,
      "autoRecall": true
    }
  }
}
```

This restricts searches to `memory/shared/` and public-tagged content, preventing leakage of private memories.

---

## Links

- **GitHub**: https://github.com/E-x-O-Entertainment-Studios-Inc/jasper-recall
- **npm**: `npx jasper-recall setup`
- **ClawHub**: `clawhub install jasper-recall`
