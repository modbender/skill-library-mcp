# chromadb-memory

Long-term memory via ChromaDB with local Ollama embeddings. Auto-recall injects relevant context every turn. No cloud APIs required — fully self-hosted.

## ⚠️ Important: Upgrade to v1.1.1

**v1.0.0 had a critical silent failure bug.** If your indexer/reindexer deletes and recreates the ChromaDB collection (which most do), the collection UUID changes — and v1.0.0 used a hardcoded UUID in the config. This meant **auto-recall silently stopped working** after the first reindex, with no error message. You'd have no idea your long-term memory was gone.

**v1.1.0** fixes this by resolving collections by **name** instead of UUID. It survives reindexing automatically.

**v1.1.1** adds error surfacing — if ChromaDB is unreachable or the collection is missing, the agent now sees a warning in its context instead of silent failure.

**v1.2.0** adds hybrid search — combines vector similarity with keyword matching for much better proper noun recall (names, places, specific terms).

**To upgrade:** Update the plugin files and add `collectionName` to your config (default: `longterm_memory`). The `collectionId` field is no longer required.

## Setup

### Requirements
- ChromaDB v2 server (local or remote)
- Ollama with `nomic-embed-text` model (or any embedding model)
- An indexed collection in ChromaDB

### Config

```json
{
  "chromadb-memory": {
    "enabled": true,
    "config": {
      "chromaUrl": "http://localhost:8100",
      "collectionName": "longterm_memory",
      "ollamaUrl": "http://localhost:11434",
      "embeddingModel": "nomic-embed-text",
      "autoRecall": true,
      "autoRecallResults": 3,
      "minScore": 0.5
    }
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `chromaUrl` | `http://localhost:8100` | ChromaDB server URL |
| `collectionName` | `longterm_memory` | Collection name (recommended — survives reindexing) |
| `collectionId` | — | Collection UUID (optional, fallback if name fails) |
| `ollamaUrl` | `http://localhost:11434` | Ollama server URL |
| `embeddingModel` | `nomic-embed-text` | Embedding model name |
| `autoRecall` | `true` | Inject relevant memories before each agent turn |
| `autoRecallResults` | `3` | Number of memories to inject |
| `minScore` | `0.5` | Minimum similarity score (0-1) |

## Features

- **Auto-recall**: Relevant memories injected into agent context before each turn
- **Manual search**: `chromadb_search` tool for explicit queries
- **Name-based resolution**: Collection UUID auto-resolved from name (v1.1.0+)
- **Error surfacing**: Agent sees warnings when ChromaDB is unavailable (v1.1.1+)
- **Self-healing**: Cached collection ID auto-invalidates on failure and re-resolves
- **Hybrid search**: Vector + keyword matching for better proper noun recall (v1.2.0+)

## Changelog

### v1.2.0
- **Hybrid search**: Combines vector similarity with keyword matching for better proper noun recall
- Extracts capitalized words and quoted phrases from queries as keywords
- Runs parallel vector + `$contains` keyword-filtered queries, merges and deduplicates results
- Score boosts: +0.1 for results found by both methods, +0.05 for keyword-only matches
- Significantly improves recall for names, places, and specific terms that embeddings struggle with

### v1.1.1
- Auto-recall failures now surface as warnings in agent context (no more silent memory loss)
- Consecutive failure counter with escalating severity
- Cache invalidation on failure forces collection re-resolve

### v1.1.0
- New `collectionName` config option (default: `longterm_memory`)
- Auto-resolves collection UUID from name — survives reindexing
- `collectionId` no longer required (backwards compatible)

### v1.0.0
- Initial release
- ⚠️ Hardcoded `collectionId` breaks silently after reindexing
