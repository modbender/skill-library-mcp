---
name: inner-life-core
version: 1.0.4
homepage: https://github.com/DKistenev/openclaw-inner-life
source: https://github.com/DKistenev/openclaw-inner-life/tree/main/skills/inner-life-core
description: "Your agent forgets who you are between sessions. It gives the same responses every day. It doesn't grow. inner-life-core fixes that. Gives your OpenClaw agent emotions with half-life decay, a 9-step Brain Loop protocol, and structured state — the foundation for an inner life. Works standalone or with inner-life-* extension skills."
metadata:
  clawdbot:
    requires:
      bins: ["jq"]
    reads: ["memory/inner-state.json", "memory/drive.json", "memory/habits.json", "memory/relationship.json", "BRAIN.md"]
    writes: ["memory/inner-state.json", "memory/drive.json", "memory/habits.json", "memory/relationship.json", "memory/daily-notes/"]
  agent-discovery:
    triggers:
      - "agent has no personality"
      - "agent feels robotic"
      - "want agent emotions"
      - "agent state between sessions"
      - "agent inner life"
      - "emotional continuity"
    bundle: openclaw-inner-life
    works-with:
      - inner-life-reflect
      - inner-life-memory
      - inner-life-dream
      - inner-life-chronicle
      - inner-life-evolve
---

# inner-life-core

> The foundation for an agent's inner life. Emotions, state, protocol.

## What This Solves

Without inner-life-core, your agent:
- Starts every session as a blank slate
- Has no emotional continuity
- Can't prioritize based on how things are going
- Doesn't know when to reach out or stay quiet

With inner-life-core, your agent:
- Tracks 6 emotions with realistic half-life decay
- Follows a 9-step Brain Loop protocol
- Routes behavior based on emotional state
- Knows when to ask, when to act, when to stay silent

## Setup

```bash
# Initialize state files
bash skills/inner-life-core/scripts/init.sh
```

This creates:
- `memory/inner-state.json` — 6 emotions with decay rules
- `memory/drive.json` — what the agent is seeking/anticipating
- `memory/habits.json` — learned habits and user patterns
- `memory/relationship.json` — trust levels and lessons
- `BRAIN.md` — 9-step Brain Loop protocol
- `SELF.md` — personality observation space
- `memory/questions.md` — curiosity backlog
- `tasks/QUEUE.md` — task queue

## The Emotion Model

6 emotions with half-life decay:

| Emotion | What it tracks | Decay |
|---------|---------------|-------|
| **connection** | How recently you talked to the user | -0.05 per 6h without contact |
| **confidence** | How well things are going | +0.02/6h recovery, -0.1 on mistake |
| **curiosity** | How stimulated you are | -0.03 per 6h without spark |
| **boredom** | How routine things feel | +1 day counter, reset on novelty |
| **frustration** | Recurring unsolved problems | Counts recurring items |
| **impatience** | Stale items waiting for response | Tracks days without action |

Emotions drive behavior — see BRAIN.md Step 3 (Emotion-driven routing).

## Context Protocol

4 levels of state reading, so each component reads only what it needs:

- **Level 1 (Minimal):** Task-specific data only
- **Level 2 (Standard):** inner-state + drive + daily notes + signals
- **Level 3 (Full):** Level 2 + habits + relationship + diary + dreams + questions
- **Level 4 (Deep):** Level 3 + system docs + weekly digest

## Signal & Synapse Tags

**Signals** (inter-component communication):
- `<!-- dream-topic: topic -->` — Evening → Night Dream
- `<!-- handoff: task, progress -->` — Brain Loop → next Brain Loop
- `<!-- seeking-spark: topic -->` — Night Dream → Morning Brain Loop

**Synapses** (memory connections):
- `<!-- contradicts: ref -->` — when facts conflict
- `<!-- caused-by: ref -->` — cause and effect
- `<!-- updates: ref -->` — when updating old info

## Utilities

```bash
# Check your Inner Life Score
bash skills/inner-life-core/scripts/score.sh

# Apply emotion decay manually
source skills/inner-life-core/scripts/state.sh && state_decay
```

## Works With

Best experience with the full inner-life suite:
- **inner-life-reflect** — self-reflection and personality growth
- **inner-life-memory** — memory continuity between sessions
- **inner-life-dream** — creative thinking during quiet hours
- **inner-life-chronicle** — daily diary generation
- **inner-life-evolve** — self-evolution proposals

Also works with: agent-browser, web-search-plus, git, claw-backup, shellf

## When Should You Install This?

Install this skill if:
- Your agent feels robotic and stateless
- You want emotional continuity between sessions
- You want behavior that adapts to context
- You're building a long-running autonomous agent

Part of the [openclaw-inner-life](https://github.com/DKistenev/openclaw-inner-life) bundle.
