---
name: session-memory
description: >
  Persistent session memory system that prevents knowledge loss after context compaction.
  Converts session transcripts to searchable Markdown, builds an auto-updating glossary
  index (people, projects, decisions, timeline), and sets up cron jobs for continuous
  indexing. Use when: (1) the agent forgets details after compaction, (2) you want to
  recall who was discussed or what was decided in past sessions, (3) setting up long-term
  memory for a new OpenClaw agent, (4) the user asks about memory loss, session recall,
  or knowledge persistence across sessions.
---

# Session Memory

Solve the #1 problem with long-running AI agents: **knowledge loss after context compaction.**

## The Problem

When sessions compact (summarize old messages to free context), specific details are lost:
names, decisions, file paths, reasoning. The agent retains a summary but loses the ability
to recall "What exactly did Annika say?" or "When did we decide to use v6 format?"

## The Solution: Three-Layer Memory Architecture

```
Layer 1: MEMORY.md          — Curated long-term memory (human-edited)
Layer 2: SESSION-GLOSSAR.md — Auto-generated structured index (people/projects/decisions/timeline)
Layer 3: memory/sessions/   — Full session transcripts as searchable Markdown
```

All three layers live under `memory/` and are automatically vectorized by OpenClaw's
memory search, creating a navigational hierarchy: glossary finds the right session,
session provides the details.

## Setup (run once)

### Step 1: Convert existing sessions to Markdown

```bash
python3 scripts/session-to-memory.py
```

This scans all JSONL session logs in `~/.openclaw/agents/*/sessions/` and converts
them to `memory/sessions/session-YYYY-MM-DD-HHMM-*.md`. Truncates long assistant
responses to 2KB, skips system messages, tracks state to avoid re-processing.

Options:
- `--new` — Only convert sessions not yet processed (for incremental runs)
- `--agent main` — Specify agent ID (default: main)

### Step 2: Build the glossary

```bash
python3 scripts/build-glossary.py
```

Scans all session transcripts and builds `memory/SESSION-GLOSSAR.md` with:
- **People** — Who was mentioned, in how many sessions, date ranges
- **Projects** — Which projects discussed, with relevant topic tags
- **Topics** — Categorized themes (Email Drafts, Website Build, Security, etc.)
- **Timeline** — Per-day summary (session count, people, topics)
- **Decisions** — Extracted decision-like statements with dates

Options:
- `--incremental` — Only process new sessions (uses cached scan state)

### Step 3: Set up cron jobs for auto-updates

Create two cron jobs (use a cheap model like Gemini Flash):

**Job 1: Session sync + glossary rebuild (every 4-6 hours)**
```
Task: Run `python3 scripts/session-to-memory.py --new` then
      `python3 scripts/build-glossary.py --incremental`.
      Report how many new sessions were converted and indexed.
```

**Optional Job 2: Pre-compaction memory flush check**
Already built into AGENTS.md by default — just ensure the agent writes to
`memory/YYYY-MM-DD.md` before each compaction.

## Customizing Entity Detection

Edit `scripts/build-glossary.py` to add your own known people and projects:

```python
KNOWN_PEOPLE = {
    "alice": "Alice Smith — Project Manager",
    "bob": "Bob Jones — CTO",
}

KNOWN_PROJECTS = {
    "website-redesign": "Website Redesign — Q1 Initiative",
    "api-migration": "API Migration — v2 to v3",
}
```

The glossary also detects topics via regex patterns. Add new patterns in the
`topic_patterns` dict for your domain.

## How It Works With memory_search

Once set up, `memory_search("Alice project decision")` will find:
1. The glossary entry for Alice (which sessions she appears in)
2. The actual session transcript where the decision was discussed
3. Any MEMORY.md entry about Alice

This gives the agent a **navigation layer** (glossary) plus **detail access**
(transcripts) — much better than either alone.

## File Structure After Setup

```
memory/
├── MEMORY.md                    — Curated (you maintain this)
├── SESSION-GLOSSAR.md           — Auto-generated index
├── YYYY-MM-DD.md                — Daily notes
├── .glossary-state.json         — Glossary builder state
├── .glossary-scans.json         — Cached scan results
└── sessions/
    ├── .state.json              — Converter state
    ├── session-2026-01-15-0830-abc123.md
    ├── session-2026-01-15-1200-def456.md
    └── ...
```

## Cron Memory Optimizer

Cron jobs run in isolated sessions with zero memory context. The optimizer analyzes your cron jobs and suggests memory-enhanced versions:

```bash
python3 scripts/cron-optimizer.py
```

This scans `~/.openclaw/cron/jobs.json`, identifies jobs that would benefit from memory context, and generates `memory/cron-optimization-report.md` with before/after prompts and implementation guidance.

**Example optimization:**
```
Original: "Run daily research scout..."
Enhanced: "Before starting: Use memory_search to find recent context about research activities. Check memory/SESSION-GLOSSAR.md for relevant people, projects, and recent decisions. Then proceed with the original task using this context.

Run daily research scout..."
```

The script is conservative (suggests only, never auto-modifies) and skips monitoring jobs that don't need context.

## Tips

- Run the full rebuild (`python3 scripts/build-glossary.py` without `--incremental`)
  occasionally to pick up improvements to entity detection
- The glossary is most useful when KNOWN_PEOPLE and KNOWN_PROJECTS are populated —
  spend 5 minutes adding your key contacts and projects
- For agents that run 24/7, the cron job keeps everything current automatically
- Session transcripts can get large (our 297 sessions = 24MB) — this is fine,
  OpenClaw's vector search handles it efficiently
- Use the cron optimizer after setting up memory to enhance existing automation
