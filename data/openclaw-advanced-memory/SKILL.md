---
name: OpenClaw Advanced Memory
description: Three-tier AI agent memory system — real-time capture, vector
  search, and LLM-curated long-term recall.
---

# OpenClaw Advanced Memory

Three-tier AI agent memory system — real-time capture, vector search, and LLM-curated long-term recall.

## What It Does

Gives your OpenClaw agent persistent, searchable memory that survives across sessions:

- **HOT tier** — Redis buffer captures conversation turns in real-time (every 30s)
- **WARM tier** — Qdrant vector store with chunked, embedded conversations (searchable, 7-day retention)
- **COLD tier** — LLM-curated "gems" extracted nightly (decisions, lessons, milestones — stored forever)

## Requirements

- **Qdrant** — vector database (Docker recommended)
- **Redis** — buffer queue (Docker recommended)
- **Ollama** — local embeddings (`snowflake-arctic-embed2`) + curation LLM (`qwen2.5:7b`)
- **Python 3.10+** with `qdrant-client`, `redis`, `requests`

No cloud APIs. No subscriptions. Runs entirely on your own hardware.

## Setup

```bash
# 1. Start Qdrant + Redis (Docker)
docker compose up -d

# 2. Pull Ollama models
ollama pull snowflake-arctic-embed2
ollama pull qwen2.5:7b

# 3. Run the installer
bash scripts/install.sh
```

The installer sets up Qdrant collections, installs a systemd capture service, and configures cron jobs.

Edit connection hosts at the top of each script if your infra isn't on localhost.

## Usage

```bash
# Search your memory
./recall "what did we decide about pricing"
./recall "deployment" --project myproject --tier cold -v

# Check system status
./mem-status

# Force a warm flush or curation run
./warm-now
./curate-now 2026-03-01
```

## Schedules

| Component | Schedule | What It Does |
|-----------|----------|-------------|
| `mem-capture` | Always running (systemd) | Watches transcripts → Redis |
| `mem-warm` | Every 30 min (cron) | Redis → Qdrant warm |
| `mem-curate` | Nightly 2 AM (cron) | Warm → LLM curation → Qdrant cold |

## How Curation Works

Every night, a local LLM (`qwen2.5:7b` via Ollama) reads the day's conversations and extracts structured gems:

```json
{
  "gem": "Chose DistilBERT over TinyBERT — 99.69% F1, zero false positives",
  "context": "A/B tested both architectures on red team suite",
  "categories": ["decision", "technical"],
  "project": "guardian",
  "importance": "high"
}
```

Only decisions, milestones, lessons, and people info make the cut. Casual banter and debugging noise get filtered out.

## Links

- **GitHub:** https://github.com/jtil4201/openclaw-advanced-memory
- **Full docs:** See README.md in the repo for architecture diagrams, tuning guide, and adaptation notes
