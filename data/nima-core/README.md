<p align="center">
  <img src="assets/banner.png" alt="NIMA Core" width="700" />
</p>

<h1 align="center">NIMA Core</h1>

<p align="center">
  <strong>Noosphere Integrated Memory Architecture</strong><br/>
  Persistent memory, emotional intelligence, and semantic recall for AI agents.
</p>

<p align="center">
  <a href="https://nima-core.ai"><b>🌐 nima-core.ai</b></a> · 
  <a href="https://github.com/lilubot/nima-core">GitHub</a> · 
  <a href="https://clawhub.com/skills/nima-core">ClawHub</a> · 
  <a href="./CHANGELOG.md">Changelog</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-3.1.0-blue" alt="Version" />
  <img src="https://img.shields.io/badge/python-3.9%2B-green" alt="Python" />
  <img src="https://img.shields.io/badge/node-18%2B-green" alt="Node" />
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="License" />
</p>

---

> *"Your AI wakes up fresh every session. NIMA gives it a past."*

NIMA Core is the memory system that makes AI agents **remember**. It captures conversations, encodes them as searchable memories with emotional context, and injects relevant history before every response — so your bot sounds like it's been paying attention all along.

**Works with any OpenClaw bot. One install script. Zero config to start.**

---

## ⚡ 30-Second Install

```bash
pip install nima-core && nima-core
```

That's it. The setup wizard handles everything:
- Creates `~/.nima/` directory
- Installs OpenClaw hooks
- Configures your embedding provider
- Restarts the gateway

**Or clone and install manually:**

```bash
git clone https://github.com/lilubot/nima-core.git
cd nima-core
./install.sh
openclaw gateway restart
```

Your bot now has persistent memory. Every conversation is captured, indexed, and recalled automatically.

---

## 🆕 What's New in v3.0

### Complete Cognitive Architecture

NIMA is no longer just memory — it's a **full cognitive stack** for AI agents:

| Module | What It Does | Since |
|--------|-------------|-------|
| **Memory Capture** | 3-layer capture (input/contemplation/output) with 4-phase noise filtering | v2.0 |
| **Semantic Recall** | Vector + text hybrid search, ecology scoring, token-budgeted injection | v2.0 |
| **Dynamic Affect** | Panksepp 7-affect emotional state tracking (SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY) | v2.1 |
| **Memory Pruner** | LLM distillation of old conversations into semantic gists, 30-day suppression limbo | v2.3 |
| **Dream Consolidation** | Nightly synthesis — extracts insights and patterns from episodic memory via LLM | v2.4 |
| **Hive Mind** | Multi-agent memory sharing via shared LadybugDB + optional Redis pub/sub | v2.5 |
| **Precognition** | Temporal pattern mining → predictive memory pre-loading | v2.5 |
| **Lucid Moments** | Spontaneous surfacing of emotionally-resonant memories | v2.5 |

### v3.0.2 Bug Fixes
- **Fixed:** ClawHub package was missing `nima_core/cognition/` directory and all OpenClaw hook files due to `.clawhubignore` glob pattern bug
- **Fixed:** All subdirectories now correctly included in published package

### v3.0.0 Highlights
- Version alignment across all modules
- Full package audit and dependency cleanup

---

## 🧠 How It Works

```text
  User message arrives
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────┐
  │ nima-memory  │────▶│ Capture → Filter → Store │
  │  (on save)   │     │ 4-phase noise remediation│
  └──────────────┘     └─────────────────────────┘
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────┐
  │ nima-recall  │────▶│ Search → Score → Inject  │
  │ (before LLM) │     │ Text + Vector + Ecology  │
  └──────────────┘     └─────────────────────────┘
         │
         ▼
  ┌──────────────┐     ┌─────────────────────────┐
  │ nima-affect  │────▶│ VADER → Panksepp 7-Affect│
  │ (on message) │     │ Emotional state tracking │
  └──────────────┘     └─────────────────────────┘
         │
         ▼
  Agent responds with memory + emotional awareness
```

**Three hooks, fully automatic:**

| Hook | Fires | Does |
|------|-------|------|
| `nima-memory` | After each message | Captures text → filters noise → stores in graph DB |
| `nima-recall-live` | Before agent responds | Searches relevant memories → injects as context |
| `nima-affect` | On each message | Detects emotion → updates 7-dimensional affect state |

---

## 📦 Package Contents

```text
nima-core/
├── SKILL.md                          # ClawHub skill definition
├── README.md                         # This file
├── CHANGELOG.md                      # Full version history
├── install.sh                        # One-command installer
├── setup.py                          # pip install support
├── requirements.txt                  # Core dependencies
│
├── nima_core/                        # Python core library
│   ├── __init__.py                   # Lazy imports, version, public API
│   ├── connection_pool.py            # SQLite connection pool (WAL, thread-safe)
│   ├── logging_config.py             # Singleton logger
│   ├── metrics.py                    # Thread-safe counters/timings
│   ├── memory_pruner.py              # Episodic distillation engine
│   ├── dream_consolidation.py        # Nightly memory synthesis
│   ├── hive_mind.py                  # Multi-agent memory sharing
│   ├── precognition.py               # Temporal pattern mining
│   ├── lucid_moments.py              # Spontaneous memory surfacing
│   └── cognition/                    # Emotional intelligence
│       ├── dynamic_affect.py         # Panksepp 7-affect system
│       ├── emotion_detection.py      # Text emotion extraction
│       ├── affect_correlation.py     # Cross-affect analysis
│       ├── affect_history.py         # Temporal affect tracking
│       ├── affect_interactions.py    # Affect coupling dynamics
│       ├── archetypes.py             # Personality baselines
│       ├── personality_profiles.py   # JSON personality configs
│       ├── response_modulator_v2.py  # Affect → response modulation
│       └── exceptions.py             # Custom exceptions
│
├── openclaw_hooks/                   # OpenClaw plugin hooks
│   ├── nima-memory/                  # Capture hook
│   │   ├── index.js                  # Hook entry point
│   │   ├── openclaw.plugin.json      # Plugin manifest
│   │   ├── ladybug_store.py          # LadybugDB storage backend
│   │   ├── embeddings.py             # Multi-provider embedding
│   │   ├── backfill.py               # Historical transcript import
│   │   ├── health_check.py           # DB integrity checks
│   │   └── ...                       # Migration, benchmarks, docs
│   ├── nima-recall-live/             # Recall hook
│   │   ├── index.js                  # Hook entry point
│   │   ├── lazy_recall.py            # Current recall engine
│   │   ├── ladybug_recall.py         # LadybugDB-native recall
│   │   └── build_embedding_index.py  # Offline index builder
│   ├── nima-affect/                  # Affect hook
│   │   ├── index.js                  # Hook entry point
│   │   ├── vader-affect.js           # VADER sentiment analyzer
│   │   └── emotion-lexicon.js        # Emotion keyword lexicon
│   └── shared/                       # Shared utilities
│       ├── resilient.js              # Auto-retry with backoff
│       └── error-handling.js         # Graceful error wrappers
```

---

## 🔧 Configuration

### Embedding Providers

NIMA needs an embedding model to create searchable memory vectors. **Pick one:**

| Provider | Setup | Dims | Cost | Best For |
|----------|-------|------|------|----------|
| **🏠 Local** (default) | `NIMA_EMBEDDER=local` + `pip install sentence-transformers` | 384 | Free | Privacy, offline, dev |
| **🚀 Voyage AI** | `NIMA_EMBEDDER=voyage` + `VOYAGE_API_KEY` | 1024 | $0.12/1M tok | Production (best quality/cost) |
| **🤖 OpenAI** | `NIMA_EMBEDDER=openai` + `OPENAI_API_KEY` | 1536 | $0.13/1M tok | If you already use OpenAI |
| **🦙 Ollama** | `NIMA_EMBEDDER=ollama` + `NIMA_OLLAMA_MODEL` | 768 | Free | Local GPU |

> **Don't have a preference?** Leave `NIMA_EMBEDDER` unset — defaults to `local` with `all-MiniLM-L6-v2`. Free, offline, no API keys.

### Database Backend

| | SQLite (default) | LadybugDB (recommended) |
|--|-----------------|------------------------|
| **Setup** | Zero config | `pip install real-ladybug` |
| **Text Search** | 31ms | **9ms** (3.4x faster) |
| **Vector Search** | External only | **Native HNSW** (18ms) |
| **Graph Queries** | SQL JOINs | **Native Cypher** |
| **DB Size** | ~91 MB | **~50 MB** (44% smaller) |

```bash
# Upgrade to LadybugDB when ready:
pip install real-ladybug
python -c "from nima_core.storage import migrate; migrate()"
```

#### LadybugDB Schema

When using the recommended **LadybugDB** backend — a custom graph database (Kùzu-based) using Cypher query language (format: `.lbug` binary) — the schema is as follows:

**Node Tables:**

| Table | Description |
|-------|-------------|
| **MemoryNode** | Primary storage (~330 nodes) |
| | `id INT64 PRIMARY KEY` |
| | `timestamp INT64` — Unix ms |
| | `layer STRING` — Memory type (see Layer Types below) |
| | `text STRING` — Full memory content |
| | `summary STRING` — Truncated to 200 chars |
| | `who STRING` — Person associated (David, Lilu, etc.) |
| | `affect_json STRING` — Emotion state at capture (JSON) |
| | `session_key STRING` — Source session |
| | `conversation_id STRING` — Conversation context |
| | `turn_id STRING` — Turn within conversation |
| | `fe_score DOUBLE` — Free Energy score (importance proxy) |
| | `strength DOUBLE` — Decay strength (default 1.0) |
| | `decay_rate DOUBLE` — Forgetting rate (default 0.01) |
| | `affect_decontextualized BOOL` — Emotion stripped for cold recall |
| **Turn** | Conversation structure |
| | `id INT64 PRIMARY KEY` |
| | `turn_id STRING` |
| | `timestamp INT64` |
| | `affect_json STRING` |

**Relationship Tables:**

| Relationship | From → To | Properties |
|--------------|-----------|------------|
| `relates_to` | MemoryNode → MemoryNode | `relation STRING`, `weight DOUBLE` |
| `has_input` | Turn → MemoryNode | — |
| `has_contemplation` | Turn → MemoryNode | — |
| `has_output` | Turn → MemoryNode | — |

##### Layer Types (valid `layer` values)

| Layer | Description |
|-------|-------------|
| `episodic` | Raw conversation turns (input/output) |
| `semantic` | Extracted facts, preferences, knowledge |
| `dream` | Consolidated insights from nightly synthesis |
| `insight` | Key realization or connection |
| `pattern` | Recurring behavioral pattern |
| `synthesis` | Cross-domain connection |
| `consolidation` | Memory pruner output (distilled) |
| `precognition` | Predicted future session |
| `lucid` | Spontaneously surfaced memory |
| `input` | User input from a conversation turn |
| `output` | Agent output from a conversation turn |
| `contemplation` | Agent's internal thought process |
| `legacy_vsa` | Older memory type from VSA-based systems |

##### Relation Types (valid `relation` values in `relates_to`)

| Relation | Meaning |
|----------|---------|
| `related_to` | General association |
| `caused_by` | Causal chain |
| `reminds_of` | Analogy or similarity |
| `contradicts` | Opposing view |
| `supports` | Reinforcing evidence |
| `elicits` | Emotion trigger |
| `refers_to` | Topic reference |
| `part_of` | Compositional hierarchy |
| `triggered` | An input that triggered a contemplation |
| `produced` | A contemplation that produced an output |
| `responded_to` | An output that responded to an input |

##### Indexes (for performance)

```cypher
// Recommended indexes
CREATE INDEX idx_memory_node_layer ON MemoryNode(layer);
CREATE INDEX idx_memory_node_who ON MemoryNode(who);
CREATE INDEX idx_memory_node_timestamp ON MemoryNode(timestamp);
CREATE INDEX idx_memory_node_session ON MemoryNode(session_key);
CREATE INDEX idx_turn_timestamp ON Turn(timestamp);
```

##### Schema Version Tracking

Schema migrations are tracked in the database:

```cypher
// Create schema-version tracking table
CREATE NODE TABLE IF NOT EXISTS _nima_schema (
    version INT64 PRIMARY KEY,
    applied_at INT64,
    description STRING
);
```

```cypher
// Check current schema version
MATCH (s:_nima_schema)
RETURN s.version, s.description ORDER BY s.version DESC LIMIT 1;
// Current version: 003
```

##### Example Cypher Queries

```cypher
// Get recent memories for a person
MATCH (t:Turn)-[:has_input|has_output]->(m:MemoryNode {who: 'David'})
WHERE t.timestamp > 1700000000000
RETURN m ORDER BY m.timestamp DESC LIMIT 10;

// Find memories related to a topic
MATCH (m:MemoryNode)
WHERE m.text CONTAINS 'consciousness' OR m.summary CONTAINS 'consciousness'
RETURN m ORDER BY m.fe_score DESC LIMIT 5;

// Get conversation thread
MATCH (t:Turn)-[:has_input|has_output]->(m:MemoryNode {conversation_id: 'abc123'})
RETURN m ORDER BY t.timestamp;

// Find emotionally significant memories
MATCH (m:MemoryNode)
WHERE m.fe_score > 0.7
RETURN m ORDER BY m.fe_score DESC LIMIT 10;

// Get all related memories (graph traversal)
MATCH (m1:MemoryNode {id: 123})-[:relates_to]->(m2:MemoryNode)
RETURN m2;

// Find dream consolidations
MATCH (m:MemoryNode {layer: 'dream'})
RETURN m ORDER BY m.timestamp DESC LIMIT 5;

// Memories by time range
MATCH (m:MemoryNode)
WHERE m.timestamp >= 1704067200000 AND m.timestamp < 1704153600000
RETURN m ORDER BY m.timestamp;

// Get memory counts by layer
MATCH (m:MemoryNode)
RETURN m.layer, count(m) AS count ORDER BY count DESC;
```

**Supporting Files** (same `~/.nima/memory/` directory):

| File | What it is |
|------|------------|
| `graph.sqlite` | 50MB — Graphiti temporal knowledge graph (separate system) |
| `embedding_index.npy` | 478MB — NumPy vector index for semantic search |
| `embedding_cache.db` | SQLite — Cached embeddings keyed by content hash |
| `precognitions.sqlite` | SQLite — Predicted future session patterns |
| `faiss.index` | 16MB — FAISS vector index (older, may be superseded) |
| `.nimaignore` | Ignore patterns for memory capture (see project root) |

### Environment Variables

```bash
# Embedding (default: local — no keys needed)
NIMA_EMBEDDER=local|voyage|openai|ollama
VOYAGE_API_KEY=pa-xxx
OPENAI_API_KEY=sk-xxx
NIMA_OLLAMA_MODEL=nomic-embed-text

# Data paths
NIMA_DATA_DIR=~/.nima/memory
NIMA_DB_PATH=~/.nima/memory/ladybug.lbug

# Memory pruner (optional)
NIMA_DISTILL_MODEL=claude-haiku-4-5
ANTHROPIC_API_KEY=sk-ant-xxx

# Logging
NIMA_LOG_LEVEL=INFO
NIMA_DEBUG_RECALL=1
```

---

## 🔌 Hook Installation

### Quick Install
```bash
./install.sh
openclaw gateway restart
```

### Manual Install
```bash
# Copy hooks to extensions
cp -r openclaw_hooks/nima-memory ~/.openclaw/extensions/
cp -r openclaw_hooks/nima-recall-live ~/.openclaw/extensions/
cp -r openclaw_hooks/nima-affect ~/.openclaw/extensions/

# Add to openclaw.json
{
  "plugins": {
    "allow": ["nima-memory", "nima-recall-live", "nima-affect"]
  }
}

# Restart
openclaw gateway restart
```

### Verify
```bash
openclaw status          # Hooks loaded?
ls ~/.nima/memory/       # Memories captured?
cat ~/.nima/affect/affect_state.json  # Affect state?
```

---

## 🎭 Affect System

Tracks emotional state using **Panksepp's 7 primary affects**:

| Affect | Feels Like | Triggers |
|--------|-----------|----------|
| **SEEKING** | Curiosity, anticipation | Questions, new topics |
| **RAGE** | Frustration, boundaries | Conflict, demands |
| **FEAR** | Caution, vigilance | Threats, uncertainty |
| **LUST** | Desire, motivation | Goals, enthusiasm |
| **CARE** | Nurturing, empathy | Sharing, vulnerability |
| **PANIC** | Distress, sensitivity | Loss, rejection |
| **PLAY** | Joy, humor, bonding | Jokes, creativity |

### Archetype Presets

```python
from nima_core import DynamicAffectSystem
affect = DynamicAffectSystem(identity_name="my_bot", baseline="guardian")
```

| Archetype | Vibe | High | Low |
|-----------|------|------|-----|
| **Guardian** | Protective, warm | CARE, SEEKING | PLAY |
| **Explorer** | Curious, bold | SEEKING, PLAY | FEAR |
| **Trickster** | Witty, irreverent | PLAY, SEEKING | CARE |
| **Empath** | Deeply feeling | CARE, PANIC | RAGE |
| **Sage** | Balanced, wise | SEEKING | All balanced |

---

## 🌙 Dream Consolidation

Nightly synthesis extracts insights and patterns from recent memories:

```bash
# Run manually
python -m nima_core.dream_consolidation

# Or schedule via OpenClaw cron (runs at 2 AM)
```

### How It Works
1. Pulls recent episodic memories from LadybugDB
2. LLM extracts `Insight` and `Pattern` objects
3. VSA-style vector blending compresses semantics
4. Stores consolidated dream memories back to DB
5. Prunes raw material after successful consolidation

---

## 🐝 Hive Mind

Share memory across multiple agents:

```python
from nima_core import HiveMind

hive = HiveMind(db_path="~/.nima/memory/ladybug.lbug")

# Inject context into a sub-agent's prompt
context = hive.build_agent_context("research quantum computing", max_memories=8)

# Capture results back
hive.capture_agent_result("researcher-1", "Found 3 key papers...", "claude-sonnet-4-5")
```

Optional Redis pub/sub for real-time agent communication:
```bash
pip install nima-core[hive]
```

---

## 🔮 Precognition

Mine temporal patterns and pre-load relevant memories before the user asks:

```python
from nima_core import NimaPrecognition

precog = NimaPrecognition(db_path="~/.nima/memory/ladybug.lbug")
precog.run_mining_cycle()  # Extract patterns → generate predictions → store
```

---

## 💡 Lucid Moments

Spontaneously surface emotionally-resonant memories:

```python
from nima_core import LucidMoments

lucid = LucidMoments(db_path="~/.nima/memory/ladybug.lbug")
moment = lucid.surface_moment()  # Returns a natural "this just came to me..." message
```

Safety: trauma keyword filtering, quiet hours, daily caps, minimum gap enforcement.

---

## 🧹 Memory Pruner

Distill old conversations into compact semantic summaries:

```bash
# Preview
python -m nima_core.memory_pruner --min-age 14

# Live run
python -m nima_core.memory_pruner --min-age 14 --live

# Restore from suppression
python -m nima_core.memory_pruner --restore 12345
```

No database writes — suppression is file-based, fully reversible within 30 days.

---

## ⏰ Scheduling Setup (OpenClaw Cron)

NIMA's autonomous features — Lucid Moments, Dream Consolidation, Memory Pruner, and Embedding Index — are designed to run on a schedule. Here's the recommended cron configuration for OpenClaw.

### Lucid Moments — 4× daily

Surfaces emotionally-resonant memories to your user at natural intervals.

```json
{
  "name": "lucid-memory-moments",
  "schedule": { "kind": "cron", "expr": "0 10,14,18,20 * * *", "tz": "America/New_York" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run the lucid moments check:\n1. Run: cd ~/.openclaw/workspace && .venv/bin/python3 lilu_core/cognition/lucid_moments.py --status\n2. If timing is good (says 'Ready'), run: .venv/bin/python3 lilu_core/cognition/lucid_moments.py\n3. If a pending file was written, read: cat ~/.openclaw/workspace/memory/pending_lucid_moment.txt\n4. Send that exact text to the user via the message tool\n5. If timing wasn't right, do nothing silently\nSend the message as a natural surfaced memory — no framing or prefix.",
    "timeoutSeconds": 120
  },
  "delivery": { "mode": "none" }
}
```

### Dream Consolidation — nightly at 2 AM

Consolidates the last 24h of memories and extracts patterns.

```json
{
  "name": "lilu_dream_consolidation",
  "schedule": { "kind": "cron", "expr": "0 2 * * *", "tz": "America/New_York" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "cd ~/.openclaw/workspace && .venv/bin/python3 lilu_core/lilu.py dream --hours 24. Report what memories were consolidated and any patterns found.",
    "timeoutSeconds": 600
  },
  "delivery": { "mode": "announce" }
}
```

### Memory Pruner — nightly at 2 AM

Distills old episodic turns into compact semantic memories.

```json
{
  "name": "nima-memory-pruner",
  "schedule": { "kind": "cron", "expr": "0 2 * * *", "tz": "America/New_York" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "cd ~/.openclaw/workspace && .venv/bin/python3 lilu_core/cognition/memory_pruner.py --min-age 7 --live --max-sessions 10. Report sessions distilled and turns suppressed.",
    "timeoutSeconds": 300
  },
  "delivery": { "mode": "announce" }
}
```

### Embedding Index Rebuild — nightly at 3 AM

Keeps vector recall indexes fresh.

```json
{
  "name": "nima-embedding-index",
  "schedule": { "kind": "cron", "expr": "0 3 * * *" },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "Rebuild embedding index for NIMA memory recall"
  }
}
```

### Precognition

Precognition runs automatically on every incoming message via the `nima-affect` OpenClaw plugin — no separate cron needed. The predicted session patterns it generates are injected into context before each agent response.

---

## 📊 Performance

| Operation | SQLite | LadybugDB |
|-----------|--------|-----------|
| Text search | 31ms | **9ms** |
| Vector search | — | **18ms** |
| Full recall cycle | ~50ms | **~30ms** |
| Context overhead | ~180 tokens | **~30 tokens** |

---

## 🔒 Privacy

- ✅ All data stored locally in `~/.nima/`
- ✅ Local embedding mode = **zero external calls**
- ✅ No NIMA-owned servers, no proprietary tracking, no analytics to external services
- ⚠️ Opt-in: HiveMind (Redis), Precognition (LLM), cloud embeddings — see SKILL.md for details
- 🔒 Embedding API calls only when explicitly enabling via env vars

---

## 🔄 Upgrading

### From v2.x → v3.x

```bash
git pull origin main
pip install -e .  # or: pip install nima-core --upgrade
openclaw gateway restart
```

No breaking changes — v3.0 is a package consolidation release. All v2.x configs continue to work.

### From v1.x → v2.x

```bash
cp -r ~/.nima ~/.nima.backup
rm -rf ~/.openclaw/extensions/nima-*
cp -r openclaw_hooks/* ~/.openclaw/extensions/
pip install real-ladybug  # optional
openclaw gateway restart
```

---

## 🤝 Contributing

PRs welcome. Python 3.9+ compatibility, conventional commits.

```bash
git clone https://github.com/lilubot/nima-core.git
cd nima-core
pip install -e ".[vector]"
python -m pytest tests/
```

---

## License

MIT License — free for any AI agent, commercial or personal.

---

<p align="center">
  <a href="https://nima-core.ai"><b>🌐 nima-core.ai</b></a><br/>
  Built by the NIMA Core Team
</p>
