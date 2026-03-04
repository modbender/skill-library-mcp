# Morning Briefing — Cron Job Template
# ⚠️  OPT-IN ONLY: This template is NOT auto-installed.
# The user must explicitly request cron setup ("set up cron jobs")
# and approve the exec command when prompted.
# This skill does not install cron jobs automatically. The agent presents the command via exec for user approval.
#
# Requires: openclaw CLI (pre-installed with OpenClaw)
# Effect: Creates a scheduled job that runs daily at 8 AM
# Scope: Runs in an isolated session — reads workspace files only
# Network: No network activity — reads local files only
#
# Runs the full 4-step AI Persona OS daily protocol
# Schedule: Daily at 8 AM (adjust timezone)
#
# Usage:
#   The agent will run this via exec. Review and approve when prompted.
#   Change --tz to your timezone.
#   Change --announce to --no-deliver if you want internal-only processing.

openclaw cron add \
  --name "ai-persona-morning-briefing" \
  --cron "0 8 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Run the AI Persona OS daily protocol:

Step 1: Load previous context — Read today's and yesterday's memory logs. Summarize key state, pending items, and open threads.

Step 2: System status — Check MEMORY.md size (<4KB), workspace structure, stale logs (>90 days), and file accessibility.

Step 3: Priority scan — Check channels in priority order (P1 critical → P4 background). Surface anything requiring attention.

Step 4: Assessment — Summarize system health, blocking issues, time-sensitive items, and recommended first action.

Format as a daily briefing. Use 🟢🟡🔴 indicators for each section. End with today's top 3 priorities." \
  --announce
