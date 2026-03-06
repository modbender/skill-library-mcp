# 🧠 Memory V2 — Three-Tier AI Agent Memory System

**Give your AI agent persistent, searchable, self-curating memory.**

Memory V2 is a three-tier memory architecture for AI assistants running on [OpenClaw](https://github.com/openclaw/openclaw) (or similar agent frameworks). It captures conversation turns in real-time, stores them as searchable embeddings, and uses a local LLM to curate long-term "gems" — facts, decisions, and lessons worth remembering forever.

No cloud APIs. No subscriptions. Runs entirely on your own hardware.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR AI AGENT                         │
│              (OpenClaw, LangChain, etc.)                 │
│                                                          │
│  Session transcripts written to disk as JSONL            │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────┐
│   🔥 HOT — Redis Buffer  │  ← mem-capture (systemd, every 30s)
│   Raw conversation turns  │    Watches transcript files, dedupes,
│   Ephemeral (~30 min)     │    buffers new turns to Redis list
└──────────────┬───────────┘
               │
               ▼  (cron: every 30 min)
┌──────────────────────────┐
│  🌡️ WARM — Qdrant         │  ← mem-warm (cron)
│  Chunked + embedded       │    Drains Redis → chunks by session
│  Searchable conversations  │    → embeds → stores in Qdrant
│  Auto-expires after 7 days │    Collection: watts_warm
└──────────────┬───────────┘
               │
               ▼  (cron: nightly at 2 AM)
┌──────────────────────────┐
│  🧊 COLD — Qdrant         │  ← mem-curate (cron)
│  LLM-curated gems         │    Reads day's warm memories
│  Structured metadata       │    → LLM extracts gems
│  Permanent storage         │    → embeds → stores in Qdrant
│  Searchable forever        │    Collection: watts_cold
└──────────────────────────┘
```

### Why Three Tiers?

| Tier | Speed | Retention | Content | Use Case |
|------|-------|-----------|---------|----------|
| 🔥 **Hot** | Instant | ~30 min | Raw turns | Real-time buffering |
| 🌡️ **Warm** | Fast | 7 days | Chunked conversations | "What did we talk about yesterday?" |
| 🧊 **Cold** | Fast | Forever | Curated gems | "What was the decision on pricing?" |

The hot tier catches everything. The warm tier makes it searchable. The cold tier distills it into what actually matters — using an LLM that reads the full day's context and extracts structured insights.

---

## What You Need

| Component | Purpose | Notes |
|-----------|---------|-------|
| **Qdrant** | Vector database | Stores warm + cold memories |
| **Redis** | Buffer queue | Holds raw turns between captures |
| **Ollama** | Embeddings + Curation LLM | Runs locally, no API keys |
| **Python 3.10+** | Scripts | All components are Python |

### Ollama Models

- **Embeddings:** `snowflake-arctic-embed2` — 1024-dim vectors, solid semantic search
- **Curation:** `qwen2.5:7b` — Reads conversations, extracts structured gems
  - We tested 3b, 7b, and 14b. The 7b model curates *better* than 14b — more thorough metadata extraction, catches subtle details. 14b was faster but missed things.

---

## Setup

### 1. Infrastructure

Start Qdrant and Redis. Docker Compose example:

```yaml
# docker-compose.yml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_data:/qdrant/storage

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - ./redis_data:/data
```

```bash
docker compose up -d
```

### 2. Ollama Models

```bash
# Install Ollama if you haven't: https://ollama.com
# Pull required models:
ollama pull snowflake-arctic-embed2
ollama pull qwen2.5:7b
```

### 3. Install Memory V2

```bash
# Clone or copy the skill into your agent workspace
cd /path/to/your/agent/skills/memory-v2

# Run the installer
bash scripts/install.sh
```

The installer will:
1. Install Python dependencies (`qdrant-client`, `redis`, `requests`)
2. Create Qdrant collections with proper indexes
3. Install the `mem-capture` systemd service
4. Set up cron jobs for warm flush and nightly curation
5. Create convenience scripts

### 4. Configure

Edit the connection details at the top of each script if your infrastructure differs from defaults:

| Setting | Default | File(s) |
|---------|---------|---------|
| `REDIS_HOST` | `localhost` | `mem_capture.py`, `mem_warm.py` |
| `REDIS_PORT` | `6379` | `mem_capture.py`, `mem_warm.py` |
| `QDRANT_HOST` | `localhost` | All scripts |
| `QDRANT_PORT` | `6333` | All scripts |
| `OLLAMA_HOST` | `http://localhost:11434` | `embeddings.py`, `mem_curate.py` |
| `SESSION_DIR` | `~/.openclaw/agents/spark/sessions` | `mem_capture.py` |

> **Tip:** If everything runs on localhost, change all hosts to `127.0.0.1` or `localhost`.

---

## How It Works

### Stage 1: Capture (Real-Time)

**`mem_capture.py`** runs as a systemd service. It:

1. Watches OpenClaw session transcript files (JSONL format)
2. Polls every 30 seconds for new lines
3. Filters out noise (tool calls, heartbeats, HTML, short messages)
4. Deduplicates using content hashes (24h window)
5. Pushes clean conversation turns to a Redis list

```
Session transcript → mem-capture → Redis buffer
```

The capture service is smart about first runs — it indexes current file positions without ingesting old history, so you won't flood your memory with past conversations.

**Noise filtering:**
- Skips tool results, tool calls, and system metadata
- Ignores messages under 15 characters
- Filters base64 data, HTML, heartbeat acks
- Drops untrusted metadata blocks

### Stage 2: Warm (Every 30 Minutes)

**`mem_warm.py`** runs via cron every 30 minutes. It:

1. Atomically drains all turns from the Redis buffer
2. Groups turns by session ID
3. Chunks them into blocks of ~8 turns (max 3000 chars)
4. Embeds each chunk using `snowflake-arctic-embed2`
5. Stores to the `watts_warm` Qdrant collection

```
Redis buffer → chunk by session → embed → Qdrant watts_warm
```

Warm memories are immediately searchable. They auto-expire after 7 days (cleaned up by the curation step).

### Stage 3: Curate (Nightly)

**`mem_curate.py`** runs via cron at 2 AM daily. It:

1. Pulls all warm memories from yesterday
2. Builds a chronological transcript
3. Sends it to a local LLM (`qwen2.5:7b`) with a structured prompt
4. The LLM extracts "gems" — decisions, milestones, lessons, people info
5. Each gem gets embedded and stored in `watts_cold`
6. Old warm memories (>7 days) are cleaned up

```
Qdrant watts_warm → build transcript → LLM curation → Qdrant watts_cold
```

**What the LLM extracts:**
- Decisions: "Josh chose X over Y because Z"
- Technical changes: "Deployed X to Y"
- People info: Names, relationships, preferences
- Project milestones: Launches, completions, starts
- Lessons learned: "Don't do X because Y"
- Business events: Pricing, customers, legal

**What the LLM skips:**
- Casual banter, greetings, "thanks"
- Routine health checks
- Debugging steps (only keeps the solution)
- Repeated information

Each gem is structured:
```json
{
  "gem": "Chose DistilBERT over TinyBERT for V2 — 99.69% F1, zero false positives",
  "context": "A/B tested both architectures on the Volt red team suite",
  "date": "2026-02-10",
  "categories": ["decision", "technical"],
  "project": "fas-guardian",
  "people": ["Josh"],
  "importance": "high",
  "confidence": 0.95
}
```

### Stage 4: Recall (On Demand)

**`mem_recall.py`** searches across both warm and cold tiers simultaneously:

```bash
# Basic search
./recall "what did we decide about pricing"

# Filter by date
./recall "Guardian deployment" --date 2026-02-15

# Filter by category, project, or person
./recall "Bryan minecraft" --person Bryan
./recall "deployment" --project fas-guardian --tier cold

# JSON output (for programmatic use)
./recall "API changes" --json --limit 5

# Verbose mode (shows context, tags, project)
./recall "infrastructure changes" -v
```

Results are ranked by a combination of:
- **Semantic similarity** (cosine distance from query embedding)
- **Recency boost** (exponential decay, half-life of 30 days)
- **Importance bonus** (high > medium > low, cold tier only)

Output shows the tier, score, date, and content:
```
🔍 Searching: "pricing decision"
   Found: 5 results (3 curated 🧊, 2 recent 🔥)

  🧊 [0.892] [2026-02-08] [high] Chose Basic $19.99 / Pro $49.99 pricing
  🧊 [0.847] [2026-02-12] [medium] Added Enterprise custom tier for >500K scans
  🔥 [0.823] [2026-03-01] [discord] Discussion about adjusting Pro tier limits
  🧊 [0.801] [2026-02-05] [medium] "Don't feel greedy" philosophy for pricing
  🔥 [0.778] [2026-03-01] [main] Reviewed competitor pricing models
```

---

## Schedules

| Component | Schedule | What It Does |
|-----------|----------|-------------|
| `mem-capture` | Always running (systemd) | Watches transcripts → Redis buffer |
| `mem-warm` | `*/30 * * * *` (every 30 min) | Redis buffer → Qdrant warm |
| `mem-curate` | `0 9 * * *` (2 AM MST / 9 AM UTC) | Warm → LLM curation → Qdrant cold + cleanup |

Adjust the curation time to run during your quiet hours. It takes ~60-90 seconds on CPU.

---

## File Structure

```
memory-v2/
├── scripts/
│   ├── mem_capture.py      # Stage 1: Transcript watcher → Redis
│   ├── mem_warm.py         # Stage 2: Redis → Qdrant warm
│   ├── mem_curate.py       # Stage 3: Warm → LLM → Qdrant cold
│   ├── mem_recall.py       # Stage 4: Unified search
│   ├── embeddings.py       # Shared embedding utilities
│   ├── setup_collections.py # Qdrant collection setup
│   ├── curator_prompt.md   # LLM system prompt for curation
│   └── install.sh          # One-shot installer
├── mem-capture.service     # systemd unit file
├── recall                  # Convenience: search memory
├── warm-now                # Convenience: force warm flush
├── curate-now              # Convenience: force curation
├── mem-status              # Convenience: system status
└── README.md               # This file
```

---

## Qdrant Collections

### `watts_warm` — Mid-Term Memory
| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Chunked conversation text |
| `session_id` | keyword | Source session identifier |
| `channel` | keyword | discord, slack, main, cron |
| `date` | keyword | YYYY-MM-DD |
| `timestamp` | float | Unix timestamp (for range queries) |
| `timestamp_start` | string | ISO timestamp of first turn in chunk |
| `timestamp_end` | string | ISO timestamp of last turn in chunk |
| `turn_count` | integer | Number of turns in chunk |
| `content_hash` | string | MD5 hash for dedup |

### `watts_cold` — Long-Term Curated Gems
| Field | Type | Description |
|-------|------|-------------|
| `gem` | string | The core insight/fact |
| `context` | string | Why it matters |
| `date` | keyword | YYYY-MM-DD |
| `categories` | keyword[] | decision, technical, business, person, project, preference, infrastructure, lesson |
| `project` | keyword | Related project name |
| `people` | keyword[] | People mentioned |
| `importance` | keyword | high, medium, low |
| `confidence` | float | LLM's confidence in accuracy (0-1) |
| `timestamp` | float | Unix timestamp |
| `content_hash` | string | MD5 hash for dedup |

---

## Adapting for Other Frameworks

Memory V2 was built for OpenClaw, but the only framework-specific piece is **`mem_capture.py`** — specifically how it reads session transcripts.

To adapt for another agent framework:

1. **Replace `get_active_sessions()`** — Point it at wherever your framework writes conversation logs
2. **Replace `process_new_lines()`** — Parse your framework's log format instead of OpenClaw's JSONL
3. Everything else (warm, curate, recall) is framework-agnostic

The capture script expects each conversation turn to have:
- `role` (user, assistant)
- `text` (the message content)
- `timestamp` (ISO 8601)

If your framework provides those three fields, you're good.

---

## Convenience Commands

```bash
# Check system status (service, collections, buffer, logs)
./mem-status

# Search memory
./recall "what was the decision on X"
./recall "Bryan" --person Bryan --tier cold -v

# Force a warm flush right now
./warm-now

# Force curation for a specific date
./curate-now 2026-03-01

# Force curation for yesterday (default)
./curate-now
```

---

## Tuning

### Chunk Size
`CHUNK_SIZE = 8` in `mem_warm.py` — turns per chunk. Smaller chunks = more granular search but more storage. Larger chunks = more context per result but fuzzier matches. 8 is a sweet spot for conversational AI.

### Warm Retention
`WARM_RETENTION_DAYS = 7` in `mem_curate.py` — how long warm memories stick around before cleanup. Extend if your curation schedule is less frequent.

### Recency Decay
`RECENCY_HALF_LIFE_DAYS = 30` in `mem_recall.py` — how fast old results lose ranking priority. Lower = more recency-biased. Higher = more balanced.

### Curation Model
`CURATOR_MODEL = "qwen2.5:7b"` in `mem_curate.py` — the LLM used for overnight curation. We tested:
- **3b:** Fast but shallow — misses nuance
- **7b:** Best quality — thorough metadata, catches subtle details ✅
- **14b:** Faster than 7b on GPU but actually extracted fewer gems

### Embedding Model
`EMBED_MODEL = "snowflake-arctic-embed2"` in `embeddings.py` — 1024-dim vectors. Good balance of quality and speed. If you swap this, update `EMBEDDING_DIM` in `setup_collections.py` and recreate collections.

### Curator Prompt
`curator_prompt.md` — the system prompt that tells the LLM what to extract and what to skip. Customize this for your use case. The current prompt is tuned for a technical assistant that tracks decisions, infrastructure, people, and projects.

---

## Monitoring

Check the health of the system:

```bash
# Full status
./mem-status

# Logs
tail -f /tmp/mem-warm.log    # Warm flush logs
tail -f /tmp/mem-curate.log  # Curation logs
journalctl --user -u mem-capture -f  # Capture service logs

# Collection stats via Qdrant API
curl http://localhost:6333/collections/watts_warm
curl http://localhost:6333/collections/watts_cold
```

---

## How We Use It

This system powers [Watts](https://github.com/openclaw/openclaw) — an AI assistant running 24/7 on a home server. Watts manages infrastructure, writes code, monitors services, and maintains context across sessions.

Before Memory V2, every new session started from scratch. Now:
- Warm memories give instant recall of the last week's conversations
- Cold gems preserve decisions, lessons, and milestones permanently
- The LLM curator runs overnight, so morning sessions start with fresh long-term memory
- Total cost: $0/month (all local hardware)

---

## License

MIT — use it, fork it, make your agent remember things.
