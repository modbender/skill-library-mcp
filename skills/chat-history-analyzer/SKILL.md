---
name: chat-history-analyzer
displayName: Chat History Analyzer | OpenClaw Skill
description: Extracts and analyzes Cursor IDE chat history to identify key discoveries, obstacles, and solutions, saving findings to the journal.
version: 1.0.0
---

# Chat History Analyzer | OpenClaw Skill

## Description

Extracts and analyzes Cursor IDE chat history to identify key discoveries, obstacles, and solutions, saving findings to the journal.

# Chat History Analyzer | OpenClaw Skill

Extracts chat history from Cursor IDE's local SQLite databases, analyzes the last hour of conversations for key discoveries, obstacles, and solutions, and saves structured findings to the OpenClaw journal directory.


## Usage

- As a scheduled cron job to continuously track insights from chat history
- Manually to analyze recent chat activity
- To identify recurring patterns, problems, or solutions in your workflow

```bash
# Combined log and chat history analysis (for cron jobs)
python3 /Users/ghost/.openclaw/workspace/skills/chat-history-analyzer/scripts/analyze_logs.py

# Analyze last hour of chat history only
python3 /Users/ghost/.openclaw/workspace/skills/chat-history-analyzer/scripts/chat_history_analyzer.py

# Analyze last 2 hours
python3 /Users/ghost/.openclaw/workspace/skills/chat-history-analyzer/scripts/chat_history_analyzer.py --hours 2

# Output JSON format
python3 /Users/ghost/.openclaw/workspace/skills/chat-history-analyzer/scripts/analyze_logs.py --json
```


## What this skill does

- **Extracts** chat history from Cursor's SQLite databases (global and workspace-specific)
- **Analyzes** the last hour of messages for patterns indicating discoveries, obstacles, and solutions
- **Saves** structured findings to `/Users/ghost/.openclaw/journal/` as markdown files
- **Runs** automatically via cron job every hour


## Integration as a Cron Job

This skill is designed to run hourly via OpenClaw cron. The `analyze_logs.py` script combines both log analysis and chat history analysis.

**Example Cron Job Configuration:**

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run analyze_logs.py script to analyze the last hour of logs and Cursor chat history, saving findings to journal.",
    "model": "openrouter/google/gemini-2.5-flash",
    "thinking": "low",
    "timeoutSeconds": 180
  },
  "schedule": {
    "kind": "cron",
    "cron": "0 * * * *"
  },
  "delivery": {
    "mode": "announce"
  },
  "sessionTarget": "isolated",
  "name": "Chat History & Log Analysis"
}
```

**Or run directly via shell script:**

```bash
# Add to crontab (crontab -e)
# Run every hour at minute 0
0 * * * * /Users/ghost/.openclaw/workspace/skills/chat-history-analyzer/scripts/analyze_logs.py --json >> /Users/ghost/.openclaw/logs/analyze_logs.log 2>&1
```


## Output Format

Findings are saved to `/Users/ghost/.openclaw/journal/chat_analysis_YYYY-MM-DD_HHMMSS.md` with sections for:

- **Key Discoveries**: Successful findings, realizations, and implementations
- **Obstacles Encountered**: Errors, failures, and blockers
- **Solutions Found**: Fixes, workarounds, and resolutions


## Requirements

- Cursor IDE installed with chat history stored locally
- SQLite3 available (usually pre-installed on macOS)
- OpenClaw journal directory writable


## How it works

1. Connects to Cursor's SQLite databases at `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` and workspace-specific databases
2. Extracts messages from the last N hours (default: 1 hour)
3. Analyzes message content using pattern matching for discoveries, obstacles, and solutions
4. Saves structured markdown report to the journal directory
