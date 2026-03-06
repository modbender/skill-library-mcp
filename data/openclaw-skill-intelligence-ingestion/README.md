# OpenClaw Skill: Intelligence Ingestion

Auto-analyze URLs and external information for strategic value.

Pipeline: **READ -> CLASSIFY -> ANALYZE -> MAP -> STORE -> REMEMBER -> RESPOND**

## Why

Most users do not need more content. They need better filtering.
This skill turns noisy external information into structured, actionable intelligence.

## Quick Start

```bash
# 1) Install
openclaw skills install github:sarahmirrand001-oss/openclaw-skill-intelligence-ingestion

# 2) Trigger
Analyze this: https://example.com/article

# 3) Verify
# - Obsidian note created
# - memory/YYYY-MM-DD.md updated
# - response includes category + strategic value
```

## What It Produces

- Structured Obsidian note
- Daily memory log update
- Strategic value score (Critical/High/Medium/Low)
- Next action recommendation

## Main Files

- `SKILL.md`: skill behavior and 7-step pipeline
- `index.html`: public landing page for sharing
- `vercel.json`: static deployment config

## Deploy

This repo is static-site ready for Vercel.

```bash
vercel --prod
```

