---
name: muninn-memory
version: "1.0.5"
description: Memory system for AI agents. Store, recall, and manage memories with semantic search, entity extraction, and salience scoring. Works locally with SQLite and Ollama. Free tier: full features, no restrictions.
install: "clawhub install muninn-memory"
type: skill
repository: https://github.com/openclaw/muninn-memory
author: KakāpōHiko (KH)
---

# Muninn Memory

A local-first memory system for AI agents. Store episodic, semantic, and procedural memories with intelligent retrieval.

## Installation

```bash
clawhub install muninn-memory
```

Or install from source:
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/openclaw/muninn-memory.git
cd muninn-memory
npm install && npm run build
```

## Requirements

- **Node.js** 18+
- **Ollama** running locally (for embeddings)
- **SQLite** (included)

## Quick Start

```typescript
import { MemoryStore } from 'muninn-memory';

// Initialize (creates SQLite DB)
const memory = new MemoryStore('./memories.db');

// Store a memory
const mem = await memory.remember(
  'Phillip lives in Brisbane, Australia',
  'semantic',
  { entities: ['Phillip', 'Brisbane', 'Australia'], salience: 0.8 }
);
console.log('Stored:', mem.id);

// Recall memories
const results = await memory.recall('Where does Phillip live?');
console.log(results[0].content);
// "Phillip lives in Brisbane, Australia"

// Get stats
console.log(memory.getStats());
// { total: 1, byType: { episodic: 0, semantic: 1, procedural: 0 }, entities: 3, edges: 0, procedures: 0 }

memory.close();
```

## Memory Types

| Type | Use Case |
|------|----------|
| `episodic` | Events, conversations, experiences |
| `semantic` | Facts, knowledge, relationships |
| `procedural` | Skills, workflows, step-by-step processes |

## API

### `remember(content, type, options?)`

Store a new memory.

```typescript
await memory.remember(
  'Meeting with Sarah about Q3 roadmap',
  'episodic',
  { 
    entities: ['Sarah', 'Q3 roadmap'],
    salience: 0.7,
    title: 'Q3 Planning Meeting'
  }
);
```

**Options:**
- `title?: string` - Short title
- `summary?: string` - Brief summary
- `entities?: string[]` - Extracted entities
- `topics?: string[]` - Topics/tags
- `salience?: number` - Importance 0-1 (default: 0.5)

**Returns:** `Memory` object with id, content, type, entities, etc.

### `recall(query, options?)`

Search memories using hybrid search.

```typescript
const results = await memory.recall('Sarah Q3', {
  limit: 5,
  types: ['episodic', 'semantic'],
  entities: ['Sarah'],
  topics: ['planning']
});
```

**Options:**
- `types?: MemoryType[]` - Filter by type
- `entities?: string[]` - Filter by entity
- `topics?: string[]` - Filter by topic
- `limit?: number` - Max results (default: 10)

**Returns:** Array of `Memory` objects sorted by relevance.

### `forget(id, hard?)`

Delete a memory.

```typescript
// Soft delete (can be recovered)
memory.forget('m_abc123');

// Hard delete (permanent)
memory.forget('m_abc123', true);
```

### `getEntities()`

List all extracted entities.

```typescript
const entities = memory.getEntities();
// [{ name: 'Phillip', memory_count: 5, last_seen: '2026-02-24...' }, ...]
```

### `getStats()`

Get vault statistics.

```typescript
const stats = memory.getStats();
// { total: 42, byType: {...}, entities: 15, edges: 8, procedures: 3 }
```

## CLI Usage

```bash
# Run tests
node dist/index.js test

# Start MCP server (for agent integration)
npm run mcp
```

## MCP Server

Start the MCP server for agent integration:

```bash
npm run mcp
```

**Security Verification:**

| Claim | Evidence |
|-------|----------|
| **stdio-only transport** | `src/mcp/server.ts:5` imports `StdioServerTransport` from `@modelcontextprotocol/sdk/server/stdio.js` — no HTTP/TCP listeners |
| **Local-only network** | Only `fetch('http://localhost:11434/...')` for Ollama embeddings — no external servers |
| **No postinstall scripts** | `package.json` has no `postinstall`, `preinstall`, or `postbuild` scripts |
| **Dependencies** | Only `better-sqlite3` (local DB), `ollama` (local embeddings), `uuid` — all from npm |
| **Credentials** | No environment variables, no secrets in code |

**Database:** Default location is `./openclaw-memory.db` (SQLite, local file).

**Known Limitations:**
- Memory content is passed to LLM prompts — users could inject instructions via stored memories
- Calls local Ollama at `localhost:11434` for embeddings — requires Ollama running

## Security Notes

1. ✅ **No external network** — MCP server uses stdio, not HTTP/TCP. Only calls `localhost:11434` for local Ollama embeddings.
2. ✅ **No authentication required** — Only accessible to the parent process
3. ✅ **Local-only database** — SQLite file, no remote connections
4. ✅ **No credentials needed** — Only requires local Ollama for embeddings
5. ✅ **No postinstall scripts** — Clean npm install
6. ⚠️ **Prompt injection risk** — Memory content is passed to LLM prompts. If users store malicious content, it could affect LLM behavior. This is inherent to all memory systems.

## Database Location

Default: `./openclaw-memory.db`

Custom path:
```typescript
const memory = new MemoryStore('/path/to/custom.db');
```

## Features

- **Hybrid Search** — BM25 + semantic (embedding) with reciprocal rank fusion
- **Entity Extraction** — Auto-extract people, orgs, projects, technologies
- **Spelling Variants** — UK↔US English expansion (colour/color, etc.)
- **Question-Type Aware** — Factual questions prioritize semantic memories
- **Entity Boost** — Memories with matching entities rank higher

## Benchmark

| System | LOCOMO Score |
|--------|--------------|
| **Muninn** | **93%** |
| Engram | 79.6% |
| Mem0 | 66.9% |

Muninn Phase 1.5 includes knowledge graph integration for temporal reasoning and contradiction detection.

## License

MIT — Free, open source, no restrictions.

---

🦜 *Built by KakāpōHiko (KH)*
