---
name: session-hygiene
description: Prevent sessions.json bloat from accumulating isolated sessions (hooks, crons, subagents). Sets up a cron to archive stale sessions to daily JSONL files and keep sessions.json lean. Use when sessions.json grows large, the gateway becomes slow or unresponsive, or as preventive maintenance on any OpenClaw instance with hooks or crons. Related to openclaw/openclaw#15225.
---

# Session Hygiene

OpenClaw's session store (`sessions.json`) grows unbounded — every hook, cron, and subagent invocation creates a session entry that never gets cleaned up. Heavy setups (webhooks + crons) can hit 200MB+ and 7000+ sessions within weeks, causing gateway slowdowns and unresponsiveness.

This skill sets up automated archive-and-rotate to keep `sessions.json` lean while preserving session history.

## Quick Setup

Create a cron that runs every 6 hours:

```javascript
cron(action: "add", job: {
  name: "Session Archive & Cleanup",
  schedule: { kind: "cron", expr: "0 */6 * * *", tz: "America/Los_Angeles" },
  sessionTarget: "isolated",
  payload: {
    kind: "agentTurn",
    message: "Archive and clean up stale sessions. Run the script: python3 <skill-dir>/scripts/archive_sessions.py",
    timeoutSeconds: 60
  },
  delivery: { mode: "announce", channel: "slack" }
})
```

Adjust the timezone and delivery channel to match your setup.

## What It Does

1. **Archive**: Sessions older than 48 hours get moved to `sessions-archive/YYYY-MM-DD.jsonl` (one JSON line per session, grouped by date)
2. **Protect**: `agent:main:main` is never removed
3. **Rotate**: Archive files older than 30 days are deleted
4. **Report**: Logs how many sessions were archived, how many remain, and file sizes

## Manual Run

For an immediate cleanup (e.g., if sessions.json is already bloated):

```bash
python3 <skill-dir>/scripts/archive_sessions.py
```

Or for a one-time aggressive purge of sessions older than N hours:

```bash
python3 <skill-dir>/scripts/archive_sessions.py --max-age-hours 1
```

## Tuning

| Parameter | Default | Notes |
|-----------|---------|-------|
| `--max-age-hours` | 48 | How old a session must be before archiving |
| `--archive-retention-days` | 30 | How long to keep archive JSONL files |
| `--sessions-path` | Auto-detected | Path to sessions.json |
| `--dry-run` | off | Preview what would be archived without changing anything |

## Sizing Estimates

| Sessions/day | 48h retention | sessions.json size |
|-------------|---------------|-------------------|
| 50 | ~100 sessions | ~3MB |
| 100 | ~200 sessions | ~6MB |
| 200 | ~400 sessions | ~12MB |

Without this skill, the same setup would grow to 200MB+ within a month.
