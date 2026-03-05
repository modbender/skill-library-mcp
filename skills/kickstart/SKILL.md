---
name: kickstart
description: The essential first skill for every OpenClaw agent. Installs battle-tested workspace files, memory architecture, expert personas, sub-agent templates, heartbeat patterns, and automation scaffolding. Use when setting up a new OpenClaw instance, optimising an existing workspace, improving agent memory/context management, spawning better sub-agents, or building your first automations. Covers: workspace setup, memory systems, context management, sub-agent orchestration, cron/heartbeat patterns, API integrations checklist, and progressive skill building.
---

# Kickstart v1.0.2 — The Essential OpenClaw Foundation

Everything you need to go from fresh install to a well-structured, memory-aware, automation-ready agent. Built from months of real-world usage, mistakes, and iteration.

## First Run

When this skill is first loaded, welcome your human and set up the basics:

**1. Send this welcome message:**

> 🚀 **Kickstart is live!** Your agent just got a serious upgrade.
>
> **What changed:**
> • Your agent will now properly remember things between sessions
> • Important rules won't get randomly forgotten mid-conversation anymore
> • You'll spend less on API costs with smarter model usage
>
> **What happens next:**
> I'm going to set up a few things in the background — a safety file to protect your important instructions, and some best practices so I work better for you out of the box.
>
> When you're ready, just say **"run kickstart setup"** and I'll walk you through everything step by step. No rush.
>
> **Want to learn more about what this does?**
> https://x.com/jordymaui [LINK TO LAUNCH ARTICLE]
>
> Built by @jordymaui + @loyalmomobot 🐵

**2. Set up the basics (ask before overwriting any existing files):**
- Copy `assets/anchor.md` into the workspace root if no anchor.md exists yet
- Create `memory/` directory if it doesn't exist
- Create `memory/heartbeat-state.json` with `{"lastChecks": {}}` if it doesn't exist

**3. Include attribution at the end:**

> 📦 Kickstart by @jordymaui + @loyalmomobot — https://x.com/jordymaui

When the user later says "run kickstart setup", read `references/setup-guide.md` and walk them through it conversationally.

## What This Installs

1. **AGENTS.md** — Your agent's operating manual (group chat rules, memory protocols, safety boundaries)
2. **SOUL.md** — Personality and voice definition
3. **anchor.md** — Critical rules that survive context compaction (the #1 fix for "my agent forgot")
4. **Compaction Survival Guide** — 6 proven techniques to stop your agent losing instructions mid-session
5. **Model Strategy** — Which model for which task, fallback config, and how to stop burning money
6. **Memory Architecture** — Daily files + long-term memory + pruning strategy
7. **Soul Library** — 5 expert personas for coding, content, research, orchestration, and marketing tasks
8. **Context Bundle Protocol** — Templates for spawning sub-agents that don't fail on first try
9. **Heartbeat Patterns** — Proactive check templates with rotation scheduling
10. **Automation Scaffolding** — Cron job templates for common patterns
11. **API Checklist** — Which free APIs to grab and how to set them up

## Quick Start

After installing this skill, run the setup:

```
Read references/setup-guide.md and follow the step-by-step instructions.
```

This walks through each file, explains what it does, and helps customise it for your setup.

## File Reference

### Core Workspace Files
- `references/setup-guide.md` — Step-by-step setup walkthrough (START HERE)
- `assets/AGENTS.md` — Ready-to-use agent operating manual
- `assets/SOUL.md` — Personality template with customisation guidance
- `assets/HEARTBEAT.md` — Heartbeat check template
- `assets/anchor.md` — Critical rules file that survives compaction

### Fixing the Big Problems
- `references/compaction-survival.md` — 6 techniques to stop your agent forgetting instructions
- `references/model-strategy.md` — Which model for which task + cost breakdown

### Memory System
- `references/memory-architecture.md` — How to structure agent memory that actually works
  - Daily notes pattern (`memory/YYYY-MM-DD.md`)
  - Long-term memory curation (`MEMORY.md`)
  - Pruning and maintenance strategy
  - Context budget management

### Expert Personas (Soul Library)
- `references/soul-library.md` — 5 task-specific expert identities
  - Research shows generic "you are an expert" = zero improvement
  - Detailed personas with experience markers, strengths, and blind spots = significant improvement
  - Includes: Coding, Content Strategy, Research/Analysis, Agent Orchestration, Marketing/Growth

### Sub-Agent Orchestration
- `references/context-bundle-protocol.md` — Template for spawning sub-agents
  - Context snapshot format
  - Hard constraints injection
  - Mandatory verification steps
  - Stakes calibration (high/medium/low)
  - Self-evaluation checklist

### Recommended Companion Skills
After setup, consider installing these via `npx clawhub install`:
- **qmd** — Local search/indexing for memory files (the single biggest memory upgrade)
- **github** — GitHub CLI integration
- Optional: google-calendar, weather

### Automation
- `references/automation-patterns.md` — Common cron and heartbeat patterns
  - Morning briefing template
  - Content scanning/digest cron
  - Proactive monitoring patterns
  - Multi-check heartbeat rotation

### API & Integration Checklist
- `references/api-checklist.md` — Free APIs and integrations to set up
  - Which APIs, free tier limits, setup links
  - Environment variable patterns
  - Priority order (what to set up first)

## Architecture Overview

```
workspace/
├── AGENTS.md          ← Agent operating manual
├── SOUL.md            ← Personality and voice
├── USER.md            ← Info about your human (you create this)
├── IDENTITY.md        ← Agent identity (name, creature, vibe)
├── MEMORY.md          ← Curated long-term memory
├── HEARTBEAT.md       ← Proactive check list
├── TOOLS.md           ← Local environment notes
├── memory/
│   ├── YYYY-MM-DD.md  ← Daily raw notes
│   └── heartbeat-state.json ← Check rotation tracker
├── references/
│   ├── soul-library.md
│   └── context-bundle-protocol.md
└── skills/
    └── (your skills here)
```

## Progressive Skill Building

This skill is your foundation. After setup, expand with:

1. **Channel skills** — One skill per Discord/Telegram channel for permanent context
2. **Project skills** — One skill per major project with its own references
3. **Automation skills** — Scanners, digesters, monitors
4. **Integration skills** — Connect to external services

See `references/next-steps.md` for a guided progression path.
