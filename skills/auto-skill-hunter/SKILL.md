---
name: auto-skill-hunter
description: Proactively discovers, ranks, and installs high-value ClawHub skills by mining unresolved user needs and agent context. Use when new tasks are unsolved, when capability gaps appear, when users ask for better tools, or as a scheduled patrol for continuous skill growth.
tags: [meta, evolution, learning, proactive]
---

# Auto Skill Hunter

Auto Skill Hunter continuously expands an agent's capability stack with task-relevant skills, then explains why each selected skill is worth trying.

## When to Use

Use this skill when at least one of the following is true:

- The user asks for a task that current skills cannot solve reliably.
- Similar issues keep appearing across recent sessions.
- The user explicitly asks to discover/install better skills.
- The agent needs proactive capability growth on a timer.

## High-Value Outcomes

- Faster discovery of practical skills for real unresolved tasks.
- Lower manual browsing effort on ClawHub.
- Better skill stack diversity through complementarity scoring.
- Safer adoption via bounded install count and runnable checks.

## Usage

```bash
node skills/skill-hunter/src/hunt.js
```

### Common Commands

```bash
# 1) Full automatic patrol
node skills/skill-hunter/src/hunt.js --auto

# 2) Targeted hunt for a specific unresolved problem
node skills/skill-hunter/src/hunt.js --query "Cannot reliably fetch web pages and summarize key insights"

# 3) Preview only (no write/install)
node skills/skill-hunter/src/hunt.js --dry-run

# 4) Cap per-run installation count
node skills/skill-hunter/src/hunt.js --max-install 2
```

## Core Workflow

1. Extract unresolved problems and topic signals from recent chat/session memory.
2. Search ClawHub with trending feeds and query endpoints.
3. Score candidates with multi-factor ranking:
   - issue relevance
   - profile and personality fit (`USER.md` + personality state)
   - complementarity with already installed skills
   - quality signals such as stars/downloads (when available)
4. Install top candidates with a runnable entry and self-test fallback.
5. Produce a concise recommendation report with strengths, scenarios, and selection reasons.

## Best-Fit Scenarios

- A user asks for a task that current skills cannot solve well.
- Recent sessions show repeated failures or unresolved tickets.
- The agent needs proactive capability growth without manual curation.
- The team wants a lightweight "discover -> test -> keep/remove" loop.

## Operating Modes

- **Auto patrol mode**: `--auto` for periodic capability growth.
- **Targeted mode**: `--query "..."` when a specific user problem is known.
- **Safe preview mode**: `--dry-run` before enabling real installs.

## Recommended Execution Policy

- Start with `--dry-run` in new environments.
- Use `--max-install 1~2` to avoid noisy bulk installs.
- Re-run with a focused `--query` when no candidate passes threshold.
- Keep only skills that survive at least one real task run.

## Scheduled Trigger Recommendation

For continuous value, run Auto Skill Hunter on a timer:

- Every **30 min** for high-change or fast-moving projects
- Every **60 min** for normal workflows
- Every **120 min** for stable environments

This cadence keeps capability coverage fresh and reduces reaction lag when new user needs appear.

### Suggested Cron-Style Routine

```bash
# High-change projects
*/30 * * * * node /path/to/workspace/skills/skill-hunter/src/hunt.js --auto --max-install 1

# Normal projects
0 * * * * node /path/to/workspace/skills/skill-hunter/src/hunt.js --auto --max-install 2
```

## Installation Policy

- Defaults to max 2 installations per run (configurable with `--max-install` or env).
- Skips already-installed skills.
- Falls back to scaffold mode when remote clone fails.

## Safety and Quality Guardrails

- Never overwrite existing skill folders.
- Prefer small, frequent patrols over large one-shot installs.
- Keep report output concise and action-oriented.
- Disable outbound reporting during local tests with `SKILL_HUNTER_NO_REPORT=1`.
