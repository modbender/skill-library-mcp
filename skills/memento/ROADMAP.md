# Memento — Roadmap & Ideas Tracker

## ✅ Done

### Core Plugin
- [x] Fact extraction from conversations (capture + extract pipeline)
- [x] SQLite storage with FTS5 full-text search
- [x] Visibility model: shared / private / secret (keyword + LLM classifier)
- [x] Duplicate detection & fact superseding with provenance chain
- [x] Auto-recall injection before each AI turn (`before_prompt_build` hook)
- [x] Per-agent memory + master KB aggregating "shared" facts
- [x] Provider-agnostic refactor (Anthropic, OpenAI, Mistral, Ollama, OpenAI-compatible)
- [x] Configurable extraction model (default: `anthropic/claude-sonnet-4-6`)
- [x] Temporal recency weighting in recall scoring
- [x] Category priority weights (decisions & corrections > routine)
- [x] Confidence scoring (0-1) with minimum threshold (0.6)

### ClawHub Publishing
- [x] Published as `memento@0.3.0` on ClawHub (@braibaud)
- [x] Renamed from Engram → Memento
- [x] Git history rewritten (no personal info leaks)
- [x] Removed credential snooping (no more reading auth-profiles.json)
- [x] TypeScript: zero errors

### Mission Control Tab
- [x] Dashboard with 6 hero stat cards, category bars, donut charts, growth timeline
- [x] Extraction pipeline health monitor
- [x] Top 10 most-reinforced facts
- [x] Recent 20 facts stream with category pills, visibility/agent badges
- [x] Expandable fact cards (full content, metadata, timestamps)
- [x] Feedback actions: 👍 Helpful, 👎 Not relevant, 🗑️ Remove, 💬 Correct
- [x] Toast notifications, inline confirmation for destructive actions
- [x] Auto-refresh every 60s, category click-to-filter

## ✅ Recently Completed (v0.4.0)

### ClawHub Trust Score — DONE
- [x] Honest messaging (no "Everything stays local"), recommends Ollama for local
- [x] Structured `optionalEnv` + `dataFiles` declarations in SKILL.md
- [x] `@anthropic-ai/sdk` removed from package-lock
- [x] `autoExtract: false` default (opt-in)
- [x] Migration docs: explicit filesystem access + security notes
- [x] Secret-filtering: expanded security comments for audit trail
- [x] Hardcoded paths removed from CLI → auto-discovery via os.homedir()
- [x] Published as `memento@0.4.0`

### Git / GitHub — DONE  
- [x] Git history rewritten (no personal info)
- [x] Pushed to `https://github.com/braibaud/Memento`

---

## 🔧 In Progress

### Side-Learning (Claude Code → Memento bridge)
- [x] Staging schema (v1 JSON format for fact exports)
- [x] Ingest pipeline: reads `~/.engram/staging/*.json`, validates, deduplicates, promotes to KB
- [x] `/memento-export` slash command installed at `~/.claude/commands/`
- [ ] **Automatic bridge** — scan `~/.claude/projects/**/*.jsonl`, extract facts via LLM, push to staging. Works regardless of macOS app vs CLI. No user action required.
- [ ] Cron job to run ingest pipeline periodically

### Knowledge Graph & Multi-Layer Memory
- [x] Schema v4: `fact_relations` table — typed weighted edges between facts
- [x] 6 relation types: related_to, elaborates, contradicts, supports, caused_by, part_of
- [x] Extraction prompt identifies relations to existing facts
- [x] Relations stored during deduplication pipeline
- [x] Recall enriched with 1-hop graph traversal (graph-sourced facts at 40% parent score)
- [x] Context builder shows graph-sourced facts with 🔗 provenance tag
- [x] Visibility filtering in graph traversal (shared < private < secret)
- [x] Schema v5: `fact_clusters` + `cluster_members` tables
- [x] Incremental consolidation after each extraction (no LLM, fast)
  - Assigns unclustered facts to existing clusters via graph edges
  - Creates new clusters from 3+ unclustered facts in same category
- [x] Deep consolidation ("sleep" pass)
  - Soft confidence decay: 0.5%/day after 30-day grace, floor 0.3
  - Clustered facts decay 50% slower, high-occurrence 30% slower
  - Cluster summary refresh from member facts
  - Cluster merging when Jaccard overlap > 60%
- [x] Deep consolidation runs at 3 AM via cron
- [ ] LLM-assisted semantic grouping in deep consolidation
- [ ] Layer 3+ meta-cluster creation
- [x] MC tab: Knowledge Graph visualization (force-directed SVG, cluster hulls, hover/click/drag, collapsible section)

## 📋 Planned — Next Up

### Interview / Onboarding Process
Structured conversation where an agent "interviews" the user to rapidly build a knowledge base. Solves the cold-start problem.
- Targeted questions across categories: identity, family, preferences, tools, work, home
- Facts from interviews start at lower confidence (~0.7)
- Confidence reinforced when facts confirmed in real conversations (natural trust-building)
- Track interview completion by category
- Trigger via CLI command or Telegram `/memento interview`
- **Priority: HIGH** — biggest UX impact for new users

### Value Measurement / Analytics
How do we know Memento is actually helping?
- **Recall precision**: % of injected facts that get 👍 vs 👎 (foundation already built with feedback buttons)
- **Question avoidance**: does the agent ask fewer clarifying questions over time?
- **User correction rate**: do "no, I told you..." messages decrease?
- **Fact staleness tracking**: how many recalled facts are thumbed down as outdated?
- **Feedback analytics panel** on MC tab (once enough data exists)
- Target: >80% recall precision = clearly adding value
- **Priority: MEDIUM** — needs data from feedback buttons first

### Fact Discussion / Conversational Correction (V3)
Full multi-turn conversation about a specific fact, beyond the current inline correction.
- Clicking "Discuss" opens a chat-like interface (or triggers a Telegram message)
- Agent can ask clarifying questions, propose corrections, negotiate final fact
- Could be embedded in MC tab or route to Telegram with fact pre-loaded as context
- Current V2 inline correction gets ~80% of the value
- **Priority: LOW** — V2 correction covers most use cases

## 💡 Ideas / Backlog

### Visibility Model Improvements
- Secret vs Private distinction is muddy — consider renaming "secret" → "sensitive"?
- Keyword classifier is too aggressive (e.g., "Ben prefers his medication in the morning" = preference, not medical secret)
- Consider user-configurable sensitivity rules

### Feedback Loop into Extraction
- Thumbs up/down patterns should feed back into extraction quality
- If certain categories consistently get thumbed down → tune extraction prompt
- If certain agents produce more low-quality facts → diagnostic signal
- Track feedback analytics per category and per agent

### Embedding Improvements
- [ ] BGE-M3 embedding backfill (blocked: needs `sudo apt install cmake`)
- Semantic search for recall (currently FTS5 keyword + recency)
- Embedding-based duplicate detection

### Data Migration
- [ ] Migrate all agents' `memory/*.md` files into Memento knowledge base (warm start)
- Migration script exists but hasn't been run on production data

### Packaging & Documentation
- [ ] Blog post covering architecture and design decisions
- [ ] Logo generation (blocked: OpenAI API key expired)
- [ ] Phase 5 final packaging review

### MC Tab Enhancements
- Feedback analytics panel (charts showing precision over time)
- Fact search/filter by content text
- Agent-specific views (filter by agent)
- Fact timeline view (chronological, not just "recent 20")
- Export facts as JSON/CSV

---
*Created: 2026-02-25 by Greg*
*Last updated: 2026-02-25 08:20*

## ✅ Recently Completed (v0.5.0)

### OpenClaw Model Routing Integration
- [x] Extraction now uses OpenClaw's `runEmbeddedPiAgent` instead of direct provider HTTP calls
- [x] Memento transparently inherits the agent's configured model (provider, fallbacks, auth)
- [x] No more standalone API key management in Memento — all delegated to OpenClaw
- [x] Graceful fallback to direct API if running outside OpenClaw (CLI mode)
- [x] New `src/extraction/embedded-runner.ts` module wraps the OpenClaw integration
- [x] `ExtractionTrigger` and `extractFacts()` updated to thread `api.config` through
- [x] README and docs updated to reflect model routing behaviour

## ✅ Recently Completed (v0.5.1)

### AMA-Agent Inspired Features — ALL DONE (from arxiv 2602.22769)

#### 1. Causality Edges in fact_relations — DONE
- [x] Added `precondition_of` edge type (alongside `caused_by`)
- [x] Extraction prompt instructs LLM to prefer causal types for cause-effect / prerequisite relationships
- [x] `causal_weight` column added to `fact_relations` (schema v7); set to `1.5` for causal edges
- [x] Graph traversal in `search.ts` applies **1.5× score boost** for `caused_by` / `precondition_of` edges vs. 0.4× for associative edges
- [x] `deduplicator.ts` stores `causal_weight` when persisting relation edges

#### 2. Query Planning Before Retrieval — DONE
- [x] `planQuery()` function in `search.ts` calls LLM to expand query with synonyms/entities/categories
- [x] `recall.autoQueryPlanning` config option (default: `false`, opt-in)
- [x] Graceful fallback: if planning fails or times out, falls back to raw FTS query
- [x] Uses OpenClaw model routing via `runViaOpenClaw`

#### 3. Temporal State Transitions — DONE
- [x] `previous_value` column added to `facts` table (schema v7)
- [x] `db.supersedeFact()` automatically captures old fact's content as `previous_value` on the new fact
- [x] `context-builder.ts` shows `_(previously: ...)_` in recall output for facts that have changed
- [x] `deduplicator.buildFactRow()` initialises `previous_value: null`; actual value set atomically in `supersedeFact`

### What was NOT implemented (by design)
Full trajectory-based reasoning from AMA-Bench — designed for agent-environment interactions (web nav, code editing), not personal assistant conversations. Memento's dialogue-centric approach is correct for this use case.

## ✅ Recently Completed (v0.5.2)

### Mission Control — Memento Tabs
- [x] `/memento` tab: Agent Memory view (current agent's facts, category bars, graph visualization)
- [x] `/memento/global` tab: Global Memory across all agents
- [x] `/memento/ingest` tab: Ingest pipeline management — approve/reject/extract projects
- [x] Old `/ingest` route redirects to `/memento/ingest`
- [x] Knowledge graph visualization: force-directed SVG, cluster hulls, tooltips, collapsible

### Bug Fix: trigger.ts openClawConfig
- [x] `trigger.ts` was passing `undefined` for `openClawConfig` to `extractFacts()` — silently broken since v0.5.0
- [x] Fixed: config now threaded correctly through `handleAfterResponse`

### Mission Control Extraction Pipeline
- [x] Direct Anthropic API call (Bearer OAuth) replaces broken `openclaw agent` CLI approach
- [x] `openclaw agent --agent main` deadlocks from inside main session (file lock) — bypassed
- [x] drjones treating extraction as heartbeat during quiet hours — bypassed
- [x] OAuth token requires `Authorization: Bearer` + `anthropic-beta: oauth-2025-04-20` header
- [x] `content_received_at` orphan bug fixed: reset timestamps for projects with 0 content files
- [x] Pending query robust against empty-content edge case
- [x] Mission Control now runs as systemd service (auto-restart, survives shell death)

### Warm-Start Ingestion
- [x] 93 Claude Code JSONL session files pushed from Mac Mini → Mission Control
- [x] 268 new facts extracted, 27 updated, 757 total active facts in Engram DB
- [x] memento-ingest CLI on Mac Mini patched: shows `⚠️ (folder deleted)` for missing project folders

---

## 🔍 Quality Analysis — 2026-03-01 Findings

### Problem: Memento stores too much, filters too little

After analyzing the live DB (1007 total facts, 533 active in `technical` category alone):

**Findings:**
1. **Confidence ≠ importance.** Almost everything scores 0.9+. A Feb-4 Drive folder upload has the same weight as Ben's family tree.
2. **`technical` is a dump category.** 533 active technical facts — meeting notes, transient statuses, one-off findings live alongside durable architectural decisions.
3. **Action items are never marked done.** 145 active action_items, many clearly stale: "gog CLI hanging since Feb 7", "Engram Phase 3/4/5 TODO" (already shipped), etc.
4. **All warm-start facts share the same timestamp (02-23)** — deduplication can't operate on them over time, no staleness signal.
5. **No durability filter.** The extraction prompt doesn't ask "would this matter in 6 months?" It asks "is this a fact?" — a much lower bar.

**Root cause:** The LLM extraction prompt is tuned for completeness, not curation. It's a journalist (capture everything), not a librarian (keep what matters).

---

## 📋 Planned — Next Up (revised priority)

### 🔴 HIGH: Fact Quality & Relevancy Improvements

#### 1. Stricter Extraction Prompt
- Add durability filter: "Would this fact still be relevant in 6 months?"
- Reject meeting notes, transient statuses, completed TODOs, session artifacts
- Require minimum information density: no facts that are just "X happened on date Y"
- Categories to be more selective: `technical` should only store architectural decisions, not implementation logs
- **Actionable test:** before storing, ask "would this help me answer a future question I can't predict?"

#### 2. TTL / Auto-Expiry for Action Items
- `action_item` facts that aren't reinforced within 30 days → auto-set `is_active=0`
- "DONE/COMPLETED/RESOLVED" prefix in summary → immediately deactivate
- Weekly consolidation pass: scan action_items older than 14 days, check if still valid via LLM
- This alone would eliminate ~50% of current noise

#### 3. Importance Score (separate from Confidence)
- Add `importance` field (1-5) alongside `confidence`
- Confidence = "how sure are we this is true" (current)
- Importance = "how useful will this be for future recall" (new)
- Scoring heuristics: person/family/preference facts → 4-5; architectural decisions → 4; meeting notes → 1-2; transient status → 1
- Recall injection: only facts with importance ≥ 3 unless query specifically relevant

#### 4. MC Bulk Curation UI
- "Review" mode in `/memento/ingest` or new `/memento/review` tab
- Shows facts sorted by (low importance × low reinforcement × age)
- Quick actions: Keep / Archive / Delete / Recategorize
- Batch archive: "archive all action_items older than 30 days"
- This gives Ben direct control without touching code

### 🟡 MEDIUM: Value Measurement / Analytics
*(unchanged from previous plan)*

### 🟡 MEDIUM: Interview / Onboarding Process  
*(unchanged from previous plan)*

### 🟢 LOW: Fact Discussion / Conversational Correction (V3)
*(unchanged from previous plan)*

---

## 💡 Ideas / Backlog (updated)

### Visibility Model Improvements
- Secret vs Private distinction is muddy — consider renaming "secret" → "sensitive"?
- Keyword classifier is too aggressive (e.g., medication timing = preference, not medical secret)
- Consider user-configurable sensitivity rules

### Feedback Loop into Extraction
- Thumbs up/down patterns should feed back into extraction quality
- If certain categories consistently get thumbed down → tune extraction prompt
- Track feedback per category and per agent

### Embedding Improvements
- [ ] BGE-M3 embedding backfill (blocked: needs `sudo apt install cmake`)
- Semantic search for recall (currently FTS5 keyword + recency)
- Embedding-based duplicate detection

### Data Migration
- [ ] Migrate all agents' `memory/*.md` files into Memento knowledge base (warm start)

### Packaging & Documentation
- [ ] Blog post covering architecture and design decisions
- [ ] Logo generation (blocked: OpenAI API key expired)

### MC Tab Enhancements
- Feedback analytics panel
- Fact search/filter by content text
- Agent-specific views
- Fact timeline view
- Export facts as JSON/CSV

---
*Last updated: 2026-03-01 by Greg*

---

## 🏗️ Architecture Redesign — 2026-03-01

### Decision: 3-Phase Extraction Pipeline

Based on analysis of current extraction quality issues, the pipeline is being redesigned into 3 cleanly separated phases:

#### Phase 1 — LLM Extraction (history-agnostic)
- **What**: Extract facts from the conversation segment only
- **What NOT**: No existing facts passed, no deduplication rules, no relation detection
- **Output**: Raw fact candidates (category, content, confidence, visibility)
- **Key rule**: "Would this fact still be relevant in 6 months?" — if no, skip
- **Prompt**: Moved to dedicated `.md` file (not embedded in code)
- **Status**: 🔲 TODO

#### Phase 2 — Embedding-Based Deduplication
- **What**: Embed each candidate fact, cosine similarity against DB
- **Dedup threshold**: ~0.92 cosine → mark as duplicate/supersede
- **Update threshold**: ~0.75–0.91 → merge/update existing fact
- **No LLM needed here at all**
- **Prerequisite**: All active facts must have embeddings
- **Status**: 🔲 TODO
- **Blocker**: 392/867 active facts currently missing embeddings → backfill needed

#### Phase 3 — Relation Linking (async, embedding-first)
- **What**: Dedicated background job linking facts to each other
- **Approach**: Embedding similarity across full DB → candidate pairs → typed edges
- **Not in the hot path**: Runs during consolidation (3 AM cron or similar)
- **LLM involvement**: Optional secondary pass to classify relation type on high-similarity pairs
- **Why not LLM-primary**: Would need full DB context; current windowed approach produces noisy edges
- **Status**: 🔲 TODO (design agreed, implementation pending)

### Other Decisions (2026-03-01)
- **Prompts in .md files**: All LLM prompts extracted from code to dedicated markdown files (editable without recompile)
- **Existing facts NOT passed to extractor**: Removes history dependency, reduces token cost, improves extraction quality
- **Embeddings are prerequisite for Phase 2**: Need backfill job for 392 facts missing embeddings
- **CUDA symlink confirmed**: `/usr/local/cuda-12.6/lib64/libcudart.so.12` → exists ✅
- **CUDA GPU status**: CUDA build present (`linux-x64-cuda` binaries exist), but no explicit `ggml_cuda_init` confirmation in logs — CPU fallback possible. Needs verification.
- **Embedding coverage**: 475/867 active facts have embeddings (55%) — insufficient for Phase 2

### Embedding Backfill — TODO
- Write a one-time backfill script: iterate facts WHERE `embedding IS NULL`, embed via bge-m3, store
- Run during off-peak (can be slow — 392 facts × ~50ms each ≈ ~20s)
- Required before Phase 2 deduplication is viable

---
*Architecture section added: 2026-03-01 by Greg*

---

## ✅ Recently Completed (v0.6.0 — Pipeline Redesign)

### Phase 1: History-Agnostic Extraction — DONE
- [x] `prompts/extraction.md` — new extraction prompt with durability filter ("would this matter in 6 months?")
- [x] Explicit anti-patterns: meeting notes, transient status, completed TODOs, implementation details
- [x] Tighter category guidance for `technical` (architectural facts only) and `action_item` (open + urgent only)
- [x] Prompt loaded from file at runtime — editable without recompile
- [x] `extractor.ts`: existing facts NO LONGER passed to LLM (removed `{{existing_facts}}` placeholder)
- [x] `_existingFacts` param kept for API compat but prefixed `_` (unused)

### Phase 2: Embedding-Based Deduplication — DONE
- [x] `deduplicator.ts` fully rewritten — LLM hints (`duplicate_of`, `supersedes`) no longer used
- [x] Cosine similarity against existing embedded facts:
  - `>= 0.97` → duplicate (increment occurrence_count)
  - `>= 0.82` → update/supersede (old fact deactivated, new inserted)
  - `< 0.82`  → new fact
- [x] Same-category comparison (avoids cross-category false positives)
- [x] New facts embedded immediately after insertion (no async backfill needed going forward)
- [x] `processExtractedFacts` now `async` — all call sites updated
- [x] `EmbeddingEngine` now passed to `ExtractionTrigger` and forwarded to deduplicator
- [x] Batch/CLI call sites (`migrate.ts`, `ingest.ts`, `process-raw-sessions.ts`) pass `null` gracefully (fall back to new-fact insertion)

### Embedding Backfill — DONE
- [x] `backfill-embeddings.ts` script — ran successfully
- [x] 392 missing embeddings generated; 870/870 active facts now have embeddings (100% coverage)
- [x] CPU mode (CUDA init fails: driver version insufficient for runtime version — node-llama-cpp CUDA issue)

### Dedup Sweep — DONE
- [x] `dedup-sweep.ts` — pairwise cosine similarity sweep across all embedded facts
- [x] 1 auto-merged (sim=0.98), 26 flagged for review (0.88–0.97)
- [x] DB confirmed clean at near-exact level; noise is breadth, not duplicates

---

## 🔲 Phase 3: Relation Linking (Next)

### Design (agreed 2026-03-01)
- Dedicated background job (runs at 3AM or on demand, not in hot path)
- Input: all active facts with embeddings
- Step 1: Find candidate pairs via embedding similarity (threshold ~0.75 — lower than dedup)
- Step 2: For high-similarity cross-category pairs → assign `related_to` edge
- Step 3: Optional LLM pass on top-N pairs to classify specific relation type (caused_by, part_of, etc.)
- Step 4: Store edges in `fact_relations` table with `created_by: "relation-sweep"`
- Avoids re-processing already-linked pairs (track via `metadata` or separate log)

### Status: ✅ DONE (v0.6.0)

Implemented:
- `src/consolidation/relation-sweep.ts`: full background job (pairwise cosine, 3 tiers, Haiku batch)
- `prompts/relation-classify.md`: structured Haiku prompt (6 relation types, rationale field)
- `db.ts`: `getAllRelations()` + `getDistinctAgentIds()` helpers
- Mission Control: `POST /api/memento/relation-sweep` endpoint + UI button on Memento page
- Secret facts excluded from all sweep operations

