---
name: smart-memory
description: Context-aware memory for AI agents with dual retrieval modes — fast vector search or curated Focus Agent synthesis. SQLite backend, zero configuration, local embeddings.
---

# Smart Memory v2.1 - Focus Agent Edition

**Drop-in replacement for OpenClaw's memory system** with superior search quality and optional curated retrieval via Focus Agent.

## Features

- **Hybrid Search**: Combines FTS5 keyword search (BM25) with semantic vector search
- **Focus Agent**: Multi-pass curation for complex queries (retrieve → rank → synthesize)
- **Dual Modes**: Fast (direct) or Focus (curated) — toggle anytime
- **SQLite Backend**: Single-file database, no external services
- **100% Local**: Embeddings run locally with Transformers.js (no API keys)
- **Auto-Optimization**: Uses sqlite-vec when available for native vector ops
- **Zero Configuration**: Works immediately after install

## Installation

```bash
npx clawhub install smart-memory
```

Or from ClawHub: https://clawhub.ai/BluePointDigital/smart-memory

## Quick Start

### 1. Sync Memory
```bash
node smart-memory/smart_memory.js --sync
```

### 2. Search (Fast Mode - Default)
```bash
node smart-memory/smart_memory.js --search "James values principles"
```

### 3. Enable Focus Mode (Curated Retrieval)
```bash
node smart-memory/smart_memory.js --focus
node smart-memory/smart_memory.js --search "complex decision about project direction"
```

### 4. Disable Focus Mode
```bash
node smart-memory/smart_memory.js --unfocus
```

## Search Modes

### Fast Mode (Default)
Direct vector similarity search. Best for:
- Simple lookups
- Quick fact retrieval
- Routine queries

```bash
node smart-memory/smart_memory.js --search "git remote"
```

### Focus Mode (Curated)
Multi-pass curation via Focus Agent. Best for:
- Complex decisions
- Multi-fact synthesis
- Planning and strategy
- Comparing options

```bash
node smart-memory/smart_memory.js --focus
node smart-memory/smart_memory.js --search "What did we decide about BluePointDigital architecture?"
```

**How Focus Mode Works:**
1. **Retrieve** 20+ chunks (broad net)
2. **Rank** by weighted relevance (vector + term matching + source boost)
3. **Synthesize** into coherent narrative
4. **Deliver** structured context with confidence scores

## How It Works

### Hybrid Search Algorithm

1. **FTS5** finds exact keyword matches (BM25 ranking)
2. **Vector search** finds semantic matches (cosine similarity)
3. **Merged results** using weighted scoring:
   - 70% vector score + 30% keyword score
   - Catches both "what you mean" and "exact tokens"

### Focus Agent Curation

When enabled, searches go through additional processing:

```
Query: "What did we decide about BluePointDigital?"

┌─────────────────┐
│  Retrieve 20+   │  ← Vector similarity
│    chunks       │
└────────┬────────┘
         ▼
┌─────────────────┐
│   Weighted      │  ← Term matching
│    Ranking      │    Source boosting
│                 │    Recency boost
└────────┬────────┘
         ▼
┌─────────────────┐
│   Select Top 5  │  ← Threshold filtering
└────────┬────────┘
         ▼
┌─────────────────┐
│   Synthesize    │  ← Group by source
│   Narrative     │    Extract key facts
└────────┬────────┘
         ▼
    Structured output with confidence
```

## Tools

### memory_search
```javascript
memory_search({
    query: "deployment configuration",
    maxResults: 5
})
```

Returns (Fast Mode):
```json
{
    "query": "deployment configuration",
    "mode": "fast",
    "results": [
        {
            "path": "MEMORY.md",
            "from": 42,
            "lines": 8,
            "score": 0.89,
            "snippet": "..."
        }
    ]
}
```

Returns (Focus Mode):
```json
{
    "query": "deployment configuration",
    "mode": "focus",
    "confidence": 0.87,
    "sources": ["MEMORY.md", "memory/2026-02-05.md"],
    "synthesis": "Relevant context for: \"deployment configuration\"\n\nFrom MEMORY.md:\n  • Docker setup uses docker-compose...\n  • Production deployment on AWS...\n\nFrom memory/2026-02-05.md:\n  • Decided to use Railway instead...",
    "facts": [
        {
            "content": "Docker setup uses docker-compose...",
            "source": "MEMORY.md",
            "lines": "42-50",
            "confidence": 0.89
        }
    ]
}
```

### memory_get
```javascript
memory_get({
    path: "MEMORY.md",
    from: 42,
    lines: 10
})
```

### memory_mode (Focus Toggle)
```javascript
memory_mode('focus')    // Enable curated retrieval
memory_mode('fast')     // Disable curated retrieval
memory_mode()           // Get current mode status
```

## CLI Commands

```bash
# Sync memory files
node smart_memory.js --sync

# Search (uses current mode)
node smart_memory.js --search "query" [--max-results N]

# Search with mode override
node smart_memory.js --search "query" --focus
node smart_memory.js --search "query" --fast

# Toggle modes
node smart_memory.js --focus      # Enable focus mode
node smart_memory.js --unfocus    # Disable focus mode
node smart_memory.js --fast       # Same as --unfocus

# Check status
node smart_memory.js --status     # Database stats + current mode
node smart_memory.js --mode       # Current mode details

# Focus agent only
node focus_agent.js --search "query"
node focus_agent.js --suggest "query"  # Check if focus recommended

# Mode management
node memory_mode.js focus
node memory_mode.js unfocus
node memory_mode.js status
```

## Performance

| Feature | Fallback | With sqlite-vec |
|---------|----------|-----------------|
| Keyword search | FTS5 (native) | FTS5 (native) |
| Vector search | JS cosine | Native KNN |
| Focus curation | +50-100ms | +50-100ms |
| Speed | ~100 chunks/sec | ~10,000 chunks/sec |
| Memory | All in RAM | DB handles it |

## When to Use Focus Mode

Use `--focus` or enable focus mode when:
- Query involves multiple related concepts
- You need synthesized context, not raw chunks
- Making decisions that require understanding relationships
- Summarizing project history
- Comparing options mentioned in different files

Don't use focus mode when:
- Quick fact lookup (phone number, command syntax)
- You need exact text matches
- Latency matters more than context quality

## Installation: sqlite-vec (Optional)

For best performance, install sqlite-vec:

```bash
# macOS
brew install sqlite-vec

# Ubuntu/Debian
# Download from https://github.com/asg017/sqlite-vec/releases
# Place vec0.so in ~/.local/lib/ or /usr/local/lib/
```

Without it: Works fine, just slower on large databases.

## File Structure

```
smart-memory/
├── smart_memory.js      # Main CLI
├── focus_agent.js       # Curated retrieval engine
├── memory_mode.js       # Mode toggle commands
├── memory.js            # OpenClaw wrapper
├── db.js                # SQLite layer
├── search.js            # Hybrid search
├── chunker.js           # Token-based chunking
├── embed.js             # Transformers.js embeddings
└── vector-memory.db     # SQLite database (auto-created)
```

## Environment Variables

```bash
MEMORY_DIR=/path/to/memory        # Default: ./memory
MEMORY_FILE=/path/to/MEMORY.md    # Default: ./MEMORY.md
MEMORY_DB_PATH=/path/to/db.sqlite # Default: ./vector-memory.db
```

## Comparison: v1 vs v2 vs v2.1

| | v1 (JSON) | v2 (SQLite) | v2.1 (Focus Agent) |
|--|-----------|-------------|-------------------|
| Search | Vector only | Hybrid (BM25 + Vector) | Hybrid + Focus Curation |
| Storage | JSON file | SQLite | SQLite |
| Scale | ~1000 chunks | Unlimited | Unlimited |
| Keyword match | Weak | Strong (FTS5) | Strong (FTS5) |
| Context curation | No | No | Yes (toggle) |
| Setup | Zero config | Zero config | Zero config |

## License

MIT
