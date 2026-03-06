# Tiered Memory v2.0

> *A mind that remembers everything is as useless as one that remembers nothing.  
> The art is knowing what to keep.* 🧠

Three-tier memory system for OpenClaw agents implementing the EvoClaw Tiered Memory Architecture. Inspired by human cognition and PageIndex tree-based retrieval.

**Version:** 2.0.0  
**License:** MIT  
**Python:** 3.8+ (zero external dependencies)

---

## What's New in v2.0

🆕 **LLM-Powered Tree Search** — Reasoning-based retrieval instead of keyword matching  
🆕 **Distillation Engine** — 3-stage compression (500B → 80B → 20B)  
🆕 **Hot Memory Structure** — Identity, owner profile, active context, lessons (auto-pruning)  
🆕 **Score-Based Tiers** — >=0.7 Hot, >=0.3 Warm, >=0.05 Cold, <0.05 Frozen  
🆕 **Multi-Agent Support** — Agent ID scoping for all operations  
🆕 **Consolidation Modes** — Quick/daily/monthly/full with tree pruning  
🆕 **Critical Sync** — Cloud-first hot+tree sync after every conversation  
🆕 **Metrics & Observability** — Comprehensive memory system metrics  

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 AGENT CONTEXT                        │
│                                                     │
│  ┌──────────────┐  ┌──────────────────────────┐    │
│  │ Memory Tree  │  │  Retrieved Memory Nodes  │    │
│  │ Index (~2KB) │  │  (on-demand, ~1-3KB)     │    │
│  │              │  │                          │    │
│  │ Always in    │  │  Fetched per conversation│    │
│  │ context      │  │  based on tree reasoning │    │
│  └──────┬───────┘  └──────────────────────────┘    │
│         │                                           │
└─────────┼───────────────────────────────────────────┘
          │
          │ Tree Search (LLM reasoning)
          │
┌─────────┼───────────────────────────────────────────┐
│         ▼              MEMORY TIERS                  │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │    HOT      │  │    WARM      │  │    COLD    │ │
│  │  (~5KB)     │  │  (~50KB)     │  │ (Unlimited)│ │
│  │             │  │              │  │            │ │
│  │ Core memory │  │ Recent facts │  │ Full archive│ │
│  │ Always in   │  │ 30-day       │  │ Turso DB   │ │
│  │ tree index  │  │ retention    │  │ Query only │ │
│  │             │  │ On-device    │  │            │ │
│  └─────────────┘  └──────────────┘  └────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         DISTILLATION ENGINE                   │  │
│  │                                              │  │
│  │  Raw conversation → Distilled facts → Core  │  │
│  │  500 bytes       → 80 bytes        → 20 B  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Features

### 🧠 Human-Like Memory
- **Consolidation** — Short-term → long-term during sleep (cron)
- **Relevance Decay** — Unused memories fade, accessed memories strengthen
- **Strategic Forgetting** — Not remembering everything is a feature
- **Hierarchical Organization** — Navigate categories, not scan linearly

### 🌲 Tree-Based Retrieval
- **Vectorless** — LLM reasoning instead of embedding similarity
- **O(log n) Navigation** — Hierarchical categories, not linear scan
- **Explainable** — Every retrieval traces a path through tree
- **Multi-hop** — Natural navigation across related categories

### 🔴🟡🟢 Three Tiers
- **Hot (5KB):** Identity, owner profile, active context, critical lessons
- **Warm (50KB):** Scored recent facts with decay (30-day retention)
- **Cold (∞):** Unlimited Turso archive (10-year retention)

### 🤖 LLM Integration
- **Tree Search:** Semantic category navigation
- **Distillation:** Extract structured facts from conversations
- **Fallback:** Rule-based when LLM unavailable

### ☁️ Cloud-First
- **Critical Sync:** Hot + tree sync after every conversation
- **Disaster Recovery:** Full restore in <2 minutes
- **Multi-Device:** Same agent across devices

### 📊 Observability
- Tree size, node count, tier sizes
- Retrieval count, accuracy, latency
- Evictions, reinforcements, consolidations
- Context tokens saved vs. flat MEMORY.md

---

## Quick Start

### 1. Install

```bash
# Via ClawHub (recommended)
clawhub install tiered-memory

# Or manually clone
cd skills/
git clone <repo-url> tiered-memory
```

### 2. Initialize

```bash
cd skills/tiered-memory

# Initialize tree categories
python3 scripts/memory_cli.py tree --add "owner" "Owner profile and preferences"
python3 scripts/memory_cli.py tree --add "projects" "Active projects"
python3 scripts/memory_cli.py tree --add "technical" "Technical setup and config"
python3 scripts/memory_cli.py tree --add "lessons" "Lessons learned"

# Initialize cold storage (optional, requires Turso)
export TURSO_URL="https://your-db.turso.io"
export TURSO_TOKEN="your-token"
python3 scripts/memory_cli.py cold --init --db-url "$TURSO_URL" --auth-token "$TURSO_TOKEN"
```

### 3. Store a memory

```bash
python3 scripts/memory_cli.py store \
  --text "Decided to use raw JSON-RPC for BSC to avoid go-ethereum dependency" \
  --category "projects/evoclaw/architecture" \
  --importance 0.8
```

### 4. Retrieve memories

```bash
# Keyword search
python3 scripts/memory_cli.py retrieve --query "BSC decision" --limit 5

# LLM search (more accurate)
python3 scripts/memory_cli.py retrieve \
  --query "what did we decide about blockchain?" \
  --llm --llm-endpoint http://localhost:8080/complete
```

### 5. Run consolidation

```bash
python3 scripts/memory_cli.py consolidate --mode daily
```

---

## Commands

| Command | Description |
|---------|-------------|
| `store` | Store a fact in warm (+ optional cold dual-write) |
| `retrieve` | Search across all tiers (keyword or LLM) |
| `distill` | Extract structured fact from conversation |
| `consolidate` | Run consolidation (quick/daily/monthly/full) |
| `sync-critical` | Sync hot+tree to cloud |
| `metrics` | Show memory system metrics |
| `hot` | Manage hot memory (identity, lessons, projects) |
| `tree` | View/manage category tree index |
| `cold` | Init tables, query cold storage |

See [SKILL.md](SKILL.md) for full command reference.

---

## Memory Tiers

### 🔴 Hot Memory (5KB)

**Always in context.** Core identity and active context.

```json
{
  "identity": {"agent_name": "Alex", "owner_name": "Bowen"},
  "owner_profile": {"personality": "technical, direct", "timezone": "Australia/Sydney"},
  "active_context": {
    "projects": [{"name": "EvoClaw", "status": "Active"}],
    "events": [{"text": "Hackathon Feb 15", "timestamp": 1707350400}],
    "tasks": [{"text": "Deploy to testnet", "status": "pending"}]
  },
  "critical_lessons": [
    {"text": "Test on testnet first", "importance": 0.9}
  ]
}
```

**Auto-pruning:** Max 20 lessons, 10 events, 10 tasks. Removes lowest-importance when full.

### 🟡 Warm Memory (50KB)

**Recent facts with decay scoring.** 30-day retention.

```json
{
  "id": "abc123",
  "text": "Decided raw JSON-RPC for BSC to keep binary small",
  "category": "projects/evoclaw/architecture",
  "importance": 0.8,
  "created_at": 1707350400,
  "access_count": 3,
  "score": 0.742,
  "tier": "warm"
}
```

**Scoring:** `score = importance × exp(-age_days/30) × (1 + 0.1 × access_count)`

**Tier classification:**
- `score >= 0.7` → Hot (promote)
- `score >= 0.3` → Warm (keep)
- `score >= 0.05` → Cold (archive)
- `score < 0.05` → Frozen (delete)

### 🟢 Cold Memory (Unlimited)

**Long-term archive in Turso.** Queryable but never bulk-loaded.

```sql
CREATE TABLE cold_memories (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  text TEXT NOT NULL,
  category TEXT NOT NULL,
  importance REAL,
  created_at INTEGER,
  access_count INTEGER
);
```

**Retention:** 10 years (configurable)

---

## Tree Index

**Hierarchical category map for O(log n) retrieval.**

```
Memory Tree Index
==================================================
📂 Root (warm:15, cold:234)
  📁 owner — Owner profile (warm:5, cold:89)
  📁 projects — Active projects (warm:8, cold:67)
    📁 projects/evoclaw — EvoClaw framework (warm:6, cold:45)
      📁 projects/evoclaw/bsc — BSC integration (warm:3, cold:12)
  📁 technical — Tech setup (warm:2, cold:34)
  📁 lessons — Learned lessons (warm:0, cold:44)

Nodes: 7/50
Size: 1842 / 2048 bytes
```

**Constraints:**
- Max 50 nodes
- Max depth 4
- Max 2KB serialized
- Max 10 children per node

---

## Distillation Engine

**Three-stage compression:**

```
Raw conversation (500B)
  ↓ Extract structured info
Distilled fact (80B)
  ↓ One-line summary
Core summary (20B)
```

**Example:**

```bash
# Input
"User: Let's use raw JSON-RPC for BSC to avoid the go-ethereum dependency.
 Agent: Great idea, keeps the binary smaller."

# Stage 1→2: Distilled
{
  "fact": "Decided raw JSON-RPC for BSC, no go-ethereum",
  "emotion": "determined",
  "topics": ["blockchain", "architecture", "dependencies"],
  "outcome": "positive"
}

# Stage 2→3: Core summary
"BSC integration: raw JSON-RPC (no deps)"
```

**Modes:**
- `rule`: Regex/heuristics (fast, no LLM)
- `llm`: LLM-powered (accurate, requires endpoint)

---

## LLM-Powered Tree Search

**Semantic search using LLM reasoning.**

**Query:** *"What did we decide about the hackathon deadline?"*

**Keyword search returns:**
- `projects/evoclaw` (0.8)
- `technical/deployment` (0.4)

**LLM search reasons:**
- `projects/evoclaw/bsc` (0.95) — "BSC integration for hackathon"
- `active_context/events` (0.85) — "Deadline mentioned here"

**Result:** Fetches memories from both categories.

---

## Multi-Agent Support

**Agent ID scoping** for all operations.

```bash
# Store for agent-2
memory_cli.py store --text "..." --category "..." --agent-id agent-2

# Retrieve for agent-2
memory_cli.py retrieve --query "..." --agent-id agent-2

# Separate file trees
memory/
  default/
    warm-memory.json
    memory-tree.json
  agent-2/
    warm-memory.json
    memory-tree.json
```

---

## Consolidation Modes

| Mode | Actions | Frequency |
|------|---------|-----------|
| **quick** | Evict warm, archive to cold, rebuild hot | Hourly |
| **daily** | quick + prune dead tree nodes | Daily |
| **monthly** | daily + tree rebuild + cold cleanup | Monthly |
| **full** | monthly + full recalculation + deep analysis | On-demand |

```bash
# Quick (hourly, via heartbeat)
memory_cli.py consolidate

# Daily (midnight cron)
memory_cli.py consolidate --mode daily

# Monthly (1st of month cron)
memory_cli.py consolidate --mode monthly --db-url "$TURSO_URL" --auth-token "$TURSO_TOKEN"
```

---

## Critical Sync (Cloud-First)

**Backup hot state + tree to cloud after every conversation.**

```bash
memory_cli.py sync-critical --db-url "$TURSO_URL" --auth-token "$TURSO_TOKEN"
```

**What syncs:**
- Hot memory (identity, lessons, active context)
- Tree index (structure + counts)
- Timestamp

**Disaster recovery:** Restore full agent personality in <2 minutes.

---

## Metrics

```bash
memory_cli.py metrics
```

**Output:**
```json
{
  "tree_index_size_bytes": 1842,
  "tree_node_count": 37,
  "hot_memory_size_bytes": 4200,
  "warm_memory_count": 145,
  "warm_memory_size_kb": 38.2,
  "retrieval_count": 234,
  "evictions_today": 12,
  "consolidation_count": 8,
  "context_tokens_saved": 47800,
  "timestamp": "2026-02-10T14:30:00"
}
```

---

## Configuration

**File:** `config.json` (optional, uses defaults if missing)

```json
{
  "agent_id": "default",
  "hot": {
    "max_bytes": 5120,
    "max_lessons": 20,
    "max_events": 10,
    "max_tasks": 10
  },
  "warm": {
    "max_kb": 50,
    "retention_days": 30,
    "eviction_threshold": 0.3
  },
  "cold": {
    "backend": "turso",
    "retention_years": 10
  },
  "scoring": {
    "half_life_days": 30,
    "reinforcement_boost": 0.1
  },
  "tree": {
    "max_nodes": 50,
    "max_depth": 4,
    "max_size_bytes": 2048
  },
  "distillation": {
    "aggression": 0.7,
    "max_distilled_bytes": 100,
    "mode": "rule"
  }
}
```

---

## Integration with OpenClaw

### After Conversation

```python
import subprocess
import json

# 1. Distill
result = subprocess.run(
    ["python3", "skills/tiered-memory/scripts/memory_cli.py", "distill", "--text", conversation],
    capture_output=True, text=True
)
distilled = json.loads(result.stdout)

# 2. Store
subprocess.run([
    "python3", "skills/tiered-memory/scripts/memory_cli.py", "store",
    "--text", distilled["distilled"]["fact"],
    "--category", "conversations",
    "--importance", "0.7"
])

# 3. Critical sync
subprocess.run([
    "python3", "skills/tiered-memory/scripts/memory_cli.py", "sync-critical",
    "--db-url", os.getenv("TURSO_URL"),
    "--auth-token", os.getenv("TURSO_TOKEN")
])
```

### Before Responding

```python
# Retrieve relevant context
result = subprocess.run([
    "python3", "skills/tiered-memory/scripts/memory_cli.py", "retrieve",
    "--query", user_message,
    "--limit", "5",
    "--llm",
    "--llm-endpoint", "http://localhost:8080/complete"
], capture_output=True, text=True)

memories = json.loads(result.stdout)
context = "\n".join([f"- {m['text']}" for m in memories])
```

### Heartbeat Consolidation

```python
import schedule

# Hourly quick consolidation
schedule.every(2).hours.do(lambda: subprocess.run([
    "python3", "skills/tiered-memory/scripts/memory_cli.py", "consolidate"
]))

# Daily consolidation
schedule.every().day.at("00:00").do(lambda: subprocess.run([
    "python3", "skills/tiered-memory/scripts/memory_cli.py", "consolidate", "--mode", "daily"
]))
```

---

## LLM Integration

### Recommended Models

**For Distillation & Search:**
- Claude 3 Haiku (fast, cheap)
- GPT-4o-mini (balanced)
- Gemini 1.5 Flash (very fast)

**For Tree Rebuilding:**
- Claude 3.5 Sonnet (better reasoning)
- GPT-4o (strong planning)

### Example LLM Endpoint

```python
from flask import Flask, request, jsonify
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic()

@app.route("/complete", methods=["POST"])
def complete():
    data = request.json
    prompt = data["prompt"]
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return jsonify({"text": response.content[0].text})

if __name__ == "__main__":
    app.run(port=8080)
```

---

## Performance

**Context Size:**
- Hot: ~5KB (always)
- Tree: ~2KB (always)
- Retrieved: ~1-3KB per query
- **Total: ~8-15KB** (constant, regardless of agent age)

**Retrieval Speed:**
- Keyword: 10-20ms
- LLM: 300-600ms
- Cold: 50-100ms

**5-Year Scenario:**
- Hot: Still 5KB (living document)
- Warm: Last 30 days (~50KB)
- Cold: ~50MB in Turso
- Tree: Still 2KB (different nodes, same size)
- **Context: Same as day 1**

---

## Comparison

| System | Scaling | Accuracy | Cost | Explainable |
|--------|---------|----------|------|-------------|
| **Flat MEMORY.md** | ❌ Months | ⚠️ Degrades | ❌ Linear | ❌ No |
| **Vector RAG** | ✅ Years | ⚠️ Similarity≠relevance | ⚠️ Moderate | ❌ Opaque |
| **Tiered v2.0** | ✅ Decades | ✅ Reasoning-based | ✅ Fixed | ✅ Yes |

**Why tree > vectors:**
- **98%+ accuracy** vs. 70-80% (PageIndex benchmark)
- **Explainable** — "Projects → EvoClaw → BSC" vs. "cosine 0.73"
- **Multi-hop** — Natural navigation vs. poor
- **False positives** — Low vs. high

---

## Migration from v1.x

**Backward compatible** — Existing files work as-is.

**Steps:**
1. Update: `clawhub update tiered-memory`
2. Consolidate: `memory_cli.py consolidate`
3. Init cold (optional): `memory_cli.py cold --init --db-url ... --auth-token ...`

---

## File Structure

```
skills/tiered-memory/
├── README.md                      # This file
├── SKILL.md                       # Full documentation
├── config.json                    # Configuration (optional)
├── scripts/
│   ├── memory_cli.py             # Main CLI (rewritten v2.0)
│   ├── distiller.py              # Distillation engine (NEW)
│   └── tree_search.py            # LLM tree search (NEW)
└── memory/                        # Generated at runtime
    ├── default/
    │   ├── warm-memory.json
    │   ├── memory-tree.json
    │   ├── hot-memory-state.json
    │   └── metrics.json
    └── agent-2/
        └── ...
```

---

## Dependencies

**Zero external dependencies** — Python stdlib only (except `urllib` for Turso HTTP).

**Requirements:**
- Python 3.8+
- Turso account (optional, for cold storage)
- LLM endpoint (optional, for LLM-powered features)

---

## Contributing

Contributions welcome! This skill is part of the EvoClaw ecosystem.

**Development:**
```bash
# Run tests (coming soon)
python3 -m pytest tests/

# Lint
python3 -m pylint scripts/memory_cli.py
```

---

## License

MIT License — See [LICENSE](LICENSE)

---

## References

- **Design:** [EvoClaw TIERED-MEMORY.md](https://github.com/clawinfra/evoclaw/docs/TIERED-MEMORY.md)
- **Cloud Sync:** [EvoClaw CLOUD-SYNC.md](https://github.com/clawinfra/evoclaw/docs/CLOUD-SYNC.md)
- **Inspiration:** [PageIndex](https://github.com/VectifyAI/PageIndex) (tree-based retrieval)
- **ClawHub:** [skills.openclaw.org](https://skills.openclaw.org)

---

**v2.0.0** — *A mind that remembers everything is as useless as one that remembers nothing. The art is knowing what to keep.* 🧠🌲
