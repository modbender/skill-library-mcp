# Changelog

## v5.0.0 (2026-02-17)

**Breaking changes: Complete modularization and generification**

- **Modularized architecture** — Split 1309-line monolith into 8 focused library modules:
  - `lib/sqlite.js` — Database operations (query, exec, migrations)
  - `lib/entities.js` — Entity validation and allowlist management
  - `lib/extraction.js` — Fact extraction regex and text parsing
  - `lib/capture.js` — Auto-capture from messages
  - `lib/recall.js` — Memory retrieval and context injection
  - `lib/embeddings.js` — Ollama integration and vector operations
  - `lib/consolidation.js` — Deduplication and memory compaction
  - `lib/stuck-detection.js` — Topic tracking and Reflexion nudging

- **Entity allowlist generification** — Removed hardcoded personal names
  - Replaced with config-driven `entities` array in `openclaw.json`
  - Added runtime `memory_add_entity(name)` tool for dynamic entity addition
  - Default entities now: `config`, `system`, `note`, `project`
  - PascalCase multi-word names (e.g., `TradingSystem`) still auto-accepted

- **SQL sanitization** — Centralized `escapeSqlValue()` replacing 23 manual escape sites
  - Reduces injection risk
  - Single source of truth for SQL value escaping
  - Applied consistently across all database operations

- **Portable test suite** — Comprehensive testing infrastructure
  - Temp SQLite databases (auto-cleanup)
  - Mocked Ollama responses
  - Node.js `node:test` runner (no external test framework)
  - 120+ tests covering all modules
  - Edge case coverage for entity validation, extraction, consolidation

- **Removed all personal name references** — Kevin, Lily, Christine, Rose no longer hardcoded
  - Documentation updated to use generic examples
  - Operator/agent identity is now configurable, not baked in

- **Config-derived paths** — Topic history path now derives from `dbPath` directory
  - If `dbPath` is `~/.openclaw/memory/decisions.db`, topic history is `~/.openclaw/memory/topic-history.json`
  - Makes database location configurable without hardcoded paths
  - Simplifies multi-instance setups

- **New config options**:
  - `entities` (array) — Additional entity names to recognize
  - `topicHistoryPath` (implicit) — Derived from `dbPath` directory

## v4.0.0 (2026-02-16)

**Intelligence layer — vector search and stuck-detection**

- **Ollama vector search** — Semantic similarity alongside keyword matching
  - Model: `nomic-embed-text` (768 dimensions, 274MB)
  - Storage: JSON-encoded vectors in SQLite `vectors` table
  - Similarity: cosine similarity computed in JavaScript
  - Recall: FTS5 runs first (instant), vectors run async (~100ms), results merged and deduplicated
  - Capture: new facts embedded asynchronously (fire-and-forget)
  - Backfill: existing entries embedded on first startup with vectors enabled
  - Graceful degradation: silent fallback to keyword-only if Ollama unavailable

- **Reflexion-enhanced stuck-detection** — Topic analysis + memory-suggested alternatives
  - Detects when agent repeats same topics (>60% Jaccard similarity over 3+ consecutive turns)
  - Builds nudge using Reflexion pattern: "You've discussed these topics: X, Y, Z. Consider: A, B, C instead."
  - Queries database for unexplored fact areas
  - More actionable than generic "stop repeating yourself"

- **Memory consolidation** — Dedup + importance boost on startup
  - Finds duplicate (entity, fact_key) groups
  - Keeps latest row, deletes older duplicates
  - Boosts importance of survivor (+0.05, capped at 0.95)
  - Cleans orphaned vectors
  - Idempotent, millisecond-scale for ~100 entries

- **54 tests passing** — Up from 41 in v3
  - Vector similarity tests (mocked Ollama)
  - Consolidation tests (dedup verification)
  - End-to-end recall flow with vectors

## v3.0.0 (2026-02-16)

**Quality overhaul — killed the noise factory**

- **Entity allowlist** — Strict validation replacing permissive regex
  - Accepts: known entity names, system keywords (`config`, `system`, `note`), PascalCase multi-word names
  - Rejects: single lowercase words, common English words (`still`, `just`, `acts`, `you`, etc.)
  - 23 test cases validating edge cases

- **Killed Qwen3 classifier** — Removed broken auto-classification layer
  - Previous: every entry marked "ARCHIVE", filter did nothing
  - Now: heuristic TTL assignment based on source (manual, user-stated, auto-capture)
  - No model calls, no latency, correct by construction

- **Tightened auto-capture** — Aggressive noise filtering
  - Minimum value length: 2 → 15 characters
  - Reject values containing `?`, `()`, `""`, `<>`
  - Expanded noise blocklist
  - Result: 0% garbage entries in live testing (up from 85% noise in v2)

- **Compaction hooks** — Two new hooks to react to context compression
  - `before_compaction`: touch permanent memories so they don't age out of recall
  - `after_compaction`: reset topic history (conversation starts fresh after context reset)

- **Stuck-detection** — Prevent topic loops
  - Extract top 5 content words (excluding stopwords) per response
  - Compare signatures with Jaccard similarity
  - If 3+ consecutive >60% overlap: inject nudge
  - Topic history persists within session, clears on compaction

- **41/41 tests passing** — Auto-capture quality validated
  - Zero garbage entities created
  - Entity allowlist tested comprehensively
  - Stuck-detection Jaccard calculation verified

## v2.0.0 (2026-02-14)

**Initial JavaScript plugin — barely working**

- SQLite FTS5 keyword search
- Basic auto-capture from LLM responses
- Basic auto-recall injection before turns
- Quality score: 4.3/10
  - 85% auto-capture noise (fragments like "Still", "Just", "Acts")
  - Broken Qwen3 classifier (100% ARCHIVE marking)
  - Zero vector embeddings (LanceDB bridge never built)
  - No compaction awareness (permanent facts age out)
  - No stuck-detection (agent loops freely)

## Pre-v2: Python Controller (2026-02-14)

**Architectural approach, never integrated**

- 850-line Python memory controller
- SQLite for structured decisions
- LanceDB for semantic vectors
- Qwen3 30B for classification
- Async background worker thread
- Comprehensive error handling

Never integrated with OpenClaw gateway (Node.js). Plugin slot filled by existing JS plugin instead. Code preserved in `~/claude/lily-memory-system/` for reference.
