---
name: skills-weekly
description: "OpenClaw Skills Weekly — tracks trending ClawHub skills, generates GitHubAwesome-style YouTube video scripts with two-track ranking (Movers + Rockets)."
emoji: "\U0001F4CA"
user-invocable: true
metadata:
  openclaw:
    version: "1.0.0"
    requires:
      bins: ["python3"]
      env: ["ANTHROPIC_API_KEY"]
    triggers:
      - "skills weekly"
      - "trending skills"
      - "clawhub trending"
      - "skill metrics"
      - "weekly report"
      - "skill snapshot"
      - "openclaw skills"
      - "generate report"
      - "video script"
---

# OpenClaw Skills Weekly

Automated pipeline for tracking trending ClawHub skills and generating YouTube-ready video scripts in the GitHubAwesome format.

## What This Skill Does

1. **ClawHub API Discovery** — Fetches all ~13K skills from `GET https://clawhub.ai/api/v1/skills` with cursor pagination. No auth required.
2. **SQLite Time-Series Snapshots** — Records daily metrics (installs, downloads, stars) to build 7-day velocity history.
3. **Two-Track Ranking** — MOVERS (established skills, 30+ days, ranked by install velocity) and ROCKETS (new skills <30 days, with recency bonus). Author diversity cap prevents one author from dominating.
4. **Content Harvesting** — Fetches documentation and author info from ClawHub detail API for top-ranked skills.
5. **YouTube Script Generation** — Generates GitHubAwesome-style video segments via Claude Haiku: hook-first, technical specs, no popularity metrics, dry newscast tone.
6. **Dual Output** — Markdown report (`.md`) + voice-ready video script (`.txt`).

## Commands

Parse the user's request and route to the correct mode:

| User says | Mode | What happens |
|---|---|---|
| `weekly report` or `full report` or `generate report` | Full Pipeline | Discovery → snapshot → rank → harvest → scripts → output |
| `snapshot` or `daily snapshot` | Snapshot Only | Record ClawHub metrics to DB (no scripts) |
| `trending` or `what's trending` | Quick Trending | Show top 10 from existing DB data |
| `status` or `db status` | Status | Show DB health and snapshot history |
| `video script` or `generate script` | Script Only | Re-generate scripts from last snapshot (no re-fetch) |

## Full Pipeline (Weekly Report)

First, install dependencies if not already present:

```bash
cd "${SKILL_ROOT}" && pip install -r requirements.txt --quiet 2>/dev/null || pip3 install -r requirements.txt --quiet
```

Then run the full pipeline:

```bash
cd "${SKILL_ROOT}" && python3 run_weekly.py --top 10 --episode ${EPISODE_NUM:-1}
```

Replace `${EPISODE_NUM}` with the episode number the user specifies, or default to 1.

If the user says `--skip-x` or doesn't want X/Twitter capture, add `--skip-x`:

```bash
cd "${SKILL_ROOT}" && python3 run_weekly.py --top 10 --skip-x --episode ${EPISODE_NUM:-1}
```

**What this produces:**
- `openclaw_weekly_YYYYMMDD.md` — Data-rich markdown report with metrics, rankings, and scripts
- `openclaw_weekly_YYYYMMDD_script.txt` — Voice-ready video script in GitHubAwesome format

Present both file paths to the user when done.

**Expected output:**
```
============================================================
  OpenClaw Skills Weekly — Full Pipeline (v4)
  Week of Mar 01, 2026
============================================================
  PHASE 1: X/Twitter Signal Capture
  PHASE 2: ClawHub Data Pipeline
  [1/5] Discovering ClawHub skills...
  [2/5] Saving snapshot...
  [3/5] Ranking by 7-day velocity...
  [4/5] Harvesting content...
  [5/5] Generating YouTube scripts...
  DONE:
    Report: openclaw_weekly_20260301.md
    Script: openclaw_weekly_20260301_script.txt
```

## Snapshot Only (Daily Cron)

For daily snapshot accumulation without script generation:

```bash
cd "${SKILL_ROOT}" && python3 run_weekly.py --snapshot-only --skip-x
```

Tell the user how many skills were captured and how many snapshot dates exist in the DB.

## Quick Trending

Show what's trending from existing DB data without re-fetching:

```bash
cd "${SKILL_ROOT}" && python3 main.py --list-db
```

## Status

```bash
cd "${SKILL_ROOT}" && python3 main.py --list-db
```

Shows: DB path, total snapshot rows, distinct dates, top skills by current installs.

## CLI Options Reference

| Flag | Default | Description |
|---|---|---|
| `--top N` | 10 | Number of top movers to include |
| `--days N` | 7 | Trailing days for velocity calculation |
| `--episode N` | 1 | Episode number for video script cold open |
| `--skip-x` | false | Skip X/Twitter signal capture |
| `--snapshot-only` | false | Just record snapshot, no scripts |
| `--max-pages N` | 0 (all) | Limit API pages (for testing) |
| `--model MODEL` | claude-haiku-4-5-20251001 | Anthropic model for script gen |
| `--output FILE` | auto-dated | Custom output file path |
| `--mock` | false | Use synthetic data (offline dev) |

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | For YouTube script generation via Claude |
| `GITHUB_TOKEN` | No | For fetching source READMEs from GitHub |
| `XAI_API_KEY` | No | For X/Twitter signal capture via xAI |
| `CLAWHUB_BASE_URL` | No | Override ClawHub URL (default: https://clawhub.ai) |

## Video Script Format

Scripts follow the GitHubAwesome "GitHub Trending Weekly" format:
- **Cold open**: "It is time for OpenClaw Skills Weekly, episode number N..."
- **Per-skill segments** (~20 sec each): Hook first → technical specs → sharp closer
- **No popularity metrics** in narration (no download/install/star counts)
- **Dry, confident newscast tone** — no hype, no superlatives
- **No outro** — last item ends the episode

## Architecture

```
run_weekly.py          # Full pipeline orchestrator
main.py                # Alternative CLI with --list-db
discovery.py           # ClawHub API cursor pagination (~13K skills)
storage.py             # SQLite time-series (slug-scoped dedup, CTE velocity)
ranker.py              # Two-track: Movers + Rockets, author diversity cap
harvester.py           # ClawHub detail API content + author extraction
script_generator.py    # LLM script gen + markdown + video script rendering
community_signals.py   # X/Twitter signal loading and rendering
x_capture.py           # xAI x_search API integration
data/metrics.db        # SQLite database (auto-created)
```
