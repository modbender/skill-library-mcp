# Nightly Build 🌙

An automation skill that runs maintenance tasks while you sleep and delivers a morning briefing.

Inspired by [The Nightly Build](https://www.moltbook.com/post/562faad7-f9cc-49a3-8520-2bdf362606bb).

## Commands

- `nightly report` — Show the last nightly build report.
- `nightly run` — Trigger a manual run (for testing).
- `nightly config` — Configure tasks (update skills, check disk, etc.).

## Tasks

- 📦 **Skill Audit**: Run `npm audit` on installed skills.
- 🔄 **Auto-Update**: Pull latest changes from git repos.
- 🧹 **Cleanup**: Remove temporary files and old logs.
- 📊 **Health Check**: Verify disk space and system load.
- 📝 **Briefing**: Summarize everything into a morning report.

## Setup

Add this to your cron (e.g., via `openclaw cron add`):
```json
{
  "schedule": { "kind": "cron", "expr": "0 3 * * *", "tz": "Asia/Shanghai" },
  "payload": { "kind": "agentTurn", "message": "Run nightly build tasks and generate report." }
}
```
