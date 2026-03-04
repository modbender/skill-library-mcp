---
name: last30days-weekly
description: "Weekly OpenClaw Skills intelligence. Tracks trending ClawHub skills via API snapshots, researches community buzz on Reddit/X/Web, generates YouTube-ready briefings. Run daily for snapshot accumulation, weekly for full report."
emoji: "\U0001F4CA"
user-invocable: true
metadata: {"openclaw": {"version": "1.0.0", "requires": {"bins": ["python3", "curl"]}, "triggers": ["skills weekly", "trending skills", "clawhub", "skill metrics", "weekly report", "skill snapshot", "last30days weekly", "openclaw skills"]}}
---

# OpenClaw Skills Weekly — Community Intelligence Skill

Automated pipeline for tracking trending OpenClaw/ClawHub skills and community discussion.

## What This Skill Does

1. **ClawHub API Snapshots** — Pulls all skills from `GET https://clawhub.ai/api/v1/skills` with cursor pagination. Stores daily snapshots in SQLite for 7-day velocity trending.
2. **Community Signal Capture** — Searches Reddit, X/Twitter, and web for OpenClaw skill discussions from the last 7 days. Structures findings into categorised signals.
3. **Trending Analysis** — Calculates install velocity (installs_current delta over trailing 7 days) to identify breakout skills.
4. **YouTube Briefing** — Generates punchy 15-second pitch scripts for the top trending skills.

## Commands

Parse the user's request and route to the correct mode:

| User says | Mode | Action |
|---|---|---|
| `snapshot` or `daily snapshot` | Snapshot | Record ClawHub metrics to DB |
| `report` or `weekly report` | Full Report | Snapshot + rank + community + scripts |
| `trending` or `what's trending` | Quick Trending | Show top 10 by velocity from DB |
| `community` or `community buzz` | Community Signals | Search Reddit/X/Web for discussions |
| `status` or `db status` | Status | Show DB health and snapshot history |

## Snapshot Mode (run daily)

```bash
python3 "${SKILL_ROOT}/scripts/clawhub_snapshot.py" snapshot
```

This fetches all skills from ClawHub API and records a timestamped snapshot to SQLite. Run this daily to build velocity history.

**Expected output:**
```
[SNAPSHOT] Fetching from https://clawhub.ai/api/v1/skills...
[SNAPSHOT] Page 1: 100 skills...
[SNAPSHOT] Done: 13,729 skills recorded at 2026-03-01T09:00:00
[SNAPSHOT] DB: 5 snapshot dates, 68,645 total rows
```

Tell the user how many skills were captured and how many snapshot dates exist.

## Full Report Mode (run weekly)

```bash
python3 "${SKILL_ROOT}/scripts/clawhub_snapshot.py" report --top 10
```

Runs: snapshot → velocity ranking → outputs markdown report.

Present the top 10 skills in a formatted table:
```
# OpenClaw Skills Weekly — Week of Mar 01, 2026

| # | Skill | Installs | 7d Delta | Stars | Score |
|---|-------|----------|----------|-------|-------|
| 1 | Gog   | 1,304    | +127     | 593   | 0.42  |
```

Then tell the user the report is saved and suggest they run community capture too.

## Community Signal Mode

Use the OpenClaw gateway's built-in WebSearch tool to search for recent community discussion:

1. Search: `"openclaw skills" site:reddit.com` (last 7 days)
2. Search: `"clawhub" trending skill` (last 7 days)
3. Search: `"openclaw skill" tutorial OR guide OR demo` (last 7 days)

For each notable result found:
- Extract the title, URL, and a 1-sentence summary
- Categorise as: tutorial, security, ecosystem, showcase, discussion, or market
- Save to the signals JSON file

```bash
python3 "${SKILL_ROOT}/scripts/clawhub_snapshot.py" community --save
```

## Status Mode

```bash
python3 "${SKILL_ROOT}/scripts/clawhub_snapshot.py" status
```

Shows: DB path, total rows, distinct snapshot dates, top 10 skills by current installs.

## Setup

The script uses Python 3 stdlib only (sqlite3, urllib, json). No pip required.

DB location: `/home/node/.local/share/skills-weekly/metrics.db`
Signals file: `/home/node/.local/share/skills-weekly/weekly_signals.json`

## Cron / Scheduling

For automated daily snapshots, add to the host's Task Scheduler or cron:

```bash
# Daily snapshot at 9am
docker exec -u node openclaw-gateway-secure python3 /home/node/.openclaw/workspace/skills/last30days-weekly/scripts/clawhub_snapshot.py snapshot
```

For the weekly full report:
```bash
# Weekly report on Mondays at 9am
docker exec -u node openclaw-gateway-secure python3 /home/node/.openclaw/workspace/skills/last30days-weekly/scripts/clawhub_snapshot.py report --top 10
```
