---
name: creative-agents
displayName: Creative Agents
description: Integration scripts for the creative agent swarm managed by overstory (Claude Code). Use when configuring or running researcher, social media, blog, or scribe agents.
---

# Creative Agents Skill

Integration scripts for the creative agent swarm managed by overstory (Claude Code). Provides the automation layer that agent definitions in `agents/` rely on.

## Overview

These scripts power four creative agents:
- **Researcher** — topic research via last30days skill
- **Social Media Manager** — posting, monitoring, engagement via Playwright + OAuth
- **Blogger** — content pipeline: research → outline → draft → humanize → publish
- **Scribe** — log analysis, pattern detection, memory curation

## Scripts

| Script | Class | Purpose |
|--------|-------|---------|
| `researcher_integration.py` | `ResearcherIntegration` | Discovers and invokes the last30days skill, parses results into structured reports |
| `oauth_handler.py` | `OAuthHandler` | Manages OAuth tokens for social platforms (Twitter, LinkedIn, etc.) |
| `social_playwright.py` | `SocialPlaywright` | Browser automation for social media actions via Playwright |
| `humanizer_integration.py` | `HumanizerIntegration` | Discovers and invokes the humanizer skill for natural-sounding content |
| `log_analyzer.py` | `LogAnalyzer` | Multi-source log scanning (Cursor, nanobot, Claude, shell) |
| `memory_curator.py` | `MemoryCurator` | Extracts insights from daily notes and commits to MEMORY.md |
| `scribe_integration.py` | `ScribeIntegration` | Orchestrates the full scribe pipeline with memory commits |

## Usage

All scripts are importable as Python modules and executable as CLI tools:

```bash
# Research
python3 scripts/researcher_integration.py --topic "AI agents" --days 30 --json

# OAuth status
python3 scripts/oauth_handler.py status --platform twitter --json

# Social posting
python3 scripts/social_playwright.py post --platform twitter --content "Hello world" --json

# Humanize content
python3 scripts/humanizer_integration.py --content "Technical text" --style casual --json

# Log analysis
python3 scripts/log_analyzer.py --hours 24 --sources cursor,nanobot,claude --json

# Memory curation
python3 scripts/memory_curator.py curate --days 7 --json

# Scribe pipeline
python3 scripts/scribe_integration.py --mode daily --commit-memory --json
```

## Architecture

nanobot routes tasks → overstory spawns agents → agents invoke these scripts.

Agent definitions live in `/Users/ghost/.openclaw/workspace/agents/`. Scripts live here. Overstory handles all agent lifecycle (spawn, monitor, collect results).

## Requirements

- Python 3.9+
- Playwright (for social_playwright.py)
- Optional: system keyring (for encrypted OAuth token storage)
