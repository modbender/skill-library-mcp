# Memory Maintenance Skill

Intelligent memory management for OpenClaw agents.

## What It Does

1. **Reviews daily notes** → Suggests MEMORY.md updates
2. **Checks directory health** → Finds fragmentation, naming issues
3. **Auto-cleans** → Archives old reviews, enforces retention

## Quick Start

```bash
# Install
bash scripts/install.sh

# Run review
bash scripts/review.sh

# Check status
bash scripts/status.sh

# Apply changes (after review)
bash scripts/apply.sh --safe YYYY-MM-DD
```

## Recommended Model

- **Primary**: `gemini-2.5-flash` (fast, efficient)
- **Fallback**: `gemini-2.5-flash-lite` (if needed)

## Architecture

Uses LLM for review, runs on cron schedule, human approval for content changes, auto-cleanup for maintenance tasks.

## Safety

- Content suggestions → Never auto-applied
- Safe maintenance (archiving) → Auto with `--safe`
- Risky operations → Require `--all` + confirmation
- Trash recovery → Deleted files recoverable

## Files

```
scripts/
  review.sh       # Main daily review
  apply.sh        # Apply approved changes
  cleanup.sh      # Archive & retention
  status.sh       # Check system health
  install.sh      # One-time setup

config/
  settings.json   # User configuration

SKILL.md          # Full documentation
```

## Author

**Max Hutchinson** — Building AI agent infrastructure.

- GitHub: [@MaxLaurieHutchinson](https://github.com/MaxLaurieHutchinson)
- Agent: Ash

## License

MIT
