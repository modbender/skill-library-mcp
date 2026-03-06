---
name: dory-memory
description: File-based memory system for AI agents that forget between sessions. Implements the "Dory-Proof" pattern for continuity across context resets. Use when setting up agent memory, building workspace structure, implementing task tracking, or preventing context-loss errors. Triggers on "memory system", "remember between sessions", "Dory pattern", "agent continuity", or "workspace setup".
---

# Dory-Proof Memory System

AI agents forget everything between sessions. This skill implements a file-based memory system that survives context resets.

## Core Principle

**Text > Brain.** Write everything down. Files are memory. The agent only "remembers" what's on disk.

## The Dory-Proof Pattern (Critical)

When the user gives a task:
1. **IMMEDIATELY** write their EXACT WORDS to `state/ACTIVE.md`
2. Then interpret what it means
3. Then do the work
4. Mark complete when done

**Why:** Paraphrasing introduces drift. Exact words preserve intent across context flushes.

## Workspace Structure

```
workspace/
├── AGENTS.md        # Operating rules (system file, don't rename)
├── SOUL.md          # Identity + personality
├── USER.md          # About the human
├── MEMORY.md        # Curated long-term memory (<10KB)
├── LESSONS.md       # "Never again" safety rules
├── TOOLS.md         # Tool-specific notes
│
├── state/           # Active state (check every session)
│   ├── ACTIVE.md    # Current task (exact user words)
│   ├── HOLD.md      # Blocked items (check before acting!)
│   ├── STAGING.md   # Drafts awaiting approval
│   └── DECISIONS.md # Recent choices with timestamps
│
├── memory/          # Historical
│   ├── YYYY-MM-DD.md
│   ├── recent-work.md
│   └── archive/
│
└── ops/             # Operational
    └── WORKSPACE-INDEX.md
```

## Boot Sequence (Every Session)

1. Read `state/HOLD.md` — what's BLOCKED
2. Read `state/ACTIVE.md` — current task
3. Read `state/DECISIONS.md` — recent choices
4. Read `memory/recent-work.md` — last 48 hours
5. Read `MEMORY.md` — long-term (main session only)

Output status line after boot:
```
📋 Boot: ACTIVE=[task] | HOLD=[n] items | STAGING=[n] drafts
```

## State File Formats

### state/ACTIVE.md
```markdown
## Current Instruction
**User said:** "[exact quote]"
**Interpretation:** [what you think it means]
**Status:**
- [ ] Step 1
- [ ] Step 2
```

### state/HOLD.md
```markdown
[YYYY-MM-DD HH:MM | session] Item — reason blocked
```
**ALL agents must check before acting on anything that looks ready.**

### state/DECISIONS.md
```markdown
[YYYY-MM-DD HH:MM | session] Decision made
```

## Conflict Resolution

When files conflict, priority (highest first):
1. **state/HOLD.md** — blocks override all
2. **state/ACTIVE.md** — current instruction
3. **state/DECISIONS.md** — recent choices
4. **AGENTS.md** — general rules

## Memory Scoring (Before Saving to MEMORY.md)

Score on 4 axes (0–3 each):

| Axis | 0 | 1 | 2 | 3 |
|------|---|---|---|---|
| Longevity | Gone tomorrow | Weeks | Months | Years+ |
| Reuse | One-off | Occasional | Frequent | Every session |
| Impact | Trivial | Nice to know | Changes outputs | Changes decisions |
| Uniqueness | Obvious | Slightly helpful | Hard to rederive | Impossible without |

**Save if:** Total ≥ 8, OR any axis = 3 AND total ≥ 6.

## Quick Setup

Copy template files from `assets/templates/` to your workspace:
```bash
cp -r skills/dory-memory/assets/templates/* ~/.openclaw/workspace/
```

Then customize SOUL.md and USER.md for your agent.

## References

- `references/IMPLEMENTATION-GUIDE.md` — Full setup walkthrough
- `references/ANTI-PATTERNS.md` — Common mistakes to avoid
