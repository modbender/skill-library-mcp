---
name: openclaw-token-optimizer
description: Optimize OpenClaw token usage and cost by auditing context injection, trimming workspace files (AGENTS.md/SOUL.md/MEMORY.md and daily memory), enabling prompt caching, heartbeat, context pruning, compaction, memory search or qmd, subagents, model tiering, and cron frequency. Use when a user asks to reduce OpenClaw token spend, speed up sessions, shrink context, or configure openclaw.json and memory search settings.
---

# OpenClaw Token Optimizer

## Overview
Deliver a practical audit and configuration plan that cuts input tokens and unnecessary calls while keeping answer quality. Provide concrete config edits, workspace file trimming guidance, and a prioritized rollout plan.

## Workflow

### 1) Scope and locate configuration
- Identify the OpenClaw config file location (common paths include `~/.openclaw/openclaw.json`, `.openclaw/openclaw.json`, or project root config).
- List injected workspace files in scope (e.g., `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `MEMORY.md`, and `memory/YYYY-MM-DD.md`).
- Confirm provider and model support for prompt caching and memory search to avoid proposing unsupported keys.

### 2) Baseline token sources
- Break input cost into buckets: system prompt, tool schema, workspace files, memory files, and conversation history.
- Use a rough sizing method if exact token counts are unavailable (e.g., characters/4 as a quick estimate) and call out that the estimate is approximate.

### 3) Input reduction (highest ROI)
- Trim workspace files first. Target budgets:
  - `AGENTS.md`: keep only essential agent rules and policies.
  - `SOUL.md`: reduce to short persona bullets.
  - `MEMORY.md`: keep durable facts only; archive the rest.
  - `memory/YYYY-MM-DD.md`: prune or rotate daily logs.
- Remove unused workspace injections in config (e.g., if `TOOLS.md` or `IDENTITY.md` is unused).
- Prefer memory search over full-file injection for large memories. If using qmd, index only needed paths.

### 4) Cache and context control
- Enable prompt caching for the primary model when supported. Set `cacheRetention` to a long window and keep a consistent system prompt to maximize cache hits.
- Configure heartbeat to keep the cache warm (e.g., ~55 minutes), using a low-cost model and a minimal heartbeat prompt.
- Enable context pruning with a TTL that matches the cache window to prevent unbounded history growth.
- Add compaction with memory flush so long sessions preserve durable decisions while clearing history.

### 5) Call reduction
- Audit cron and scheduled tasks. Consolidate overlapping checks, reduce frequency, and move non-creative tasks to cheaper models.
- Configure delivery to be on-demand or only on change to avoid no-op calls.

### 6) Model strategy
- Default to a cost-effective model for routine work and provide aliases for manual upgrades to premium models.
- Use subagents for parallel, isolated tasks with cheaper models to avoid bloating the main context.

### 7) Deliverables
Provide:
- A short audit summary and estimated savings.
- A concrete config patch or JSON snippet for `openclaw.json`.
- A list of files to trim, with before/after size targets.
- A phased rollout plan (quick wins first, then advanced options).

## References
- Use `references/openclaw-token-optimization.md` for configuration snippets, checklists, and qmd guidance.
