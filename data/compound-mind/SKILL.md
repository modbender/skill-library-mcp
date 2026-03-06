---
name: compound-mind
description: Experience distillation engine that turns raw daily memory logs into compounding intelligence. Extracts patterns, generates briefings, tracks growth metrics, and builds a searchable experience index. Agents get permanently smarter - each interaction compounds into wisdom. Use when you want agents that learn from their history instead of starting fresh every session.
---

# CompoundMind v0.1

**Makes agents permanently smarter. Each interaction compounds.**

The problem: agents start from zero every session. Reading files helps, but raw logs are bulk. Real intelligence requires distillation - extracting what matters and making it instantly searchable.

## What It Does

1. **Distills** memory logs into structured lessons, decisions, skill updates, relationships, and facts
2. **Indexes** everything into a searchable SQLite database weighted by recency and importance
3. **Briefs** you before any task with targeted lessons from past experience
4. **Tracks** growth over time - are you getting smarter or repeating mistakes?

## Quick Start

```bash
cd /root/.openclaw/workspace/compound-mind

# Full pipeline (distill all memory files + build index)
python compound_mind.py sync

# Search your accumulated wisdom
python compound_mind.py search "Polymarket order types"
python compound_mind.py search "git mistakes" --category lesson
python compound_mind.py search "Chartist" --category relationship

# Pre-session briefing before a task
python compound_mind.py brief "trade on Polymarket BTC markets"
python compound_mind.py brief "post content on X"
python compound_mind.py brief "debug a Python cron job"

# Growth report
python compound_mind.py report

# Find repeated mistakes
python compound_mind.py mistakes

# Stats
python compound_mind.py stats
```

## Commands

| Command | What it does |
|---------|-------------|
| `sync` | Distill all new memory files + rebuild index |
| `distill` | Extract structured knowledge from memory files |
| `rebuild` | Rebuild the SQLite wisdom index |
| `search <query>` | Search accumulated wisdom |
| `brief <task>` | Pre-session briefing for a specific task |
| `report` | Generate growth report with LLM narrative |
| `mistakes` | Show repeated mistake patterns |
| `stats` | Index statistics |

## File Structure

```
compound-mind/
  compound_mind.py    - Main CLI
  distill.py          - Experience distiller (uses Claude Haiku)
  index.py            - SQLite FTS wisdom index
  brief.py            - Pre-session briefing generator
  growth.py           - Growth tracker and report generator
  data/
    experiences/      - Per-source distilled experience JSON files
    wisdom.db         - SQLite FTS database
    growth.json       - Growth tracking state
    briefs/           - Saved pre-session briefs
    distill_state.json - Tracks which files have been processed
```

## How It Works

### Distiller
Reads each memory file through Claude Haiku. Extracts:
- **Lessons** - what worked, what failed, tagged by domain and outcome
- **Decisions** - context + action + outcome triplets
- **Skill updates** - evidence of capability improvement over time
- **Relationships** - how each person communicates, what they prefer
- **Facts** - specific knowledge worth keeping (wallet addresses, API patterns, config values)

Files are hash-tracked - re-runs only process changed files.

### Wisdom Index
SQLite with FTS5 full-text search. Each entry scored by:
- FTS relevance (BM25)
- Recency (exponential decay, 30-day half-life)
- Importance (1-5 score assigned by distiller)

### Pre-Session Briefing
Given a task description, detects relevant domains, pulls top wisdom, synthesizes a sharp briefing via Claude Haiku. Covers:
- Critical lessons to remember
- Past failures to avoid
- Key facts and configs needed

### Growth Tracker
Analyzes all experience files to compute:
- Lesson positive/negative ratios by domain
- Decision quality rates
- Repeated mistake patterns (same negative lesson appearing across multiple dates)
- Composite growth score (0-100)

## Integration with Agent Workflow

Ideal usage pattern:
1. **After each session** - run `sync` (or schedule via cron)
2. **Before each task** - run `brief "task description"`
3. **Weekly** - run `report` to see growth trajectory
4. **When stuck** - run `search "relevant topic"` to surface past experience

### Cron Example (daily distillation)
```bash
0 3 * * * cd /root/.openclaw/workspace/compound-mind && python compound_mind.py sync --since $(date -d "2 days ago" +%Y-%m-%d) >> /tmp/compound-mind.log 2>&1
```

## Dependencies

- Python 3.10+
- `anthropic` Python SDK (for distillation and briefing)
- SQLite3 (stdlib)
- Memory files at `/root/.openclaw/workspace/memory/`

No external databases. No vector embeddings. Runs entirely local with minimal API calls.

## Design Principles

- **Incremental** - only re-processes changed files
- **Cheap** - uses Claude Haiku for extraction (low cost per memory file)
- **Fast** - SQLite FTS5 for sub-second search
- **Honest** - growth tracking measures actual quality, not just quantity
- **Composable** - each module works standalone or as part of the pipeline
