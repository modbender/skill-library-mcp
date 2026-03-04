---
name: agent-health-optimizer
description: "Automated agent diagnostics and self-optimization toolkit for OpenClaw. Run one command to score your agent's health (0-100, grade A+ to F), audit memory hygiene, detect cron job issues, and compare installed skills against ClawHub. Set up a weekly cron for continuous self-improvement with trend tracking. Use when you want to diagnose agent problems, optimize your setup, check for better skills, or automate periodic health checks."
metadata:
  openclaw:
    requires:
      bins: ["openclaw", "python3"]
---

# Agent Health Optimizer

**Diagnose, score, and continuously optimize your OpenClaw agent.**

One command tells you exactly what's wrong and how to fix it. Set up a weekly cron and your agent gets better on its own.

## Requirements

- **python3** (3.8+)
- **openclaw CLI** (for cron job analysis)

## Quick Start

```bash
# Full diagnostic suite — one command
python3 scripts/self_optimize.py

# Individual tools
python3 scripts/health_score.py        # Health grade (A+ to F)
python3 scripts/memory_auditor.py      # Memory hygiene check
python3 scripts/cron_optimizer.py      # Cron job analysis
python3 scripts/cron_optimizer.py --fix # Auto-repair (backs up first)
python3 scripts/skill_comparator.py    # Compare vs ClawHub catalog
```

## What It Does

### 🏥 health_score.py — Agent Health Grade (0-100)

Scores 5 dimensions:

- **🧠 Memory (25pts)**: MEMORY.md completeness, daily log activity, working buffer, anti-poisoning hygiene, source tags
- **⏰ Cron (25pts)**: job health, error states, stagger configuration, time diversity, session isolation, delivery mode
- **📦 Skills (20pts)**: count, redundancy detection, ClawHub management ratio, essential skills
- **🔒 Security (15pts)**: safety rules, anti-poisoning policy, WAL protocol, external action controls
- **🔄 Continuity (15pts)**: SOUL.md, USER.md, HEARTBEAT.md, IDENTITY.md, git tracking

Letter grade from A+ (90+) to F (<50).

### 🔍 memory_auditor.py — Memory Hygiene

Detects:
- **Imperative rules** that should be declarative facts (anti-poisoning)
- **Missing source tags** on factual entries
- **Stale entries** >30 days with pending status
- **External content** stored as instructions (injection risk)
- **Oversized files** needing archival
- **Daily log** gaps

### ⏰ cron_optimizer.py — Cron Job Doctor

Detects:
- **Error states** with job names and error messages
- **Time collisions** (multiple jobs on same schedule)
- **Missing stagger/jitter** (API stampede risk)
- **Announce duplication** (user gets message twice)
- **Timeout mismatches** (complex jobs with short timeouts)
- **Session target** recommendations (isolated vs main)

`--fix` mode: creates `memory/cron-backup.json` before any changes, then auto-applies stagger and disables duplicate announce.

### 📦 skill_comparator.py — Skill Quality Checker

Via ClawHub API (`https://clawhub.ai/api/v1/`):
- Fetches stars, downloads, installs for all installed skills
- Lists top ClawHub skills you're missing
- Finds upgrades: same-category skills with higher community rating
- Category coverage analysis (what domains are you missing?)
- Uses semantic categorization (15+ categories) with slug-weighted matching

### 🔄 self_optimize.py — Unified Runner

Runs all 4 tools, produces:
- Combined report with prioritized action items (HIGH/MED/LOW)
- Trend tracking: compares with last run, shows score change (📈/📉)
- All reports saved as JSON in `memory/` for historical analysis

## What It Reads & Writes

**Reads** (non-destructive):
- Workspace files: MEMORY.md, AGENTS.md, SOUL.md, USER.md, HEARTBEAT.md, IDENTITY.md
- Daily logs: `memory/*.md`
- Skill metadata: `skills/*/SKILL.md`
- Cron config: `openclaw cron list --json`
- ClawHub public API: `https://clawhub.ai/api/v1/skills/...`

**Writes** (reports only):
- `memory/health-score.json`
- `memory/memory-audit.json`
- `memory/cron-optimizer.json`
- `memory/skill-comparator.json`
- `memory/self-optimize-report.json`
- `memory/self-optimize-last.json` (trend baseline)

**Modifies** (only with `--fix`):
- `cron_optimizer.py --fix` edits cron jobs via `openclaw cron edit`
- Always backs up to `memory/cron-backup.json` first

## Periodic Self-Optimization

Set up a weekly cron (read-only, no --fix):

```bash
openclaw cron add \
  --name "Agent Self-Optimize" \
  --cron "0 11 * * 0" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --stagger 2m \
  --no-deliver \
  --message "Run agent self-optimization:
python3 ~/.openclaw/workspace/skills/agent-health-optimizer/scripts/self_optimize.py

Report results. If HIGH priority issues exist, list them. Compare health score trend. Keep it brief if everything is fine."
```

⚠️ Cron runs in read-only mode. Review suggested repairs before applying `--fix`.

## Example Output

```
🏥 Agent Health Score: 81/100 (81%) — Grade: A
==================================================
  🧠 Memory: 18/25 [███████░░░]
  ⏰ Cron: 18/25 [███████░░░]
  📦 Skills: 15/20 [███████░░░]
  🔒 Security: 15/15 [██████████]
  🔄 Continuity: 15/15 [██████████]

🎯 PRIORITIZED ACTION ITEMS
  🚨 HIGH: 2 cron jobs in error state
  ⚠️ MED: Time collision on 2 schedules
  💡 LOW: No working-buffer.md

📈 Health trend: +13% since last run
```

## Credits

Diagnostic patterns informed by:
- **[proactive-agent](https://clawhub.ai/halthelobster/proactive-agent)** by halthelobster — WAL Protocol concepts
- **[self-improving-agent](https://clawhub.ai/pskoett/self-improving-agent)** by pskoett — continuous improvement patterns
- **Moltbook openclaw-explorers community** — cron jitter pattern (thoth-ix), heartbeat batching (pinchy_mcpinchface)
