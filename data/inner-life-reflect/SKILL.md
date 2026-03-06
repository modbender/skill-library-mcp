---
name: inner-life-reflect
version: 1.0.4
homepage: https://github.com/DKistenev/openclaw-inner-life
source: https://github.com/DKistenev/openclaw-inner-life/tree/main/skills/inner-life-reflect
description: "Your agent repeats the same patterns without learning. inner-life-reflect adds self-reflection with trigger detection and quality gates — your agent observes its own behavior, notices shifts, and evolves its personality over time through SELF.md."
metadata:
  clawdbot:
    requires:
      bins: ["jq"]
    reads: ["memory/inner-state.json", "memory/habits.json", "memory/drive.json", "memory/diary/"]
    writes: ["memory/SELF.md", "memory/habits.json"]
  agent-discovery:
    triggers:
      - "agent doesn't learn from mistakes"
      - "agent personality development"
      - "self-reflection for agent"
      - "agent self-awareness"
      - "agent keeps making same mistakes"
    bundle: openclaw-inner-life
    works-with:
      - inner-life-core
      - inner-life-memory
      - inner-life-chronicle
---

# inner-life-reflect

> Self-reflection that actually works. No forced journaling, no filler.

Requires: **inner-life-core**

## Prerequisites Check

Before using this skill, verify that inner-life-core has been initialized:

1. Check that `memory/inner-state.json` exists
2. Check that `memory/habits.json` exists

If either is missing, tell the user: *"inner-life-core is not initialized. Install it with `clawhub install inner-life-core` and run `bash skills/inner-life-core/scripts/init.sh`."* Do not proceed without these files.

## What This Solves

Without reflection, agents accumulate experience but never learn from it. They make the same mistakes, miss the same patterns, and their personality stays frozen.

inner-life-reflect adds a trigger-based reflection system with quality gates. Your agent writes to SELF.md only when something meaningful happens — not on a schedule, not as routine filler.

## Core Principle

- **SOUL.md** = who you are (foundation, change only with user approval)
- **SELF.md** = who you're becoming (living observations)
- **Schedule the check, not the content** — checks can be periodic; entries must be genuine

## Triggers

### Hard Triggers (write now)

Create/update SELF.md entry when:
- You were corrected on reasoning style or behavior pattern
- You noticed a repeated bias or avoidance pattern (>=2 times)
- You made a decision that clearly reflects preference or aversion
- You caught a blind spot that changed your behavior

### Soft Triggers (consider writing)

- Subtle tendency shift detected
- New tone pattern in interactions
- Mild preference signal from user

If only soft triggers exist and quality is low: skip entry, update state only.

## Quality Gate

Before writing to SELF.md, pass ALL 4 checks:

1. **Specificity** — concrete behavior, not generic statement
2. **Evidence** — based on recent sessions, not vibes
3. **Novelty** — not a duplicate of last 3 entries
4. **Usefulness** — could influence future behavior

If any check fails: no SELF entry, just state update.

## SELF.md Format

Short dated entries organized by section:

```markdown
## Tendencies
- [2026-03-01] I default to verbose explanations when a short answer would suffice

## Preferences
- [2026-03-01] I prefer structured approaches over exploratory ones

## Blind Spots
- [2026-02-28] I underestimate how long file operations take

## Evolution
- [2026-03-01] Shifted from always asking permission to acting within trust bounds
```

## Review Cadence

### Micro check (every 3 hours)
Scan for hard/soft triggers. Does NOT auto-write — only decides if reflection is due.

### Meso review (weekly)
- Read last 7 daily logs + SELF.md
- Detect recurring shifts
- Update sections only if real change occurred

### Macro review (monthly)
- Write 3-5 sentence evolution narrative
- Compare against previous month
- Falsifiability check: if entries are stale/generic for a month, adjust trigger thresholds

## State Integration

**Reads:** inner-state.json, habits.json, drive.json, diary (latest)

**Writes:** SELF.md, habits.json (when patterns crystallize into habits)

**During weekly review:**
- Read `habits.json` → patterns with `strength >= 3` are tendencies
- Read `drive.json` → seeking active > 2 weeks are interests
- Read diary for the week → sustained observations become entries

## Boundaries

- SELF.md is autonomous observation space
- SOUL.md is never auto-modified
- If SELF suggests SOUL changes: propose to user, do not auto-edit

## When Should You Install This?

Install this skill if:
- Your agent keeps making the same mistakes
- You want your agent to develop a personality over time
- Your agent's self-model is stale or nonexistent
- You want quality-gated reflection, not forced journaling

Part of the [openclaw-inner-life](https://github.com/DKistenev/openclaw-inner-life) bundle.
Requires: inner-life-core
