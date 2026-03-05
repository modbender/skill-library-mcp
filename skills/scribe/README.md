# Scribe | OpenClaw Skill

Comprehensive note-taking system for OpenClaw that scans logs, configs, chat history, memory files, drafts, and behavior files to generate daily and weekly notes with summaries.

## Quick Start

```bash
# Generate daily note
python3 workspace/skills/scribe/scripts/scribe.py --mode daily

# Generate weekly note
python3 workspace/skills/scribe/scripts/scribe.py --mode weekly

# Generate both
python3 workspace/skills/scribe/scripts/scribe.py --mode both
```

## Features

- ✅ **Log Analysis** - Scans OpenClaw logs for errors, warnings, gateway events, and subagent activity
- ✅ **Config Scanning** - Reads model preferences and settings from `openclaw.json`
- ✅ **Chat History** - Extracts messages from Cursor IDE SQLite databases
- ✅ **Memory Tracking** - Scans daily notes and long-term memory files
- ✅ **Draft Detection** - Finds blog posts, tweets, and other draft files
- ✅ **Behavior Files** - Reads BEHAVIOR.md, DESIRES.md, TASTES.md, PREFERENCES.md
- ✅ **Summary Generation** - Creates summaries at the top of each note file
- ✅ **Daily & Weekly Notes** - Generates both daily and weekly reports

## Output Location

Notes are saved to:
- Daily: `workspace/Notes/daily/YYYY-MM-DD.md`
- Weekly: `workspace/Notes/weekly/YYYY-MM-DD.md`

## Example Output

### Daily Note Summary

```markdown
# Daily Summary - 2026-02-17 10:30:00

- **Logs**: 3 errors, 5 warnings
- **Gateway Events**: 12 events
- **Subagent Activity**: 8 spawns
- **Chat Messages**: 45 messages
- **Daily Notes**: 2 files
- **Drafts**: 1 draft files
- **Config**: Loaded successfully
```

### Weekly Note Summary

```markdown
# Weekly Summary - 2026-02-17 10:30:00

- **Total Errors**: 15
- **Total Warnings**: 28
- **Gateway Events**: 89
- **Subagent Spawns**: 42
```

## Usage Examples

### Manual Execution

```bash
# Daily note only
python3 workspace/skills/scribe/scripts/scribe.py --mode daily

# Weekly note only
python3 workspace/skills/scribe/scripts/scribe.py --mode weekly

# Both daily and weekly
python3 workspace/skills/scribe/scripts/scribe.py --mode both

# JSON output
python3 workspace/skills/scribe/scripts/scribe.py --mode daily --json
```

### Cron Job Integration

Add to your OpenClaw cron jobs:

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run scribe.py --mode daily",
    "model": "openrouter/google/gemini-2.5-flash",
    "thinking": "low",
    "timeoutSeconds": 300
  },
  "schedule": {
    "kind": "cron",
    "cron": "0 0 * * *"
  },
  "delivery": {
    "mode": "announce"
  },
  "sessionTarget": "isolated",
  "name": "Daily Scribe Note"
}
```

## Data Sources

Scribe scans the following locations:

- **Logs**: `~/.openclaw/logs/*.log`
- **Config**: `~/.openclaw/openclaw.json`
- **Chat History**: Cursor SQLite databases (`~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`)
- **Memory**: `~/.openclaw/workspace/memory/*.md`
- **Drafts**: `~/.openclaw/workspace/**/*draft*.txt`, `**/*draft*.md`, `blog/**/*.md`, `tweet*.txt`
- **Behavior**: `~/.openclaw/workspace/BEHAVIOR.md`, `DESIRES.md`, `TASTES.md`, `PREFERENCES.md`

## Requirements

- Python 3.7+
- OpenClaw installation
- Cursor IDE (for chat history)
- SQLite3 (usually pre-installed on macOS)

## License

OpenClaw Skill - See main OpenClaw repository for license information.
