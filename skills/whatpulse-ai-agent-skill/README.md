# WhatPulse AI Skill

Query your [WhatPulse](https://whatpulse.org) computer usage statistics using natural language. Keystrokes, mouse activity, application screen time, network bandwidth, website tracking, uptime, and profiles; all read directly from the local WhatPulse SQLite database.

Works with Claude Code, OpenClaw, and any AI coding agent that supports the Agent Skills specification.

![Example of WhatPulse skill in action, showing a daily briefing and answering questions about computer usage](./docs/screenshot.png)

## Installation

Copy `SKILL.md` into your agent's skills directory.

Claude Code:
```bash
mkdir -p ~/.claude/skills/whatpulse
cp SKILL.md ~/.claude/skills/whatpulse/
```

OpenClaw:
```bash
mkdir -p ~/.openclaw/skills/whatpulse
cp SKILL.md ~/.openclaw/skills/whatpulse/
```

Alternatively, copy it as a slash command for Claude Code:
```bash
mkdir -p ~/.claude/commands
cp SKILL.md ~/.claude/commands/whatpulse.md
```

Restart your agent after installing.

## Requirements

- [WhatPulse](https://whatpulse.org) installed with a local database
- `sqlite3` CLI available on your PATH

## Usage

```
/whatpulse
```
Returns a daily briefing: today's stats vs your averages, top apps, and an insight.

```
/whatpulse <question>
```
Ask anything about your computer usage.

### Examples

```
/whatpulse how productive was I today?
/whatpulse what apps did I use the most this week?
/whatpulse how much time did I spend in VS Code today?
/whatpulse what are my most-used keyboard shortcuts?
/whatpulse how far has my mouse traveled?
/whatpulse top countries by network traffic
/whatpulse am I working later than usual this week?
/whatpulse compare my profiles by keystroke volume
/whatpulse what websites did I spend the most time on?
/whatpulse summarize this week vs last week
```

## Database Location

The skill auto-detects your WhatPulse database. Default paths:

- macOS: `~/Library/Application Support/WhatPulse/whatpulse.db`
- Windows: `%LOCALAPPDATA%\WhatPulse\whatpulse.db`
- Linux: `~/.config/whatpulse/whatpulse.db`

Override with the `WHATPULSE_DB` environment variable:
```bash
export WHATPULSE_DB="/custom/path/to/whatpulse.db"
```

## Remote Access

For AI agents running on a remote server, sync the database periodically.

1. On the WhatPulse machine, schedule a snapshot:
```bash
# cron: every 4 hours (adjust as wanted)
0 */4 * * * sqlite3 ~/Library/Application\ Support/WhatPulse/whatpulse.db ".backup '/path/to/synced/whatpulse.db'"
```

2. Sync via cloud storage (Dropbox, OneDrive, etc.) or `rsync`.

3. On the remote machine:
```bash
export WHATPULSE_DB="/data/whatpulse.db"
```

## Safety

All queries use `sqlite3 -readonly`. No writes, no locks, no journal files. The database is never modified.

## License

MIT
