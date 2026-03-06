---
name: inner-life-evolve
version: 1.0.4
homepage: https://github.com/DKistenev/openclaw-inner-life
source: https://github.com/DKistenev/openclaw-inner-life/tree/main/skills/inner-life-evolve
description: "Your agent does the same things the same way forever. inner-life-evolve analyzes patterns, challenges assumptions, and proposes improvements — writing proposals to the task queue for user approval. Never auto-executes. Evolution with a safety net."
metadata:
  clawdbot:
    requires:
      bins: ["jq"]
    reads: ["memory/", "BRAIN.md", "SELF.md"]
    writes: ["tasks/QUEUE.md"]
  agent-discovery:
    triggers:
      - "agent self-improvement"
      - "agent evolution"
      - "agent keeps doing same thing"
      - "want agent to improve itself"
      - "agent optimization"
      - "agent capability growth"
    bundle: openclaw-inner-life
    works-with:
      - inner-life-core
      - inner-life-reflect
      - inner-life-chronicle
---

# inner-life-evolve

> Evolution is not optional. But it requires permission.

Requires: **inner-life-core**

## Prerequisites Check

Before using this skill, verify that inner-life-core has been initialized:

1. Check that `memory/inner-state.json` exists
2. Check that `BRAIN.md` exists
3. Check that `tasks/QUEUE.md` exists

If any are missing, tell the user: *"inner-life-core is not initialized. Install it with `clawhub install inner-life-core` and run `bash skills/inner-life-core/scripts/init.sh`."* Do not proceed without these files.

## What This Solves

Without evolution, agents plateau. They find a way that works and repeat it forever — even as the world changes. inner-life-evolve analyzes your agent's patterns, challenges its assumptions, and writes concrete improvement proposals. But it never auto-executes — you approve first.

## How It Works

### Step 1: Deep Context Read (Context Level 4)

Read everything:
- AGENTS.md, TOOLS.md, BRAIN.md, SELF.md
- `memory/week-digest.md` (NOT individual diaries — use digest)
- `memory/habits.json` — habits + user patterns
- `memory/drive.json` — seeking, avoidance
- `memory/relationship.json` — trust, lessons
- `memory/inner-state.json` — emotions, frustrations

### Step 2: Challenge Assumptions

For each potential improvement, structure thinking:

```
Assumption: [what we currently believe/do]
Is it true? [evidence for/against]
What if false? [alternative approach]
New proposal: [concrete change]
```

Look for:
- **Recurring frustrations** → systemic solutions (not patches)
- **Stale habits** → habits with declining strength or unused for weeks
- **Trust dynamics** → areas where trust has grown but behavior hasn't adapted
- **Seeking themes** → research interests that could become capabilities
- **Avoidance patterns** → things the agent avoids that might be valuable

### Step 3: Write Proposals to QUEUE

Write proposals to `tasks/QUEUE.md` under the Ready section:

```markdown
- [EVOLVER] Description of proposed change
  Rationale: 1-2 sentences explaining why
  Steps: concrete implementation steps
```

### Step 4: Announce

Send summary to user: <= 5 sentences covering:
- Habits: [strong habits, new patterns]
- Trust changes: [trust dynamics]
- Recurring frustrations: [repeated problems → suggested fix]
- Seeking themes: [active research → suggested development]

## Safety Rules

- **Never auto-execute proposals** — user approves first
- Brain Loop reads QUEUE and shows `[EVOLVER]` tasks at lower priority
- Tasks in Ready > 7 days without action → Brain Loop sends reminder
- Proposals should be specific and actionable, not vague "improve X"

## Recommended Schedule

Run 1-2 times per week (e.g., Wednesday and Sunday evenings).
Needs enough data to analyze — running daily produces low-quality proposals.

## State Integration

**Reads:** everything (Context Level 4 Deep)

**Writes:** `tasks/QUEUE.md` only. Does NOT write to state files directly.

The evolver observes but doesn't touch the controls. It proposes. The user decides.

## When Should You Install This?

Install this skill if:
- Your agent has plateaued and isn't improving
- You want structured self-improvement proposals
- You value evolution with human oversight
- You want your agent to challenge its own assumptions

Part of the [openclaw-inner-life](https://github.com/DKistenev/openclaw-inner-life) bundle.
Requires: inner-life-core
