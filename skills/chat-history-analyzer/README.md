# Chat History Analyzer

Extracts and analyzes Cursor IDE chat history to identify key discoveries, obstacles, and solutions from your conversations.

## Quick Start

```bash
# Run combined log and chat history analysis
python3 scripts/analyze_logs.py

# Analyze chat history only
python3 scripts/chat_history_analyzer.py --hours 1
```

## Features

- Extracts chat history from Cursor's SQLite databases
- Analyzes last hour for patterns indicating discoveries, obstacles, and solutions
- Saves structured markdown reports to `/Users/ghost/.openclaw/journal/`
- Integrates with self-optimizer for combined log + chat analysis

## Cron Job Setup

The `analyze_logs.py` script is designed to run hourly and combines:
- OpenClaw log analysis (errors, restarts, config changes)
- Cursor chat history analysis (discoveries, obstacles, solutions)

See `SKILL.md` for OpenClaw cron job configuration examples.

## Output

Journal entries are saved as:
```
/Users/ghost/.openclaw/journal/chat_analysis_YYYY-MM-DD_HHMMSS.md
```

Each entry contains:
- **Key Discoveries**: Successful findings and implementations
- **Obstacles Encountered**: Errors and blockers
- **Solutions Found**: Fixes and workarounds
