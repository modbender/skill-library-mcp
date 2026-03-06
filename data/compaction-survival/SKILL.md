---
name: compaction-survival
version: 1.0.0
description: "Prevent context loss during LLM compaction via Write-Ahead Logging (WAL), Working Buffer, and automatic recovery. Three mechanisms that ensure critical state — decisions, preferences, values, paths — survives when the context window compresses. Always-active behavioral skill, not a one-time tool."
author: rustyorb
keywords: [memory, compaction, context, wal, write-ahead-log, session-state, persistence, survival, long-context, agent-memory]
metadata:
  openclaw:
    emoji: "🛡️"
---

# Compaction Survival System

Compaction destroys specifics: file paths, exact values, config details, reasoning chains. This skill ensures critical state survives.

**The problem:** When your context window fills up, OpenClaw compacts older messages into a summary. Summaries lose precision — exact numbers become "approximately," file paths vanish, decisions lose their rationale. Your agent wakes up dumber after every compaction.

**The fix:** Three mechanisms that capture critical state before compaction hits, and recover it after.

## Three Mechanisms

### 1. WAL Protocol (Write-Ahead Logging)

**On EVERY incoming message, scan for:**
- ✏️ Corrections — "It's X, not Y" / "Actually..."
- 📍 Proper nouns — names, places, companies, products
- 🎨 Preferences — styles, approaches, "I like/don't like"
- 📋 Decisions — "Let's do X" / "Go with Y"
- 📝 Draft changes — edits to active work
- 🔢 Specific values — numbers, dates, IDs, URLs, paths

**If ANY appear:**
1. **STOP** — do not compose response yet
2. **WRITE** — update `SESSION-STATE.md` with the detail
3. **THEN** — respond to the human

The trigger fires on the human's INPUT, not your memory. Write what they said, not what you think.

### 2. Working Buffer (Danger Zone)

**At 60% context utilization** (check via `session_status`):

1. Create/clear `memory/working-buffer.md`, write header:
   ```markdown
   # Working Buffer (Danger Zone)
   **Status:** ACTIVE
   **Started:** [timestamp]
   ```
2. **Every exchange after 60%:** append human's message + your response summary
3. Buffer is a file — it survives compaction
4. Leave buffer as-is until next 60% threshold in a new session

**Location:** `memory/working-buffer.md`

### 3. Compaction Recovery

**Auto-trigger when:**
- Session starts with `<summary>` tag in context
- You should know something but don't
- Human says "where were we?" / "continue" / "what were we doing?"

**Recovery steps (in order):**
1. Read `memory/working-buffer.md` — raw danger-zone exchanges
2. Read `SESSION-STATE.md` — active task state
3. Read today's + yesterday's `memory/YYYY-MM-DD.md`
4. Run `memory_search` if still missing context
5. Extract important context from buffer → update SESSION-STATE.md
6. Report: "Recovered context. Last task was X. Continuing."

**NEVER ask "what were we discussing?"** — the buffer has the answer.

## SESSION-STATE.md Format

```markdown
# Session State — Active Working Memory

## Current Task
[What we're actively working on]

## Key Details
- [Specific values, paths, configs captured via WAL]

## Decisions Made
- [Decisions with rationale]

## Pending
- [What's waiting/blocked]

## Last Updated
[timestamp]
```

Update this file frequently. It's your RAM — the only place specifics survive between compaction events.

## How It Works Together

```
                    ┌──────────────────────────┐
                    │    Human sends message    │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  WAL: Scan for specifics  │
                    │  Found? Write first.      │
                    └────────────┬─────────────┘
                                 │
               ┌─────────────────▼─────────────────┐
               │  Context > 60%? Buffer everything  │
               └─────────────────┬─────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │    Respond to human       │
                    └────────────┬─────────────┘
                                 │
                        ┌────────▼────────┐
                        │  COMPACTION HIT  │
                        └────────┬────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │  Recovery: Read buffer,   │
                    │  SESSION-STATE, daily log  │
                    │  → Full context restored   │
                    └──────────────────────────┘
```

## Integration

- Works alongside MEMORY.md (long-term) and memory/YYYY-MM-DD.md (daily logs)
- SESSION-STATE.md = working memory for current task
- Working buffer = emergency capture for the danger zone
- All three layers stack: WAL → Buffer → Recovery
- No dependencies. No API keys. Pure behavioral patterns.

## Why This Works

Most "memory" solutions try to store everything forever. That's the wrong problem. The real problem is **precision loss during compaction**. You don't need to remember everything — you need to remember the RIGHT things at the RIGHT time.

WAL catches specifics the moment they appear. The buffer captures the danger zone. Recovery restores context after the reset. Three layers, zero dependencies, zero data leakage.

---

*Built by [@rustyorb](https://github.com/rustyorb) + S1nthetta ⚡ — Battle-tested across 30+ compaction events.*
