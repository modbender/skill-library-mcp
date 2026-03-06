# TASK: Convert clawdscan to a Clawdbot Skill + Heartbeat Integration

## Context
`clawdscan.py` is a working 919-line Python CLI that analyzes Clawdbot session health. 
It's currently a standalone script. We need to package it as a proper Clawdbot skill 
AND create heartbeat integration.

**Repo:** https://github.com/jugaad-lab/clawdscan
**Current location:** This directory (`/Users/yajat/workspace/agent-forge/2026-02-09-clawdscan/`)

## Task 1: Create Clawdbot Skill Package

Create a proper skill structure in this repo:

### Required files:

**`SKILL.md`** — The skill instruction file that Clawdbot reads. Should include:
- Description: Session health analyzer for Clawdbot/OpenClaw
- When to use: When user asks about session health, disk usage, session cleanup, bloat analysis
- Commands reference for all 7 subcommands (scan, top, inspect, tools, models, disk, clean)
- Integration patterns (cron setup, JSON export, heartbeat usage)
- Example outputs
- Alert thresholds and what they mean

**`skill.json`** — Skill metadata:
```json
{
  "name": "clawdscan",
  "version": "0.1.0",
  "description": "Session health analyzer for Clawdbot/OpenClaw. Diagnose bloat, find zombies, reclaim disk space.",
  "author": "jugaad-lab",
  "license": "MIT",
  "repository": "https://github.com/jugaad-lab/clawdscan",
  "keywords": ["sessions", "health", "maintenance", "cleanup", "disk"],
  "requirements": {
    "python": ">=3.9"
  }
}
```

**`LICENSE`** — MIT license

### Skill conventions:
- The SKILL.md should be written as instructions for an AI agent (Clawdbot) on how to use the tool
- Include exact commands to run
- Include how to interpret results
- Include recommended actions for each severity level

## Task 2: Heartbeat Integration

Create a file `heartbeat-snippet.md` that contains the exact block to add to a user's HEARTBEAT.md:

```markdown
## Session Health Check (clawdscan)
Run periodically (every 6-12 hours):
```bash
python3 /path/to/clawdscan.py scan --json /tmp/clawdscan-report.json
```

Check the JSON report:
- If any sessions are 🔴 critical → alert the user
- If zombie count > 20 → suggest cleanup
- If total disk > 200MB → suggest cleanup
- Track trends: compare with previous report
```

## Task 3: Trend Tracking Feature

Add a new subcommand to clawdscan.py: `history`

**`clawdscan.py history`** — Saves scan results over time and shows trends:
- After each `scan`, optionally append summary to `~/.clawdbot/clawdscan-history.json`
- `clawdscan.py scan --save-history` — run scan AND save to history
- `clawdscan.py history` — show trend: sessions count, disk usage, critical count over time
- `clawdscan.py history --json` — export history as JSON

History format:
```json
[
  {
    "timestamp": "2026-02-09T04:30:00Z",
    "total_sessions": 1765,
    "total_disk_mb": 150.7,
    "critical": 9,
    "warning": 415,
    "zombie": 30,
    "healthy": 1311
  }
]
```

## Task 4: Update README.md

Update the README to reflect:
- Skill installation instructions (ClawdHub + manual)
- All commands including new `history` command
- Heartbeat integration guide
- Example outputs
- Badge: Python 3.9+ required

## Important Notes
- Do NOT break the existing clawdscan.py functionality
- Keep it zero-dependency (stdlib only)
- The script must remain a single file (that's a feature, not a limitation)
- Test all changes work by running the commands
- Commit everything to git when done

## Testing
After making changes, verify:
1. `python3 clawdscan.py scan` still works
2. `python3 clawdscan.py scan --save-history` works
3. `python3 clawdscan.py history` shows the saved data
4. All existing commands still work
5. SKILL.md reads well as AI instructions
