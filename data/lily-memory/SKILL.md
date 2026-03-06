---
name: lily-memory
description: Persistent memory plugin for OpenClaw agents. Hybrid SQLite FTS5 keyword + Ollama vector semantic search with auto-capture, auto-recall, stuck-detection, and memory consolidation.
metadata:
  openclaw:
    requires:
      bins: [node]
      npm: [better-sqlite3]
    primaryEnv: ""
---

# Lily Memory

Persistent memory plugin for OpenClaw agents. Gives your agent long-term memory that survives session resets, compaction, and restarts.

## What It Does

- **Auto-recall**: Injects relevant memories as context before each LLM turn
- **Auto-capture**: Extracts facts from conversations and stores them automatically
- **Hybrid search**: SQLite FTS5 keyword search + Ollama vector cosine similarity
- **Stuck detection**: Detects topic repetition and nudges the agent to break loops
- **Memory consolidation**: Deduplicates entries on startup
- **Dynamic entities**: Config-driven allowlist + runtime tool to add entities
- **Graceful degradation**: Works without Ollama (keyword-only mode)
- **Minimal dependencies**: Uses better-sqlite3 for secure parameterized queries + native fetch

## Requirements

- Node.js 18+ (for native `fetch`)
- `better-sqlite3` npm package (installed via `npm install`)
- Optional: Ollama with `nomic-embed-text` model for semantic search

## Quick Start

1. Install the plugin to your extensions directory
2. Add to your `openclaw.json`:

```json
{
  "plugins": {
    "slots": { "memory": "lily-memory" },
    "entries": {
      "lily-memory": {
        "enabled": true,
        "config": {
          "dbPath": "~/.openclaw/memory/decisions.db",
          "entities": ["config", "system"]
        }
      }
    }
  }
}
```

3. Restart the gateway: `openclaw gateway restart`

## Tools

| Tool | Description |
|------|-------------|
| `memory_search` | FTS5 keyword search across all facts |
| `memory_entity` | Look up all facts for a specific entity |
| `memory_store` | Save a fact to persistent memory |
| `memory_semantic_search` | Vector similarity search via Ollama |
| `memory_add_entity` | Register a new entity at runtime |

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dbPath` | string | `~/.openclaw/memory/decisions.db` | SQLite database path |
| `autoRecall` | boolean | `true` | Inject memories before each turn |
| `autoCapture` | boolean | `true` | Extract facts from responses |
| `maxRecallResults` | number | `10` | Max memories per turn |
| `maxCapturePerTurn` | number | `5` | Max facts per response |
| `stuckDetection` | boolean | `true` | Topic repetition detection |
| `vectorSearch` | boolean | `true` | Ollama semantic search |
| `ollamaUrl` | string | `http://localhost:11434` | Ollama endpoint |
| `embeddingModel` | string | `nomic-embed-text` | Embedding model |
| `consolidation` | boolean | `true` | Dedup on startup |
| `vectorSimilarityThreshold` | number | `0.5` | Min cosine similarity |
| `entities` | array | `[]` | Additional entity names |

## Architecture

**Recall flow**: Extract keywords from message -> FTS5 + vector search -> merge and deduplicate -> inject as context

**Capture flow**: Regex scan for `entity: key = value` patterns -> validate entity against allowlist -> store to SQLite -> async embed via Ollama

**Stuck detection**: Track top 5 content words per response -> Jaccard similarity -> if 3+ consecutive >60% overlap, inject Reflexion nudge

## License

MIT
