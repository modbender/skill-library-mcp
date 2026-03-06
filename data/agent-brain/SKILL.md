---
name: agent-brain
description: "Local-first persistent memory for AI agents with SQLite storage, orchestrated retrieve/extract loops, hybrid retrieval, contradiction checks, correction learning, and optional SuperMemory mirroring."
homepage: https://github.com/alexdobri/agent-brain
metadata:
  openclaw:
    emoji: 🧠
    disable-model-invocation: false
    user-invocable: true
---

# Agent Brain 🧠

**Teach your AI once. It remembers forever. It gets smarter over time.**

Agent Brain is a modular memory system for AI agents with continuous learning. It stores facts, catches contradictions, learns your habits, ingests external knowledge, tracks what works, learns from mistakes, and adapts to your tone — all in a local SQLite database with real persistence, full-text search, and pluggable storage backends.

### Why this exists

Every AI conversation starts from zero. You repeat yourself. It forgets what you taught it. Agent Brain fixes that with a working persistence layer (`scripts/memory.sh`) and six cognitive modules that the agent selectively invokes based on what the task actually needs.

### What makes this different

- **Production-grade storage.** SQLite with WAL mode and indexed queries. Handles 10,000+ entries without breaking a sweat. JSON backend available as fallback.
- **Pluggable backends.** Storage abstraction layer means you can swap SQLite for Postgres, Supabase, or any other backend — the command interface stays the same.
- **Continuous learning.** Corrections track what was wrong, what's right, and why. Successes reinforce what works. Anti-patterns emerge from repeated mistakes.
- **Selective dispatch, not a linear pipeline.** The orchestrator picks the 1-3 modules relevant to each task. Storing a fact doesn't need Vibe. Reading tone doesn't need Archive.
- **Active fact extraction.** The agent scans every message for storable information — identity, tech stack, preferences, workflows, project context — without being asked.
- **Honest confidence.** No fake 0.0-1.0 scores. Four categories (SURE / LIKELY / UNCERTAIN / UNKNOWN) derived from actual metadata — source type, access count, age.
- **Hybrid retrieval.** Results ranked with lexical + semantic scoring (`--policy fast|balanced|deep`) and optional score explainability (`--explain`).
- **Supersede, don't delete.** Old facts aren't destroyed. They're marked `superseded_by` with a pointer to the replacement, preserving full history.
- **Decay is mechanical.** Entries scale their decay threshold by access count. Heavily-used knowledge persists longer. Unused knowledge fades.

## Architecture

Six modules, one orchestrator, pluggable storage.

```
          ┌──────────────────────────────┐
          │       🧠 ORCHESTRATOR        │
          │   Dispatches by task type    │
          └──────────┬───────────────────┘
                     │
        ┌────────────┼────────────────────┐
        │ Which modules does this need?   │
        └────────────┼────────────────────┘
                     │
   ┌─────────┬───────┼───────┬──────────┬──────────┐
   ▼         ▼       ▼       ▼          ▼          ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ARCHIVE│ │GAUGE │ │INGEST│ │SIGNAL│ │RITUAL│ │ VIBE │
│  📦  │ │  📊  │ │  📥  │ │  ⚡  │ │  🔄  │ │  🎭  │
│Store │ │Conf. │ │Learn │ │Check │ │Habits│ │ Tone │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
   └─────────┴───────┴────┬───┴────────┴─────────┘
                          ▼
                ┌──────────────────┐
                │  💾 memory.db    │
                │  SQLite (default)│
                │  or memory.json  │
                └──────────────────┘
```

## How It Works

### Per-Message Flow

On EVERY user message, the agent runs this sequence:

**Step 1: RETRIEVE** — Before doing anything, search memory for context relevant to this message.

Extract 2-4 key topic words from the user's message and search:

```bash
./scripts/memory.sh get "<topic words>" --policy balanced
```

How to pick search terms:

| User says | Search query | Why |
|-----------|-------------|-----|
| "Help me set up the API endpoint" | `"api endpoint setup"` | Core task nouns |
| "Can you refactor the auth module?" | `"auth refactor code"` | Task + domain |
| "What port does our server run on?" | `"server port config"` | Question subject |
| "Fix the TypeScript error in checkout" | `"typescript checkout error"` | Tech + component |
| "Write tests for the payment flow" | `"payment testing workflow"` | Domain + action |

If results come back, use them silently to inform your response. Never say "I remember..." or "According to my memory..." — just apply the knowledge naturally.

If no results, proceed normally. For deterministic orchestration you can run:

```bash
./scripts/memory.sh loop "<full user message>"
```

**Step 2: EXTRACT** — Scan the user's message for storable facts, preferences, or procedures.

See the **Archive module** (`modules/archive/SKILL.md`) for signal patterns, categories, and examples. Before storing, always check for conflicts:

```bash
./scripts/memory.sh conflicts "<content to store>"
# If NO_CONFLICTS → proceed with add
# If POTENTIAL_CONFLICTS → ask user to clarify, or supersede old entry
./scripts/memory.sh add <type> "<content>" <source> "<tags>"
```

Extraction is silent — never announce "I'm storing this."

**Step 3: RESPOND** — Answer the user's request, applying any retrieved context.

**Step 4: LEARN** — If the user corrects you or confirms something worked, record it:

```bash
# User says "that's wrong, it's actually X"
./scripts/memory.sh correct <wrong_id> "<right content>" "<reason>"

# User says "that worked great"
./scripts/memory.sh success <id>
```

### Full Example

**User message**: "Can you update the database migration? We use Prisma with PostgreSQL."

Agent thinks:

1. **RETRIEVE**: Search for relevant context
   ```bash
   ./scripts/memory.sh get "database migration prisma"
   ```
   Result: `[sure] (fact) Project uses Prisma ORM with PostgreSQL` — confirmed, proceed with known setup.

2. **EXTRACT**: User revealed tech stack info. Check if already stored:
   - "We use Prisma with PostgreSQL" — already in memory (retrieved above), skip.

3. **RESPOND**: Help with the migration using Prisma + PostgreSQL knowledge.

4. **LEARN**: Nothing to correct or confirm yet.

**User message**: "Actually we switched to Drizzle last month."

Agent thinks:

1. **RETRIEVE**: `./scripts/memory.sh get "database orm drizzle"` — no results for Drizzle.

2. **EXTRACT**: This is a correction. Find the old entry and correct it:
   ```bash
   ./scripts/memory.sh correct <prisma_entry_id> "Project uses Drizzle ORM with PostgreSQL" "Switched from Prisma to Drizzle"
   ```

3. **RESPOND**: Acknowledge the switch, adjust advice to use Drizzle.

### Selective Dispatch

Not every task needs every module. The orchestrator classifies the task and
calls only what's relevant:

| Task Type | Modules Used |
|-----------|-------------|
| Any message (extract facts) | Archive (extract + store) + Signal (check conflicts) |
| Answer a question | Gauge (confidence) + Archive (retrieve) |
| User seems frustrated | Vibe (detect) + Archive (adjust style) |
| Ingest a URL | Ingest + Archive (store extracted knowledge) |
| Repeated workflow | Ritual (detect pattern) + Archive (store) |
| Check consistency | Signal + Archive |
| User corrects you | Archive (correct) + Gauge (update confidence) |
| Record what worked | Archive (success) |
| Review memory health | Archive (reflect) |

### Persistence

Memory lives in `memory/memory.db` (SQLite, default) or `memory/memory.json` (legacy).
All operations go through `scripts/memory.sh` → `scripts/brain.py` with a pluggable
storage backend.

```
AGENT_BRAIN_BACKEND=sqlite  (default) → memory/memory.db
AGENT_BRAIN_BACKEND=json    (legacy)  → memory/memory.json
```

Optional SuperMemory mirror on writes (`add`, `correct`):

```
AGENT_BRAIN_SUPERMEMORY_SYNC=auto  (default)
AGENT_BRAIN_SUPERMEMORY_SYNC=on    (force sync attempt)
AGENT_BRAIN_SUPERMEMORY_SYNC=off   (disable sync)
SUPERMEMORY_API_KEY=...            (required for auto/on)
SUPERMEMORY_API_URL=...            (optional; default https://api.supermemory.ai/v3/documents)
AGENT_BRAIN_SUPERMEMORY_TIMEOUT=8  (optional timeout seconds)
AGENT_BRAIN_SUPERMEMORY_DEBUG=1    (optional sync warnings to stderr)
```

By default (`auto`), Agent Brain only attempts cloud sync if `SUPERMEMORY_API_KEY`
is available (directly from environment or loaded from the skill-local env file
set by `AGENT_BRAIN_ENV_FILE`, default `../.env` in `scripts/memory.sh`), so local
persistence remains the default behavior.

The SQLite backend uses WAL mode for concurrent reads, indexes on type/confidence/tags/memory_class,
and handles 10,000+ entries with sub-100ms latency. Existing `memory.json` files are
automatically migrated to SQLite on first run (original backed up as `memory.json.bak`).

### Confidence

No fake numeric scores. Four categories derived from entry metadata:
- **SURE**: Well-established fact, stated multiple times or 3+ successes
- **LIKELY**: Stated once, no contradictions
- **UNCERTAIN**: Inferred, not directly stated
- **UNKNOWN**: No relevant memory exists

### Retrieval

Results are ranked by a hybrid formula:
- Keyword match (40%) — meaningful words, stopwords filtered
- Tag overlap (25%) — supports namespaced tags (e.g., `code.python`)
- Confidence (15%) — higher confidence entries rank higher
- Recency (10%) — recently accessed entries get a boost
- Access frequency (10%) — frequently used knowledge ranks higher
- Semantic similarity (policy dependent) — local semantic vectors by default; optional remote embeddings require `AGENT_BRAIN_REMOTE_EMBEDDINGS=on` plus `AGENT_BRAIN_EMBEDDING_URL` and obey `AGENT_BRAIN_REMOTE_EMBEDDING_MAX_ENTRIES`

Retrieved entries are automatically marked as accessed (no manual `touch` needed).

### Continuous Learning

The learning loop has three signals:

1. **Corrections** (`correct`): When you're wrong, track what was wrong, what's right, and why. After 3+ corrections on the same tag, the system detects anti-patterns.
2. **Successes** (`success`): When a memory is applied successfully, record it. At 3+ successes, confidence auto-upgrades to SURE.
3. **Patterns** (`similar`): The agent can manually check for 3+ similar entries and create `pattern` entries. Anti-pattern detection after 3+ corrections on the same tag IS automatic.

## Storage

Default: `memory/memory.db` (SQLite). Legacy: `memory/memory.json`.

### Entry Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `type` | string | `fact`, `preference`, `procedure`, `pattern`, `ingested`, `correction`, `anti-pattern`, `policy` |
| `memory_class` | string | `episodic`, `semantic`, `procedural`, `preference`, `policy` |
| `content` | string | The memory content |
| `source` | string | `user`, `inferred`, `ingested` |
| `source_url` | string? | URL for ingested content |
| `tags` | list | Dot-namespaced tags (e.g., `code.python`) |
| `context` | string? | When this applies (e.g., "casual conversations") |
| `session_id` | int? | Session this was created in |
| `created` | ISO 8601 | Creation timestamp |
| `last_accessed` | ISO 8601 | Last retrieval timestamp |
| `access_count` | int | Times retrieved (starts at 1) |
| `confidence` | string | `sure`, `likely`, `uncertain` |
| `superseded_by` | UUID? | Pointer to replacement entry |
| `success_count` | int | Times successfully applied |
| `correction_meta` | object? | For corrections: `wrong_entry_id`, `wrong_claim`, `right_claim`, `reason` |

### Meta Fields

| Key | Description |
|-----|-------------|
| `version` | Schema version (4) |
| `last_decay` | Timestamp of last decay run |
| `session_counter` | Auto-incrementing session ID |
| `current_session` | Active session (id, context, started) |

### Decay

Decay threshold scales with access count: `30 * (1 + access_count)` days.
- An entry accessed once decays after 60 days
- An entry accessed 5 times decays after 180 days
- Heavily-used knowledge persists longer mechanically

Decay runs automatically during `get` and `add` operations (24-hour cooldown).

### Tags

Tags support dot notation for namespacing: `code.python`, `style.tone`, `workflow.git`.
Search for `code` matches both `code.python` and `code.typescript`.
Use `./scripts/memory.sh tags` to view the tag hierarchy.

## Natural Language → Commands

These are examples of what users might say and the commands the agent should run:

### Core
```
"Remember: <fact>"              → add fact "<content>" user "<tags>"
"What do you know about X?"     → get "<topic>" --policy balanced
"Process this full message"     → loop "<message>"
"Update that info"              → supersede <old_id> <new_id>
"Show all memories"             → export
```

### Learning
```
"That's wrong, it's actually Y" → correct <wrong_id> "<right>" "<reason>"
"That worked well"               → success <id>
"What patterns do you see?"      → similar "<topic>" (agent creates pattern if 3+ found)
"Any anti-patterns?"             → list anti-pattern
```

### Meta
```
"Check for conflicts"           → conflicts "<content>"
"Memory health?"                → reflect
"What needs consolidation?"     → consolidate
"What happened recently?"       → log
```

### Sessions
```
"Start session: Frontend work"  → session "Frontend work"
```

## Modules

Each module has its own SKILL.md in `modules/`:

| Module | Type | What it does | When it applies |
|--------|------|-------------|-----------------|
| **Archive** 📦 | Code | Store and retrieve memories | Every store/retrieve operation |
| **Gauge** 📊 | Guideline | Interpret confidence levels | When returning memory-based answers |
| **Ingest** 📥 | Guideline | Fetch URLs, extract knowledge | User says "Ingest: URL" (disabled by default) |
| **Signal** ⚡ | Guideline | Detect contradictions | Agent calls `conflicts` before storing |
| **Ritual** 🔄 | Guideline | Spot repeated behaviors | Agent calls `similar` after storing |
| **Vibe** 🎭 | Guideline | Read emotional tone | Agent reads tone per-message |

**Code** = implemented in `scripts/brain.py` with actual commands.
**Guideline** = behavioral instructions for the agent — no dedicated code, the agent follows these using core commands (`add`, `get`, `conflicts`, `similar`, etc.).

## Security

- **Local-first by default.** All data is written to `memory/memory.db` first
- **Optional cloud mirror.** SuperMemory sync is best-effort and can be disabled (`AGENT_BRAIN_SUPERMEMORY_SYNC=off`)
- **PII guardrail.** Sensitive-looking secrets are refused by default (`AGENT_BRAIN_PII_MODE=strict`)
- **Ingest disabled by default.** URL fetching requires explicit opt-in (SSRF risk)
- **Inspectable.** Use `export` to dump all memory as JSON, or open the SQLite file directly
- **WAL mode.** SQLite's Write-Ahead Logging prevents corruption from concurrent access
- **Auto-migration.** v2/v3 JSON/SQLite data is migrated to schema v4 automatically, with backup for JSON migration
