# End-of-Day Checkpoint — Cron Job Template
# ⚠️  OPT-IN ONLY: This template is NOT auto-installed.
# The user must explicitly request cron setup ("set up cron jobs")
# and approve the exec command when prompted.
# This skill does not install cron jobs automatically. The agent presents the command via exec for user approval.
#
# Requires: openclaw CLI (pre-installed with OpenClaw)
# Effect: Creates a scheduled job that runs daily at 6 PM
# Scope: Runs in an isolated session — reads/writes workspace files only
# Network: No network activity — reads local files only
#
# Writes a full context checkpoint and reviews the day
# Schedule: Daily at 6 PM (adjust timezone)
#
# Usage:
#   The agent will run this via exec. Review and approve when prompted.
#   Change --tz to your timezone.

openclaw cron add \
  --name "ai-persona-eod-checkpoint" \
  --cron "0 18 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "End-of-day checkpoint protocol:

1. Write a full checkpoint to today's memory log with all decisions, action items, and open threads.

2. Review MEMORY.md — promote any repeated learnings from today. Prune anything stale or no longer relevant.

3. Check .learnings/ — any pending items with 3+ repetitions? Promote to MEMORY.md or AGENTS.md.

4. Deliver a brief end-of-day summary: what was accomplished, what carries over to tomorrow, and any blockers.

Use 🟢🟡🔴 indicators for system health. Keep it concise." \
  --announce
