# OpenClaw Local Supermemory Plugin

## Overview
A fully local, privacy-first persistent memory system for OpenClaw agents. No cloud dependencies, no subscriptions. All data stays on the machine.

This is designed as an **official OpenClaw plugin** from day one.

## Architecture

### Four Layers

```
┌─────────────────────────────────────────────────┐
│ CAPTURE LAYER (Hooks: message events)           │
│ • Buffers all messages per conversation          │
│ • Detects conversation pauses / topic shifts    │
│ • Triggers extraction when segment is complete  │
│ • Multi-turn aware (sliding window, not single) │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ EXTRACTION LAYER (Configurable LLM - Sonnet)    │
│ • Receives full conversation segment            │
│ • Extracts: preferences, decisions, facts,      │
│   action items, people info, corrections        │
│ • Deduplicates against existing knowledge       │
│ • Detects fact UPDATES (not just additions)     │
│ • Flags recurring topics (temporal signal)      │
│ • Assigns visibility: private/shared/secret     │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ STORAGE LAYER (SQLite + embeddings)             │
│ • Structured facts with categories, timestamps  │
│ • Occurrence tracking (when/how often mentioned)│
│ • Embeddings for semantic search                │
│ • Visibility levels (private/shared/secret)     │
│ • memory/*.md files (human-readable journal)    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│ RECALL LAYER (before each AI turn)              │
│ • Semantic search over knowledge base           │
│ • Injects relevant facts as context             │
│ • Temporal awareness ("discussed on Jan 29th")  │
│ • Pattern detection (recurring = important)     │
└─────────────────────────────────────────────────┘
```

### Multi-Agent Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│   main   │  │ drjones  │  │   bob    │  │  frank   │
│ (main)   │  │(drjones) │  │  (bob)   │  │ (frank)  │
│ memory   │  │ memory   │  │ memory   │  │ memory   │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └─────────────┴──────┬──────┴─────────────┘
                          │
                   ┌──────▼──────┐
                   │   MASTER    │
                   │ KNOWLEDGE   │
                   │   BASE      │
                   └─────────────┘
```

Each agent searches: own memory → master KB. Never other agents' private stores.

### Visibility Levels
- **`private`** — stays in agent's own store (default for operational details)
- **`shared`** — propagates to master KB (user preferences, family, home setup)
- **`secret`** — never propagated, potentially encrypted (credentials, medical, financial)

### Temporal Pattern Detection
When a topic recurs, track:
- **What**: the fact/topic
- **When**: timestamps of each occurrence
- **Why**: context of each mention (was it a reminder? frustration? update?)
- **Frequency**: occurrence count → importance weight

Recurring topics = core values/unresolved issues. Not just duplicates to squash.

## Phase Plan

### Phase 1: Conversation Capture (THIS PHASE)
- OpenClaw plugin structure (`openclaw.plugin.json`, `package.json`)
- Hook on `message:received` + `message:sent` events
- Buffer conversations per session in memory
- Write raw conversation segments to append-only log files
- Detect conversation pauses (configurable timeout, default 5 min)
- Detect topic shifts (heuristic: long gap or explicit topic change)
- When segment completes, write to `<workspace>/memory/conversations/YYYY-MM-DD-HH-MM-slug.jsonl`
- SQLite schema for conversation segments (metadata, timestamps, session info)

### Phase 2: Extraction + Knowledge Base
- Sonnet extraction of structured facts from conversation segments
- SQLite knowledge base with categories, embeddings, visibility levels
- Occurrence tracking (temporal dimension)
- Deduplication with "recurring topic" detection
- Initial migration: ingest existing memory/*.md files

### Phase 3: Auto-Recall
- Hook on `before_agent_start` (or equivalent) to inject relevant facts
- Semantic search over knowledge base
- Temporal context injection ("you discussed this on...")
- Pattern-aware recall (recurring topics get priority)

### Phase 4: Master Knowledge Base
- Cross-agent fact sharing (respecting visibility)
- Conflict resolution (latest wins, with provenance)
- Master KB aggregation/merge logic

### Phase 5: Package & Publish
- Full test suite
- Documentation
- npm package
- ClawHub listing

## Technical Details

### Plugin Structure
```
openclaw-memento-local/
├── package.json                    # npm package with openclaw.extensions
├── openclaw.plugin.json            # Plugin manifest + config schema
├── src/
│   ├── index.ts                    # Plugin entry point (register hooks + tools)
│   ├── hooks/
│   │   ├── capture.ts              # message:received + message:sent handler
│   │   └── recall.ts               # before_agent_start handler (Phase 3)
│   ├── capture/
│   │   ├── buffer.ts               # In-memory conversation buffer
│   │   ├── segmenter.ts            # Topic shift / pause detection
│   │   └── writer.ts               # Write segments to disk + SQLite
│   ├── extraction/                 # Phase 2
│   │   ├── extractor.ts            # LLM-based fact extraction
│   │   ├── deduplicator.ts         # Fact deduplication + recurrence detection
│   │   └── classifier.ts           # Visibility level assignment
│   ├── storage/
│   │   ├── schema.ts               # SQLite schema definitions
│   │   ├── db.ts                   # Database operations
│   │   └── embeddings.ts           # Local embedding generation
│   ├── recall/                     # Phase 3
│   │   ├── search.ts               # Semantic search
│   │   └── context-builder.ts      # Build injection context
│   └── config.ts                   # Configuration types + defaults
├── HOOK.md                         # Hook metadata (for hook discovery)
└── README.md
```

### Configuration (in openclaw.json)
```json
{
  "plugins": {
    "entries": {
      "memento-local": {
        "enabled": true,
        "config": {
          "extractionModel": "anthropic/claude-sonnet-4-6",
          "embeddingModel": "hf:BAAI/bge-m3-gguf",
          "pauseTimeoutMs": 300000,
          "maxBufferTurns": 50,
          "autoCapture": true,
          "autoRecall": true,
          "visibility": {
            "defaultLevel": "shared",
            "rules": {
              "medical": "secret",
              "credentials": "secret",
              "operational": "private"
            }
          }
        }
      }
    }
  }
}
```

### SQLite Schema (Phase 1 - Conversations)
```sql
-- Conversation segments (raw capture)
CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  session_key TEXT NOT NULL,
  channel TEXT,
  started_at INTEGER NOT NULL,
  ended_at INTEGER NOT NULL,
  turn_count INTEGER NOT NULL,
  raw_text TEXT NOT NULL,
  metadata TEXT -- JSON
);

-- Individual messages within segments
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL REFERENCES conversations(id),
  role TEXT NOT NULL, -- 'user' or 'assistant'
  content TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  message_id TEXT, -- provider message ID
  metadata TEXT -- JSON
);
```

### SQLite Schema (Phase 2 - Knowledge Base)
```sql
-- Extracted facts
CREATE TABLE facts (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  category TEXT NOT NULL, -- preference, decision, person, action_item, etc.
  content TEXT NOT NULL,
  summary TEXT, -- one-line summary
  visibility TEXT NOT NULL DEFAULT 'shared', -- private, shared, secret
  confidence REAL DEFAULT 1.0,
  first_seen_at INTEGER NOT NULL,
  last_seen_at INTEGER NOT NULL,
  occurrence_count INTEGER DEFAULT 1,
  embedding TEXT, -- vector embedding
  supersedes TEXT, -- ID of fact this updates/replaces
  metadata TEXT -- JSON (extra context)
);

-- Fact occurrences (temporal tracking)
CREATE TABLE fact_occurrences (
  id TEXT PRIMARY KEY,
  fact_id TEXT NOT NULL REFERENCES facts(id),
  conversation_id TEXT NOT NULL REFERENCES conversations(id),
  timestamp INTEGER NOT NULL,
  context_snippet TEXT, -- what was said around this mention
  sentiment TEXT -- neutral, frustration, confirmation, correction, etc.
);

-- Master knowledge base (Phase 4)
CREATE TABLE master_facts (
  id TEXT PRIMARY KEY,
  source_agent_id TEXT NOT NULL,
  source_fact_id TEXT NOT NULL,
  -- same columns as facts, minus private ones
  category TEXT NOT NULL,
  content TEXT NOT NULL,
  summary TEXT,
  confidence REAL DEFAULT 1.0,
  first_seen_at INTEGER NOT NULL,
  last_seen_at INTEGER NOT NULL,
  occurrence_count INTEGER DEFAULT 1,
  embedding TEXT,
  metadata TEXT
);
```

## Embedding Model
- **Target**: BGE-M3 (GGUF format)
- **Dimensions**: 1024
- **Why**: Multilingual (EN/FR), state of the art, fits easily in 16GB VRAM
- **Runtime**: GPU-accelerated via node-llama-cpp or llama.cpp server

## Extraction Prompt Design (Phase 2)
The extraction prompt should:
1. Receive the full conversation segment (multi-turn)
2. Extract structured facts with categories
3. Check against existing facts (provided as context) for deduplication
4. Flag updates to existing facts (e.g., "FTP changed from 250W to 260W")
5. Detect recurring topics and assign importance
6. Assign visibility levels based on content category
7. Return structured JSON output

## Key Design Principles
1. **Privacy first** — all data local, no external calls except LLM API
2. **Plugin-ready** — proper OpenClaw plugin from day one
3. **Multi-turn aware** — capture conversation arcs, not single exchanges
4. **Temporal intelligence** — track when and how often topics arise
5. **Configurable** — model, thresholds, visibility rules all configurable
6. **Graceful degradation** — if extraction fails, raw capture still works
7. **Human-readable** — all data inspectable in files + SQLite
