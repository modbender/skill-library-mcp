---
name: context-slimmer
description: Audit and slim down always-loaded context files (AGENTS.md, TOOLS.md, USER.md, MEMORY.md, HEARTBEAT.md, SOUL.md, IDENTITY.md). Use when asked to reduce token usage, audit context files, optimize context window, or slim down workspace files. Measures current token cost and identifies what to move, remove, or compress.
---

# Context Slimmer

Audit workspace files that load into every message and reduce their token footprint.

## Quick Start

```bash
# Measure current context cost
bash scripts/measure.sh

# Full audit (outputs recommendations)
bash scripts/measure.sh --audit
```

## Audit Process

For each always-loaded file, evaluate:

1. **Move to skill** — Content only needed for specific tasks (betting config, group chat rules, detailed protocols). Move to a skill or reference file that loads on demand.
2. **Remove** — Outdated info, dead features, completed one-time setup, duplicated content across files.
3. **Compress** — Verbose explanations that could be 1 sentence. If the agent already knows it, cut it.

## Rules of Thumb

- If a cron job handles it, remove it from HEARTBEAT.md
- If it's in SOUL.md, don't repeat it in MEMORY.md or AGENTS.md
- If it's in USER.md, don't repeat it in MEMORY.md
- If the agent does it daily, it doesn't need instructions — just a trigger word
- Prefer 1 sentence over 5 bullets saying the same thing
- Target: each file should justify every line's token cost

## Expected File Sizes (lean targets)

| File | Target |
|------|--------|
| AGENTS.md | < 500 tokens |
| TOOLS.md | < 500 tokens |
| USER.md | < 700 tokens |
| MEMORY.md | < 400 tokens |
| HEARTBEAT.md | < 400 tokens |
| SOUL.md | < 250 tokens |
| IDENTITY.md | < 50 tokens |
| **Total** | **< 2,800 tokens** |

## Output Format

Report: current size, projected size, savings per file. Include specific recommendations grouped by move/remove/compress.
