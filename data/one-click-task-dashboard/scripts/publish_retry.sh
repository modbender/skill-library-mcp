#!/bin/zsh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="${HOME}/.openclaw/logs"
LOG_FILE="${LOG_DIR}/one-click-task-dashboard-publish.log"
MAX_TRIES="${MAX_TRIES:-24}"
SLEEP_SECONDS="${SLEEP_SECONDS:-300}"

mkdir -p "${LOG_DIR}"
echo "[$(date '+%F %T')] start publish retry" >> "${LOG_FILE}"

for ((i=1; i<=MAX_TRIES; i++)); do
  echo "[$(date '+%F %T')] attempt ${i}/${MAX_TRIES}" >> "${LOG_FILE}"
  if bash "${SKILL_DIR}/scripts/publish_to_clawhub.sh" >> "${LOG_FILE}" 2>&1; then
    /usr/bin/osascript -e 'display notification "one-click-task-dashboard 已发布，请到 ClawHub 设置售价100元" with title "X小姐提醒"' >/dev/null 2>&1 || true
    echo "[$(date '+%F %T')] publish success" >> "${LOG_FILE}"
    exit 0
  fi
  if rg -qi "rate limit" "${LOG_FILE}"; then
    sleep "${SLEEP_SECONDS}"
    continue
  fi
  echo "[$(date '+%F %T')] non-rate-limit failure, stop retry" >> "${LOG_FILE}"
  exit 1
done

echo "[$(date '+%F %T')] exhausted retries" >> "${LOG_FILE}"
exit 1
