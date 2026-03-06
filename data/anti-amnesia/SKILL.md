---
name: anti-amnesia
description: "Complete anti-amnesia system for OpenClaw agents. Prevents context loss across sessions with structured state files, automatic session saving, health monitoring, and decision tracking. Your agent wakes up knowing everything — every time."
version: 1.0.0
---

# Anti-Amnesia Agent System 🧠🛡️

Your OpenClaw agent forgets everything between sessions. This skill fixes that.

## What It Does

1. **STATE.md** — Single source of truth. Active projects, iron decisions, open issues. Read first on every wake-up.
2. **Session Memory Hook** — Automatically saves full conversation when you `/new` or `/reset`. Zero manual work.
3. **Daily Journals** — `memory/YYYY-MM-DD.md` files capture everything that happens each day.
4. **MEMORY.md** — Long-term curated memory. The distilled wisdom, not raw logs.
5. **Heartbeat Health Checks** — Every wake-up: verify crons, check processes, validate state consistency.
6. **Decision Capture** — Decisions made in conversation get written to files immediately. No "mental notes."

## Setup

### Step 1: Enable Session Memory Hook

Add to your `~/.openclaw/openclaw.json` under hooks:

```json
{
  "hooks": {
    "session-memory": {
      "enabled": true,
      "messages": 9999,
      "path": "memory/"
    }
  }
}
```

### Step 2: Create Core Files

Copy the templates from this skill's `templates/` folder to your workspace:

```
templates/STATE.md      → workspace/STATE.md
templates/HEARTBEAT.md  → workspace/HEARTBEAT.md
```

Edit STATE.md with your actual projects and decisions.

### Step 3: Update AGENTS.md

Add to your AGENTS.md session start protocol:

```markdown
## Every Session — Mandatory
1. Read `STATE.md` — current world state
2. Read `memory/YYYY-MM-DD.md` (today) — if missing, create it
3. Read `MEMORY.md` — long-term memory
```

### Step 4: Create memory directory

```bash
mkdir -p workspace/memory
```

## The Anti-Amnesia Protocol

### On Every Session Start:
```
STATE.md → What's happening now
memory/today.md → What happened today
MEMORY.md → What happened before
```

### On Every Heartbeat:
```
1. Read STATE.md
2. Check cron health (consecutiveErrors > 0 → alert)
3. Check critical processes (are they running?)
4. Read income-tracker.md (if night shift)
5. Write everything to memory/today.md
```

### On Every Decision:
```
Decision made in chat → Write to file IMMEDIATELY
No "I'll remember that" — files only
```

## Key Principle

> **If it's not in a file, it didn't happen.**

Mental notes don't survive session restarts. Files do. Every decision, every status change, every important conversation — write it down in the same response.

## Files Reference

| File | Purpose | When to Read |
|------|---------|-------------|
| `STATE.md` | Current world state | Every session + heartbeat |
| `MEMORY.md` | Long-term curated memory | Every session |
| `memory/YYYY-MM-DD.md` | Daily journal | Every session + heartbeat |
| `HEARTBEAT.md` | Wake-up protocol | Every heartbeat |
| `AGENTS.md` | Agent behavior rules | On first load |

## Why This Works

Most OpenClaw agents lose context because they rely on conversation history alone. When context resets, everything is gone.

This system creates **external persistent memory** — files that survive any reset. Your agent reads them on startup and knows everything within 30 seconds.

Tested in production: 24/7 autonomous trading system, 20+ cron jobs, multi-agent coordination — zero context loss over weeks of operation.
