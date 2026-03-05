---
name: scribe
displayName: Scribe | OpenClaw Skill
description: Scans OpenClaw logs, config files, chat history, cursor history, behavior, desires, tastes, and drafts to take comprehensive daily and weekly notes with summaries.
version: 1.0.0
---

# Scribe | OpenClaw Skill

Comprehensive note-taking system that scans multiple OpenClaw data sources to generate daily and weekly notes with summaries.

## Description

Scribe automatically scans and analyzes:
- **OpenClaw logs** - Errors, warnings, gateway events, subagent activity
- **Config files** - Model preferences, gateway settings, agent configurations
- **Chat history** - Cursor IDE chat messages from SQLite databases
- **Cursor history** - Workspace-specific conversation history
- **Memory files** - Daily notes and long-term memory (MEMORY.md)
- **Behavior files** - BEHAVIOR.md, DESIRES.md, TASTES.md, PREFERENCES.md
- **Drafts** - Blog posts, tweets, and other draft files

Generates structured markdown notes with summaries at the top of each file.

## Installation

```bash
clawhub install scribe
```

Or clone into your skills directory:

```bash
git clone https://github.com/Org/scribe.git workspace/skills/scribe
```

## Usage

### Daily Notes

Generate a daily note covering the last 24 hours:

```bash
python3 workspace/skills/scribe/scripts/scribe.py --mode daily
```

### Weekly Notes

Generate a weekly note covering the last 7 days:

```bash
python3 workspace/skills/scribe/scripts/scribe.py --mode weekly
```

### Both Daily and Weekly

Generate both notes at once:

```bash
python3 workspace/skills/scribe/scripts/scribe.py --mode both
```

### JSON Output

Get results in JSON format:

```bash
python3 workspace/skills/scribe/scripts/scribe.py --mode daily --json
```

## Examples

**Example 1: Daily Note Generation**  
*Scenario:* You want a daily summary of OpenClaw activity.  
*Action:* Run `python3 workspace/skills/scribe/scripts/scribe.py --mode daily`.  
*Outcome:* A markdown file `workspace/Notes/daily/YYYY-MM-DD.md` with a summary at the top, followed by detailed sections for logs, chat history, memory, drafts, behavior, and config.

**Example 2: Weekly Summary**  
*Scenario:* You want a weekly overview of patterns and trends.  
*Action:* Run `python3 workspace/skills/scribe/scripts/scribe.py --mode weekly`.  
*Outcome:* A markdown file `workspace/Notes/weekly/YYYY-MM-DD.md` with weekly statistics, trends, and activity summaries.

**Example 3: Cron Job Integration**  
*Scenario:* Automate daily note generation.  
*Action:* Add a cron job that runs `scribe.py --mode daily` every day at midnight.  
*Outcome:* Daily notes are automatically generated and saved to `workspace/Notes/daily/`.

## Commands

```bash
python3 workspace/skills/scribe/scripts/scribe.py --mode daily    # Generate daily note
python3 workspace/skills/scribe/scripts/scribe.py --mode weekly   # Generate weekly note
python3 workspace/skills/scribe/scripts/scribe.py --mode both     # Generate both
python3 workspace/skills/scribe/scripts/scribe.py --mode daily --json  # JSON output
python3 workspace/skills/scribe/scripts/scribe.py --openclaw-home /path/to/openclaw  # Custom home directory
```

- **--mode** — Choose `daily`, `weekly`, or `both` (default: `daily`)
- **--json** — Output results in JSON format instead of markdown files
- **--openclaw-home** — Specify OpenClaw home directory (default: `~/.openclaw`)

## What this skill does

1. **Scans logs** - Analyzes all `.log` files in `logs/` directory for errors, warnings, gateway events, and subagent spawns
2. **Reads config** - Extracts model preferences, gateway settings, and agent configurations from `openclaw.json`
3. **Extracts chat history** - Queries Cursor's SQLite databases (`state.vscdb`) for recent chat messages
4. **Scans memory files** - Reads daily notes (`memory/YYYY-MM-DD.md`) and long-term memory (`MEMORY.md`)
5. **Finds drafts** - Searches for draft files matching patterns like `*draft*.txt`, `*draft*.md`, `blog/**/*.md`, `tweet*.txt`
6. **Reads behavior files** - Looks for `BEHAVIOR.md`, `DESIRES.md`, `TASTES.md`, `PREFERENCES.md`
7. **Generates notes** - Creates structured markdown files with summaries at the top
8. **Saves to Notes** - Writes daily notes to `workspace/Notes/daily/YYYY-MM-DD.md` and weekly notes to `workspace/Notes/weekly/YYYY-MM-DD.md`

## Output Format

### Daily Note Structure

```markdown
# Daily Summary - YYYY-MM-DD HH:MM:SS

- **Logs**: X errors, Y warnings
- **Gateway Events**: Z events
- **Subagent Activity**: N spawns
- **Chat Messages**: M messages
- **Daily Notes**: K files
- **Drafts**: L draft files
- **Config**: Loaded successfully

---

# Daily Note

## Logs
### Errors (X)
- [error details]

### Warnings (Y)
- [warning details]

## Chat History
Found M messages in the last 24 hours.
### User (X messages)
- [message previews]

## Memory Files
### Daily Notes (K)
- **YYYY-MM-DD**: [content preview]

## Drafts
### [draft path]
- Size: X bytes
- Modified: [timestamp]
- Preview: [content preview]

## Behavior & Preferences
### Behavior Files
- **BEHAVIOR.md**: [content preview]

## Configuration
### Model Preferences
- Default: [model]
- Aliases: X configured
```

### Weekly Note Structure

```markdown
# Weekly Summary - YYYY-MM-DD HH:MM:SS

[Summary statistics]

---

# Weekly Note - YYYY-MM-DD to YYYY-MM-DD

## Weekly Summary
- **Total Errors**: X
- **Total Warnings**: Y
- **Gateway Events**: Z
- **Subagent Spawns**: N

## Chat Activity (M messages)
- **User**: X messages
- **Assistant**: Y messages

## Memory Activity (K daily notes)
- **YYYY-MM-DD**: X bytes

## Drafts (L files)
- **[path]**: X bytes (modified: [timestamp])

## Trends & Patterns
- ⚠️ **Error Rate**: X errors this week
- 🤖 **Subagent Activity**: N spawns this week
- 💬 **Chat Activity**: M messages this week
```

## Requirements

- Python 3.7+
- OpenClaw installation with `~/.openclaw` directory structure
- Cursor IDE installed (for chat history scanning)
- SQLite3 available (usually pre-installed on macOS)
- Write access to `workspace/Notes/` directory

## Integration as a Cron Job

**Example Cron Job Configuration:**

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run scribe.py --mode daily to generate daily notes.",
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

**Or run directly via shell script:**

```bash
# Add to crontab (crontab -e)
# Run daily at midnight
0 0 * * * /Users/ghost/.openclaw/workspace/skills/scribe/scripts/scribe.py --mode daily >> /Users/ghost/.openclaw/logs/scribe.log 2>&1
```

## Security & Privacy

- **File access**: Reads `openclaw.json` (config only, no secrets), `logs/*.log`, `memory/*.md`, and Cursor SQLite databases
- **No data exfiltration**: All data stays local; notes are saved to `workspace/Notes/` directory
- **Safe execution**: Uses read-only access to config and logs; only writes to `workspace/Notes/daily/` and `workspace/Notes/weekly/` directories

## Limitations

- Chat history extraction depends on Cursor's database schema (may need updates if Cursor changes storage format)
- Draft file detection uses pattern matching; may miss files with non-standard naming
- Behavior file detection looks for common filenames; custom locations may not be found
- Large log files may take time to process
