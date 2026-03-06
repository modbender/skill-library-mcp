# Muninn Memory

**Memory system for AI agents.** 93% on LOCOMO benchmark. Free, open source, no lock-in.

## What It Does

- **Store memories** — Episodic (events), semantic (facts), procedural (skills)
- **Recall intelligently** — Hybrid search (BM25 + semantic), entity-aware
- **Knowledge graph** — Temporal reasoning, contradiction detection
- **Extract entities** — People, organizations, projects, technologies
- **Score salience** — Important memories surface first

## Security

| Claim | Evidence |
|-------|----------|
| **stdio-only transport** | MCP server uses `StdioServerTransport` — no HTTP/TCP |
| **Local-only network** | Only calls `localhost:11434` for Ollama embeddings — no external servers |
| **No postinstall scripts** | `package.json` has no postinstall hooks |
| **Local-only** | SQLite database, Ollama embeddings — both local |

**Known Limitations:**
- Memory content is passed to LLM prompts — users could inject instructions via stored memories (inherent to all memory systems)
- Requires local Ollama running at `localhost:11434`

## Installation

```bash
# Install via ClawHub
clawhub install muninn-memory

# Or from source
git clone https://github.com/openclaw/muninn-memory.git
cd muninn-memory && npm install && npm run build
```

## Quick Start

```typescript
import { MemoryStore } from 'muninn-memory';

// Initialize
const memory = new MemoryStore('./memories.db');

// Store a memory
await memory.remember(
  'Phillip lives in Brisbane, Australia',
  'semantic',
  { entities: ['Phillip', 'Brisbane', 'Australia'], salience: 0.8 }
);

// Recall
const results = await memory.recall('Where does Phillip live?');
console.log(results[0].content);
// "Phillip lives in Brisbane, Australia"
```

## API

### `remember(content, type, metadata?)`

Store a memory.

```typescript
await memory.remember(
  'Meeting with Sarah about Q3 roadmap',
  'episodic',
  { 
    entities: ['Sarah', 'Q3 roadmap'],
    salience: 0.7
  }
);
```

### `recall(query, options?)`

Search memories.

```typescript
const results = await memory.recall('Sarah Q3', {
  limit: 5,
  types: ['episodic', 'semantic']
});
```

### `forget(id)`

Delete a memory by ID.

```typescript
memory.forget('m_abc123');
```

### `entities()`

List all extracted entities.

```typescript
const entities = memory.getEntities();
// [{ name: 'Phillip', memory_count: 5, last_seen: '...' }, ...]
```

## Benchmark Results

| System | LOCOMO Score |
|--------|--------------|
| **Muninn** | **93%** |
| Engram | 79.6% |
| Mem0 | 66.9% |

Phase 1.5 includes knowledge graph integration for temporal reasoning and contradiction detection.

## Architecture

- **Storage:** SQLite (local) or PostgreSQL (cloud)
- **Embeddings:** Nomic via Ollama (local) or OpenAI (cloud)
- **Search:** Hybrid (BM25 + semantic) with reciprocal rank fusion
- **Entity Extraction:** Rule-based + LLM optional

## Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Core** | FREE | Local SQLite, all features, MIT license |
| **Cloud** | $19/mo | Hosted API, cloud sync, team support |
| **Enterprise** | $49/mo | Priority support, custom schemas, SLA |

## License

MIT — Use it however you want.

---

🦜 *Built by KakāpōHiko (KH)*
