---
name: memory-maintenance
version: 1.0.0
description: "Intelligent memory management for OpenClaw agents. Reviews daily notes, suggests MEMORY.md updates, maintains directory health, and auto-cleans old files. Recommended for agents with growing memory footprints."
homepage: https://github.com/MaxLaurieHutchinson/memory-maintenance
author: 
  name: "Max Hutchinson"
  email: "max.hutchinson258@gmail.com"
  url: "https://github.com/MaxLaurieHutchinson"
tags: ["memory", "maintenance", "automation", "agent-improvement", "workflow"]
metadata:
  openclaw:
    emoji: 🧹
    requires: 
      bins: ["gemini", "jq"]
      env: ["GEMINI_API_KEY"]
    install:
      - id: setup
        kind: script
        script: ./scripts/install.sh
        label: "Install memory maintenance"
---

# Memory Maintenance Skill

Intelligent memory management for OpenClaw agents. Reviews daily notes, suggests MEMORY.md updates, maintains directory health, and auto-cleans old files.

## Why This Exists

Agents wake up fresh every session. Without maintenance:
- Daily notes pile up and become unsearchable
- Important decisions get buried in old sessions
- Context windows fill with irrelevant history
- You repeat the same context-setting every day

This skill automates the tedious work of keeping your agent's memory organized and actionable.

## Features

- **Content Review**: Analyzes daily notes and suggests MEMORY.md updates
- **Directory Health**: Monitors memory/ directory for naming issues, fragmentation, bloat
- **Auto-Cleanup**: Archives old reviews (7+ days) and enforces retention policy (30 days)
- **Safe by Default**: Content changes require approval; only safe maintenance auto-applies

## Recommended Model

This skill works well with lightweight models. We recommend:
- **Primary**: `gemini-2.5-flash` (fast, cost-effective)
- **Fallback**: `gemini-2.5-flash-lite` (if rate limits hit)

Both handle the structured output and analysis tasks efficiently.

## Quick Start

```bash
# Install the skill
clawhub install memory-maintenance

# Configure (optional)
# Edit config/settings.json to customize schedule, retention, etc.

# Run manually
openclaw skill memory-maintenance run

# Or let it run automatically via cron (configured during install)
```

## Architecture

```
Daily Session Notes (memory/YYYY-MM-DD.md)
    ↓
Review Agent (scheduled daily)
    ↓
Structured Suggestions (JSON)
    ↓
Human Review (markdown report)
    ↓
Approved Updates → MEMORY.md
    ↓
Auto-Cleanup (archive old files)
```

## Workflow

1. **Daily Review** (23:00 by default)
   - Scans configurable lookback period (default: 7 days)
   - Checks memory/ directory health
   - Generates suggestions via LLM
   - Outputs structured JSON + human-readable markdown

2. **Human Review**
   - Read `agents/memory/review-v2-YYYY-MM-DD.md`
   - Approve/reject suggestions

3. **Apply Changes**
   ```bash
   # Dry run (preview)
   openclaw skill memory-maintenance apply --dry-run 2026-02-05
   
   # Apply safe changes (archiving, cleanup)
   openclaw skill memory-maintenance apply --safe 2026-02-05
   
   # Apply all (requires confirmation)
   openclaw skill memory-maintenance apply --all 2026-02-05
   ```

4. **Auto-Cleanup** (runs after successful review)
   - Archives reviews older than configured threshold
   - Deletes archive files older than retention period
   - Cleans up error logs

## Configuration

Edit `config/settings.json`:

```json
{
  "schedule": {
    "enabled": true,
    "time": "23:00",
    "timezone": "Europe/London"
  },
  "review": {
    "lookback_days": 7,
    "model": "gemini-2.5-flash",
    "max_suggestions": 10
  },
  "maintenance": {
    "archive_after_days": 7,
    "retention_days": 30,
    "consolidate_fragments": true,
    "auto_archive_safe": true
  },
  "safety": {
    "require_approval_for_content": true,
    "require_approval_for_delete": true,
    "trash_instead_of_delete": true
  }
}
```

## Safety

- **Content suggestions**: Never auto-applied (human review mandatory)
- **Safe maintenance** (archiving): Auto-applied with `--safe`
- **Risky operations** (delete, rename): Require `--all` + confirmation
- **Trash recovery**: Deleted files go to `agents/memory/.trash/` (recoverable for retention period)

## Commands

```bash
# Run review manually
openclaw skill memory-maintenance review

# Apply changes
openclaw skill memory-maintenance apply [--dry-run|--safe|--all] DATE

# Run cleanup
openclaw skill memory-maintenance cleanup

# Check status
openclaw skill memory-maintenance status

# View stats
openclaw skill memory-maintenance stats
```

## Integration with MEMORY.md

The skill suggests updates to standard MEMORY.md sections:
- Agent Identity and Core Preferences
- Infrastructure/Setup
- Memory Management
- Backup & Migration
- Contacts
- Scheduled Operations
- Content Creation & Projects
- Active Projects

## Files

### Output
- `agents/memory/review-v2-YYYY-MM-DD.json` — Structured suggestions
- `agents/memory/review-v2-YYYY-MM-DD.md` — Human-readable report
- `agents/memory/stats.json` — Aggregate statistics

### Archive
- `agents/memory/archive/YYYY-MM/` — Monthly buckets
- `agents/memory/.trash/` — Recoverable deletions

## Requirements

- OpenClaw >= 2026.2.0
- Gemini CLI (`brew install gemini-cli`)
- jq (`brew install jq`)
- Gemini API key (from Google AI Studio)

## Troubleshooting

**"Gemini failed"**
→ Check `GEMINI_API_KEY` is set in `.env` or environment

**"No suggestions generated"**
→ Check daily notes exist in `memory/YYYY-MM-DD.md`
→ Review error logs in `agents/memory/error-*.txt`

**"Too many maintenance tasks"**
→ Run `openclaw skill memory-maintenance apply --safe` to archive old files
→ Adjust `archive_after_days` in config

## Author

Built by **Max Hutchinson** as part of an AI agent infrastructure exploration.

- GitHub: [@MaxLaurieHutchinson](https://github.com/MaxLaurieHutchinson)
- Agent: Ash (OpenClaw)

## License

MIT — Free to use, modify, distribute.

---

*Part of the Hybrid Agent Architecture. Built for agents that improve over time.*
