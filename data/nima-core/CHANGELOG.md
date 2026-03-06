# Changelog

All notable changes to NIMA Core will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2026-02-26

### Fixed
- **CRITICAL: LadybugDB SIGSEGV on SET/CREATE/DELETE** — Root cause identified: `LOAD VECTOR` extension must be called before any mutation on tables with `FLOAT[512]` columns (like MemoryNode). Without it, Kùzu crashes with SIGSEGV. Added `LOAD VECTOR` calls to: `memory_pruner.py`, `lucid_moments.py`, `dream_db_sync.py`, and all LadybugDB connection helpers.

### Added
- **`nima_core/dream_db_sync.py`** — New module that syncs dream consolidation outputs (insights, patterns, dream runs, narratives) from JSON files to both SQLite and LadybugDB. Called automatically after dream consolidation and pruning.
- **Ghost-marking pipeline** — Memory pruner now syncs suppression registry → LadybugDB ghost marks after each pruning run. Batched in groups of 200 IDs.
- **SQLite dual-write in `ladybug_store.py`** — Every memory stored to LadybugDB is also written to SQLite with optional Voyage embedding for semantic search (requires `VOYAGE_API_KEY` env var).
- **Dream system SQLite tables** in `scripts/init_db.py`:
  - `nima_insights` — Dream-generated insights with confidence scores
  - `nima_patterns` — Cross-domain recurring patterns
  - `nima_dream_runs` — Dream consolidation run history
  - `nima_suppressed_memories` — Pruned memory records
  - `nima_pruner_runs` — Pruner execution log
  - `nima_lucid_moments` — Surfaced memory moments

### Changed
- **`dream_consolidation.py`** — Now calls `dream_db_sync.sync_all()` after each consolidation run to persist results to both databases.
- **`memory_pruner.py`** — After pruning, syncs ghost marks to LadybugDB via `dream_db_sync.sync_pruner_to_ladybug()`.

## [3.0.8] - 2026-02-24

### Added
- **Security section in SKILL.md** — Comprehensive security documentation covering:
  - What gets installed and where
  - Credential handling table (which env vars make network calls)
  - Safety features (input filtering, injection prevention, timeouts)
  - Best practices (review before install, don't run as root, use containers)
  - Data location reference
- **`.nimaignore` file** — Specification for excluding content from memory capture
  - Supports glob patterns (like .gitignore)
  - Defines filters for system messages, heartbeats, passwords/secrets
  - Note: Pattern matching implementation in hook is pending
- **`scripts/init_db.py`** — Extracted database initialization from install.sh
  - Standalone script with argparse
  - Verbose mode for debugging
  - Proper error handling

### Changed
- **`install.sh` refactored** — Cleaner, more verbose output
  - Uses `scripts/init_db.py` instead of inline Python
  - Shows each step clearly
  - Data directory configurable via `NIMA_DATA_DIR`

### Security
- **Transparency** — All install actions logged, no hidden operations
- **Defense in depth** — Multiple layers of input filtering
- **Minimal permissions** — No root required, user home only

## [3.0.7] - 2026-02-23

## [3.0.6] - 2026-02-23

### Fixed
- **CRITICAL:** SyntaxError in lucid_moments.py line 447 — unterminated f-string with literal newline, preventing NIMA from loading

## [3.0.5] - 2026-02-23

### Changed
- SKILL.md: remove internal post-mortem language, fix NIMA_DATA_DIR example (~/.nima/memory → ~/.nima), update changelog to v3.0.4, add Darwinian Memory + Installer to module table

## [3.0.4] - 2026-02-23

### Fixed
- **Version alignment:** Synced `__init__.py`, `README.md` badge, and all three OpenClaw hook `package.json` files to match canonical `setup.py` version `3.0.4`
- **nima-affect missing package.json:** Added `package.json` to `openclaw_hooks/nima-affect/` — consistent with `nima-memory` and `nima-recall-live` hook format
- Hook versions were scattered across `2.0.2`, `2.0.3`, `2.0.11` — all unified to `3.0.4`

## [3.0.3] - 2026-02-22

### Changed
- Minor internal refinements post `3.0.2` publish
- `setup.py` bumped to `3.0.3` → `3.0.4` for subsequent release

## [3.0.2] - 2026-02-22

### Fixed
- **CRITICAL:** ClawHub package was missing entire `nima_core/cognition/` directory (10 files) due to `.clawhubignore` glob pattern bug — `*` excluded subdirectory contents even when parent was re-included
- **CRITICAL:** All OpenClaw hook files missing from package (`openclaw_hooks/nima-memory/*.py`, `openclaw_hooks/nima-recall-live/*.py`, `openclaw_hooks/nima-affect/*`) — same `.clawhubignore` root cause
- Fixed `.clawhubignore` to use `!dir/**` pattern for recursive re-inclusion

### Changed
- README.md fully rewritten — consolidated all features (v2.0–v3.0), added package contents tree, simplified configuration docs, removed outdated sections
- Version badges updated to 3.0.2

## [3.0.0] - 2026-02-22

### Changed
- Version alignment across all modules to 3.0.0
- Package audit and dependency cleanup
- SKILL.md version bump

### Known Issues
- Package published to ClawHub was incomplete (fixed in 3.0.2)

## [2.5.0] - 2026-02-21

### Added
- **Hive Mind** (`nima_core/hive_mind.py`) — Proposal #7: Memory Entanglement.
  - `HiveMind` class: inject shared memory context into sub-agent prompts + capture results back to LadybugDB.
  - `HiveBus` class: Redis pub/sub message bus for real-time agent-to-agent communication. Channels: `hive` (broadcast), `role:{role}`, `agent:{id}`, `results:{swarm_id}`.
  - Optional: requires `redis-py` (`pip install nima-core[hive]`).
- **Precognition** (`nima_core/precognition.py`) — Proposal #4: Precognitive Memory Injection.
  - `NimaPrecognition` class: mine temporal patterns from LadybugDB, generate predictions via any OpenAI-compatible LLM, inject relevant precognitions into agent prompts.
  - Configurable: `db_path`, `llm_base_url`, `llm_model`, `voyage_api_key`, `lookback_days`.
  - Full cycle: `run_mining_cycle()` → `mine_patterns()` → `generate_precognitions()` → `store_precognitions()`.
  - Semantic dedup via SHA-256 pattern hashing; optional Voyage embeddings.
- **Lucid Moments** (`nima_core/lucid_moments.py`) — Proposal #8: Spontaneous Memory Surfacing.
  - `LucidMoments` class: surface emotionally-resonant memories unbidden via any delivery callback.
  - Scoring: age window (3–30 days), layer bonus, content richness, warm keywords.
  - Safety: trauma keyword filter, quiet hours, min gap, daily cap.
  - Enrichment: LLM transforms raw memories into natural "this just came to me" messages.
  - Fully configurable: quiet hours, `min_gap_hours`, `max_per_day`, `warm_keywords`, `persona_prompt`.

### Changed
- `setup.py`: version 2.4.0 → 2.5.0, added `[hive]` extra for `redis>=4.0.0`.
- `__init__.py`: lazy-imports for all three new modules (graceful if LadybugDB/redis unavailable).

## [2.4.0] - 2026-02-20

### Added
- **Dream Consolidation** (`nima_core/dream_consolidation.py`) — nightly memory synthesis engine.
  - Extracts `Insight` and `Pattern` objects from episodic memories via LLM.
  - VSA-style `blend_dream_vector` for semantic compression.
  - `DreamConsolidator` class with configurable LLM endpoint, lookback window, temperature.
  - `nima-dream` CLI entry point for scripted/cron usage.
- **Dream session state** — `DreamSession` dataclass tracks what was consolidated.

## [2.3.0] - 2026-02-19

### Added
- **Memory Pruner** (`nima_core/memory_pruner.py`) — Episodic distillation engine. Distills old conversation turns into semantic gists via LLM, suppresses raw noise in 30-day limbo. Configurable: `NIMA_DISTILL_MODEL`, `NIMA_DB_PATH`, `NIMA_DATA_DIR`, `NIMA_CAPTURE_CLI`. Pure stdlib (no `anthropic` package needed).
- **Logging** (`nima_core/logging_config.py`) — Singleton logger with file + console handlers. `NIMA_LOG_LEVEL` env var.
- **Metrics** (`nima_core/metrics.py`) — Thread-safe counters, timings, gauges. `Timer` context manager. Tagged metric support.
- **Connection Pool** (`nima_core/connection_pool.py`) — SQLite connection pool with WAL mode, max 5 connections, thread-safe.
- **Ollama embedding support** — `NIMA_EMBEDDER=ollama` with `NIMA_OLLAMA_MODEL` configuration.

### Fixed
- `__init__.py` — `__all__` NameError (used before definition)
- Memory pruner — Cypher injection prevention via layer whitelist
- Connection pool — Thread-safe `_waiters` counter, no double-decrement
- Logging — Correct log directory path (`NIMA_DATA_DIR/logs`, not parent)
- Metrics — Tagged metrics no longer overwrite each other in `get_summary()`

### Changed
- Version bump: 2.2.0 → 2.3.0
- Python requirement: 3.8+ (was 3.11+)
- All hardcoded paths replaced with env vars for portability

## [2.2.0] - 2026-02-19

### Added
- **VADER Affect Analyzer** — Contextual sentiment replacing lexicon-based detection
- **4-Phase Noise Remediation** — Empty validation → heartbeat filter → dedup → metrics
- **Resilient hook wrappers** — Auto-retry with exponential backoff and jitter
- **Ecology scoring** — Memory strength, decay, recency, surprise, dismissal in recall
- **Suppression registry** — File-based memory suppression with 30-day limbo

### Fixed
- Null contemplation layer crash
- Duplicate VADER/emotion lexicon keys
- Negation logic (proper 2-word window)
- Hardcoded venv paths → dynamic `os.homedir()`
- `--who` CLI filter (was a no-op)
- `maxRetries` clamped ≥ 1 in resilient wrapper
- Debug logging gated behind `NIMA_DEBUG_RECALL`
- Division by zero in cleanup script
- Ruff E701 lint issues

### Changed
- Recall token budget: 500 → 3000
- Shebang: hardcoded path → `#!/usr/bin/env python3`
- Turn IDs: full millisecond timestamps

## [2.1.0] - 2026-02-17

### Added
- Pre-release of VADER and noise remediation (shipped in v2.2.0)

## [2.0.3] - 2026-02-15

### Security
- Fixed path traversal vulnerability in affect_history.py (CRITICAL)
- Fixed temp file resource leaks in 3 files (HIGH)

### Fixed
- Corrected non-existent `json.JSONEncodeError` → `TypeError`/`ValueError`
- Improved exception handling — replaced 5 generic catches with specific types

### Improved
- Better error visibility and debugging throughout

## [2.0.1] - 2026-02-14

### Fixed
- Thread-safe singleton with double-checked locking

### Security
- Clarified metadata requirements (Node.js, env vars)
- Added security disclosure for API key usage

## [2.0.0] - 2026-02-13

### Added
- **LadybugDB backend** with HNSW vector search (18ms query time)
- **Native graph traversal** with Cypher queries
- **nima-query CLI** for unified database queries
- SQL/FTS5 injection prevention
- Path traversal protection
- Temp file cleanup
- API timeouts (Voyage 30s, LadybugDB 10s)
- 348 unit tests with full coverage

### Performance
- 3.4x faster text search (9ms vs 31ms)
- 44% smaller database (50MB vs 91MB)
- 6x smaller context tokens (~30 vs ~180)

### Fixed
- Thread-safe singleton initialization

## [1.2.1] - 2026-02-10

### Added
- 8 consciousness systems (Φ, Global Workspace, self-awareness)
- Sparse Block VSA memory
- ConsciousnessCore unified interface

## [1.2.0] - 2026-02-08

### Added
- 4 Layer-2 composite affect engines
- Async affective processing
- Voyage AI embedding support

## [1.1.9] - 2026-02-05

### Fixed
- nima-recall hook spawning new Python process every bootstrap
- Performance: ~50-250x faster hook recall

---

## Release Notes Format

Each release includes:
- **Added** — New features
- **Changed** — Changes to existing functionality
- **Deprecated** — Soon-to-be removed features
- **Removed** — Removed features
- **Fixed** — Bug fixes
- **Security** — Security improvements
