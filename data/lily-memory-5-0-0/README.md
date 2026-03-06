# lily-memory

Persistent memory plugin for OpenClaw agents. Hybrid keyword + semantic search with auto-capture, stuck-detection, and zero npm dependencies.

## Features

- **SQLite FTS5 keyword search + Ollama vector cosine similarity** — Find memories by exact keywords and by meaning
- **Auto-capture** — Extract facts from conversations via regex patterns and entity validation
- **Auto-recall** — Inject relevant memories before each LLM turn
- **Stuck-detection** — Jaccard similarity on topic signatures with Reflexion-enhanced nudging
- **Memory consolidation** — Dedup on startup and refresh permanent memories on compaction
- **Compaction-aware** — Resets topic state and touches permanent facts when context compresses
- **Dynamic entity management** — Config-driven allowlist plus runtime tool to add entities
- **Graceful degradation** — Works without Ollama (keyword-only mode)
- **Zero npm dependencies** — sqlite3 CLI + native fetch

## Requirements

- Node.js 18+ (for native `fetch`)
- SQLite 3.33+ with FTS5 (ships with macOS; `apt install sqlite3` on Linux)
- Optional: Ollama with `nomic-embed-text` model for vector search

## Installation

```bash
mkdir -p ~/.openclaw/extensions/lily-memory
cp -r . ~/.openclaw/extensions/lily-memory/
```

## Configuration

Add this to your `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "slots": {
      "memory": "lily-memory"
    },
    "entries": {
      "lily-memory": {
        "enabled": true,
        "config": {
          "dbPath": "~/.openclaw/memory/decisions.db",
          "autoRecall": true,
          "autoCapture": true,
          "maxRecallResults": 10,
          "maxCapturePerTurn": 5,
          "stuckDetection": true,
          "vectorSearch": true,
          "ollamaUrl": "http://localhost:11434",
          "embeddingModel": "nomic-embed-text",
          "consolidation": true,
          "vectorSimilarityThreshold": 0.5,
          "entities": []
        }
      }
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dbPath` | string | `~/.openclaw/memory/decisions.db` | Path to SQLite database (supports `~` for home) |
| `autoRecall` | boolean | `true` | Inject relevant memories before each LLM turn |
| `autoCapture` | boolean | `true` | Extract and store facts from conversation messages |
| `maxRecallResults` | number | `10` | Maximum memories to inject per turn (1-50) |
| `maxCapturePerTurn` | number | `5` | Maximum facts to extract per response (1-20) |
| `stuckDetection` | boolean | `true` | Detect topic repetition and inject nudge |
| `vectorSearch` | boolean | `true` | Enable semantic search via Ollama |
| `ollamaUrl` | string | `http://localhost:11434` | Ollama API endpoint |
| `embeddingModel` | string | `nomic-embed-text` | Ollama embedding model name |
| `consolidation` | boolean | `true` | Dedup memories on plugin startup |
| `vectorSimilarityThreshold` | number | `0.5` | Minimum cosine similarity (0-1) for results |
| `entities` | array | `[]` | Additional entity names to recognize |

## Entity Management

The plugin uses a three-layer entity system:

**Layer 1: Built-in defaults**
- System: `config`, `system`, `note`, `project`

**Layer 2: Config array**
- Any names in the `entities` array in `openclaw.json`
- Example: `"entities": ["kevin", "alice", "trading_system"]`

**Layer 3: Runtime tool**
- Call `memory_add_entity(name)` to dynamically add entities
- Names are stored in the database and persist across sessions

**Special case: PascalCase auto-accept**
- Multi-word PascalCase names (e.g., `TradingSystem`, `MemoryPlugin`) are always accepted
- Useful for project names and system identifiers

## Tools

### memory_search(query: string)
FTS5 keyword search across all facts.
- Extracts keywords from query
- Returns matching entities and facts
- Includes permanent facts first
- Deduplicated results

**Example:**
```
User: "What do I know about TypeScript preferences?"
→ Searches for keywords: type, script, preference
→ Returns facts containing those terms
```

### memory_entity(entity: string)
Look up all facts for a specific entity.
- Returns complete fact set for that entity
- Sorted by importance (permanent facts first)

**Example:**
```
User: "Show all facts about Kevin"
→ Returns all Kevin-related facts in database
```

### memory_store(entity: string, key: string, value: string)
Manually store a fact (bypasses auto-capture).
- TTL defaults to "stable" (90 days) unless explicitly set
- Importance set to 0.9
- Useful for user-provided context

**Example:**
```
User: "Remember: Kevin prefers async/await over promises"
→ Stores fact: Kevin.coding_style = "prefers async/await over promises"
```

### memory_semantic_search(query: string)
Vector similarity search via Ollama embeddings.
- Finds semantically related memories even if keywords don't match
- Returns results above similarity threshold
- Falls back to keyword search if Ollama unavailable

**Example:**
```
User: "What about strongly-typed languages?"
→ Even if database says "TypeScript" (not "strongly-typed"), vector search finds it
```

### memory_add_entity(name: string)
Add a new entity to the allowlist at runtime.
- Names are validated (2-60 chars, no URLs, no common English words)
- Persisted in database
- Returns success/failure with reason

**Example:**
```
User: "Start remembering facts about Alice"
→ memory_add_entity("alice") adds alice to allowlist
```

## Architecture

### Recall Flow (before_agent_start hook)

1. Extract keywords from user message
2. Run FTS5 keyword search against decisions table
3. If Ollama available: embed query, compute cosine similarity against all vectors
4. Merge results, deduplicate by decision ID
5. Format as structured context block
6. Inject into system message

### Capture Flow (agent_end hook)

1. Scan LLM response for factual patterns (`entity: key = value`)
2. Validate each match:
   - Entity passes allowlist?
   - Value >= 15 characters?
   - No noise characters (`?()""<>`)?
   - Not in blocklist?
3. Store valid facts to SQLite (UPSERT on entity+key)
4. Fire-and-forget: embed via Ollama asynchronously
5. Extract topic signature (top 5 content words, excluding stopwords)
6. Compare with previous 3 signatures using Jaccard similarity
7. If stuck (3+ consecutive >60% overlap): build Reflexion nudge for next turn

### Consolidation (startup)

1. Find duplicate (entity, fact_key) groups
2. Keep row with latest `updated_at`, delete rest
3. Boost survivor importance +0.05 (capped at 0.95)
4. Clean orphaned vectors

### Compaction Awareness

- `before_compaction`: Touch permanent memories to refresh timestamps
- `after_compaction`: Reset topic history (conversation effectively starts fresh)

## How It Works

Before each turn: extract keywords from message → FTS5 + vector search → merge → inject context.

After each turn: regex scan for `entity: key = value` patterns → validate against entity allowlist → store → async embed.

Stuck detection: track top 5 content words per response → compare signatures with Jaccard similarity → if 3+ consecutive >60% overlap, inject alternative topics from memory.

## Testing

```bash
node --test test/*.test.js
```

Expected: 120+ tests passing across all modules (sqlite, entities, extraction, capture, recall, embeddings, consolidation, stuck-detection).

Tests use:
- Temporary SQLite databases (cleanup after each test)
- Mocked Ollama responses
- Comprehensive edge case coverage
- Zero external dependencies

## License

MIT
