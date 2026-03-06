#!/usr/bin/env bash
set -euo pipefail

REPO_PATH=${1:-}
shift || true

AGENT_ID="persey"
TZ="Europe/Minsk"
TIME="10:00"
NAME="daily-pm-review"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT_ID="$2"; shift 2;;
    --tz) TZ="$2"; shift 2;;
    --time) TIME="$2"; shift 2;;
    --name) NAME="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

if [[ -z "$REPO_PATH" ]]; then
  echo "Usage: add_daily_pm_cron.sh /absolute/path/to/repo [--agent persey] [--tz Europe/Minsk] [--time 10:00] [--name daily-pm-review]" >&2
  exit 1
fi

# TIME HH:MM
HH=${TIME%:*}
MM=${TIME#*:}

CRON_EXPR="${MM} ${HH} * * *"

openclaw cron add \
  --name "${NAME}" \
  --agent "${AGENT_ID}" \
  --cron "${CRON_EXPR}" \
  --tz "${TZ}" \
  --announce \
  --description "Daily PM audit for repo: ${REPO_PATH}" \
  --message "Run daily PM review for repo: ${REPO_PATH}\n\nProcess:\n1) Read docs/roadmap/ROADMAP.md\n2) Read docs/features/*/KANBAN.md\n3) Scan docs/pm/bugs/*.md and ensure each open bug is linked from a feature KANBAN\n4) gh pr list + check recent commits\n5) Ensure KANBAN + ROADMAP reflect reality\n6) Run lightweight checks (if applicable): cd apps/telegram && npx tsc --noEmit\n7) Post report: Done/In progress/Open bugs/Blocked/Risks/Next"

echo "Cron created: ${NAME} (${CRON_EXPR} ${TZ})"