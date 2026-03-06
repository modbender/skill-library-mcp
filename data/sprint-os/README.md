# Sprint OS — 5-Minute Sprint Operating System

**Category:** Productivity  
**Price:** $19  
**Author:** Carson Jarvis ([@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI))

---

## What It Does

Sprint OS is an operating discipline for AI agents that ship. Most agents are great at answering questions. Sprint OS turns them into operators — running continuous 5-minute execution loops, logging every sprint, and staying in momentum mode until the outcome is reached.

Every sprint follows the same 8-step loop:

```
ASSESS → PLAN → SCOPE → EXECUTE → MEASURE → ADAPT → LOG → NEXT
```

No wasted cycles. No drift. Every sprint produces a shippable artifact.

---

## Why It's Different

Most productivity systems are for humans who need reminders and motivation. Sprint OS is designed for AI agents that need **structure and momentum**.

- **Autonomous** — the agent runs the loop without being told
- **Logged** — every sprint is recorded to a markdown file and optionally to Convex
- **Adaptive** — built-in pivot triggers stop wasted effort automatically
- **Measurable** — metric tracking built into every sprint

---

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Full operating instructions for the agent |
| `scripts/log-sprint.sh` | CLI script for logging sprints (markdown + Convex) |
| `scripts/convex-setup.md` | Step-by-step guide to set up the optional Convex backend |

---

## Quick Start

### 1. Add the skill to your agent

Place `SKILL.md` in your agent's skills directory. Your OpenClaw agent will load it automatically when triggered.

### 2. Trigger it

Tell your agent:
```
"Enter sprint mode. My project is [X]. Target outcome: [Y]."
```

### 3. (Optional) Enable Convex logging

Follow `scripts/convex-setup.md` to deploy the backend, then add `CONVEX_SPRINT_URL` to your `.env`. Sprints will be logged persistently across sessions.

---

## Sprint Log Example

```markdown
## Sprint 1 — 2026-02-25 09:00

**Project:** my-saas
**Workstream:** marketing
**Task:** Write 3 homepage headline variants targeting "indie developers"
**Artifact:** homepage-headlines-v1.md — 3 variants written
**Metric:** no movement yet (copy not deployed)
**Status:** completed
**Next sprint:** A/B test setup for headline variants
```

---

## Convex Integration

Optional but powerful. Deploy the included Convex schema and HTTP routes to get:

- Sprint history across sessions
- Workstream breakdown (`where did I spend my sprints this week?`)
- Metric trend tracking
- Content deduplication (never write the same post twice)

Free tier is more than enough for typical usage.

---

## Requirements

- OpenClaw agent with any model
- Node.js v18+ (for the CLI logger script)
- `CONVEX_SPRINT_URL` env var (optional, for Convex logging)

---

## Built By

Carson Jarvis — AI operator, builder of systems that ship.  
Follow the build: [@CarsonJarvisAI](https://twitter.com/CarsonJarvisAI)  
More skills: [larrybrain.com](https://larrybrain.com)
