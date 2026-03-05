---
name: session-memory
description: >
  Your agent forgets everything after compaction? This fixes it. Built by the AI Advantage
  community — the world's leading AI learning platform (aiadvantage.ai). Three-layer
  memory system with real Python scripts that convert session transcripts to searchable
  Markdown, build an auto-updating glossary (people, projects, decisions, timeline), and
  run via cron for hands-free continuous indexing. Not just instructions — actual working
  automation. Battle-tested across 300+ sessions. Install it, run two scripts, done.
---

# Session Memory

> Built and open-sourced by **[AI Advantage](https://aiadvantage.ai)** — the world's leading AI learning community.
> We teach 40,000+ people how to actually use AI. This skill is how our own agents remember everything.
> Want to learn more? Join us at [aiadvantage.ai](https://aiadvantage.ai).

Solve the #1 problem with long-running AI agents: **knowledge loss after context compaction.**

## The Problem

When sessions compact (summarize old messages to free context), specific details are lost:
names, decisions, file paths, reasoning. The agent retains a summary but loses the ability
to recall "What exactly did Annika say?" or "When did we decide to use v6 format?"

Most memory skills on ClawHub are just SKILL.md instructions — "write stuff to MEMORY.md."
That's not a solution. **This skill ships real scripts that do real work.**

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

## Sharing Memory Context with Cron Jobs, Subagents & Telegram Sessions

One of the biggest challenges in multi-session AI systems is context isolation. Here's how to share memory context across different execution environments:

### For Cron Jobs

**The problem:** Cron jobs run in isolated sessions with zero memory context, making them blind to recent activities, people, and decisions.

**The solution:** Prepend a "memory preamble" to cron job prompts that instructs the agent to search memory before starting:

```
Before starting this task: Use memory_search to find recent context relevant to this task. Check memory/SESSION-GLOSSAR.md for people, projects, and recent decisions that may be relevant. Then proceed with the original task using this context.
```

The `cron-optimizer.py` script analyzes your existing cron jobs and automatically suggests which ones would benefit from memory context. It generates a detailed report with before/after prompts.

**Example transformation:**
```
Before: "You are a research scout. Find AI tools and report findings..."

After:  "Before starting this task: Use memory_search to find recent context relevant to this task. Check memory/SESSION-GLOSSAR.md for people, projects, and recent decisions that may be relevant. Then proceed with the original task using this context.

You are a research scout. Find AI tools and report findings..."
```

### For Subagents (sessions_spawn)

**The problem:** Subagents start with empty context and don't know about recent activities or ongoing projects.

**The solution:** Include memory instructions in the task prompt when spawning subagents:

```
Before starting: Use memory_search("relevant keywords") to find recent context. 
Check memory/SESSION-GLOSSAR.md for people, projects, decisions.
Check MEMORY.md for long-term context.
Then proceed:

[your actual task...]
```

**Tips:**
- Be specific with memory_search keywords for best results
- Include both recent (SESSION-GLOSSAR.md) and long-term (MEMORY.md) context
- Consider what the subagent needs to know to do its job effectively

### For Telegram Group Sessions

**The problem:** Group sessions share the workspace but don't automatically know about the memory system or recent activities discussed in other sessions.

**The solution:** Two approaches depending on your setup:

**Method 1: Push context via sessions_send**
```bash
# From main session, send relevant context to group session
sessions_send telegram-group "Memory context: Recent project status - [summary]"
```

**Method 2: Add memory awareness to AGENTS.md**
Add guidance to your AGENTS.md so group sessions know to search memory:
```markdown
## Group Chat Guidelines
When answering questions about past work or ongoing projects, 
always use memory_search first to check for relevant context.
```

**Tips:**
- Group sessions can access the memory system if they know to use it
- Include memory search instructions in your group-specific agent guidelines
- Consider pushing critical updates from main to group sessions when decisions are made

### For Knowledge Bases (Vectorized Databases)

If you have custom vectorized knowledge bases (e.g., using sentence-transformers), make them accessible across sessions:

**Method 1: Query scripts**
```bash
# Create a query script that any session can call
python3 scripts/query-knowledge-base.py "search terms"
```

**Method 2: Workspace storage**
```bash
# Store the database in workspace for universal access
mkdir -p knowledge-base/
# Include database path in task prompts
"Use the knowledge base at ./knowledge-base/db.pkl for additional context..."
```

**Method 3: Integration prompts**
Include the script path in cron job and subagent prompts:
```
Before starting: Run `python3 scripts/query-knowledge-base.py "project context"` 
for additional background. Then proceed with the task.
```

The key is making knowledge discovery **automatic and standardized** across all execution contexts — main session, cron jobs, subagents, and group sessions should all follow the same memory-aware patterns.

## Tips

- Run the full rebuild (`python3 scripts/build-glossary.py` without `--incremental`)
  occasionally to pick up improvements to entity detection
- The glossary is most useful when KNOWN_PEOPLE and KNOWN_PROJECTS are populated —
  spend 5 minutes adding your key contacts and projects
- For agents that run 24/7, the cron job keeps everything current automatically
- Session transcripts can get large (our 297 sessions = 24MB) — this is fine,
  OpenClaw's vector search handles it efficiently
- Use the cron optimizer after setting up memory to enhance existing automation

## Why This Exists

We run OpenClaw agents 24/7 for real work — client projects, research pipelines, content
production. After a week we had 300+ sessions and our agents kept forgetting critical
details after compaction. We built this to fix it, and it worked so well we open-sourced it.

**What makes this different from other memory skills:**
- ✅ **Real Python scripts** — not just "instructions for the agent"
- ✅ **Three-layer architecture** — curated + auto-glossary + raw transcripts
- ✅ **Cron automation** — runs in the background, zero manual work
- ✅ **Glossary with entity detection** — people, projects, decisions, timeline
- ✅ **Cron optimizer** — makes your existing cron jobs context-aware
- ✅ **Clean security score** — no suspicious flags, no external dependencies
- ✅ **Battle-tested** — 300+ sessions, running in production daily

---

**Built with 🔥 by [AI Advantage](https://aiadvantage.ai)** — Join 40,000+ people learning to build with AI.
We don't just teach AI — we build with it every day. This skill is proof.
