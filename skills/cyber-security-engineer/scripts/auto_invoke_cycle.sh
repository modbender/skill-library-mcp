#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASSESS_DIR="${SKILL_DIR}/assessments"
ASSESS_FILE="${ASSESS_DIR}/openclaw-assessment.json"
HTML_OUT="${ASSESS_DIR}/compliance-dashboard.html"
SUMMARY_OUT="${ASSESS_DIR}/compliance-summary.json"
PORT_OUT="${ASSESS_DIR}/port-monitor-latest.json"
EGRESS_OUT="${ASSESS_DIR}/egress-monitor-latest.json"
LOG_DIR="${HOME}/.openclaw/logs"
RUN_LOG="${LOG_DIR}/cyber-security-engineer-auto.log"

mkdir -p "${LOG_DIR}" "${ASSESS_DIR}"

{
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting auto security cycle"

  if [[ ! -f "${ASSESS_FILE}" ]]; then
    python3 "${SKILL_DIR}/scripts/compliance_dashboard.py" init-assessment --system "OpenClaw" --output "${ASSESS_FILE}"
  fi

  python3 "${SKILL_DIR}/scripts/live_assessment.py" --assessment-file "${ASSESS_FILE}"
  python3 "${SKILL_DIR}/scripts/compliance_dashboard.py" render \
    --assessment-file "${ASSESS_FILE}" \
    --output-html "${HTML_OUT}" \
    --output-summary "${SUMMARY_OUT}"
  # Optional: notify when new violations/partials appear between cycles.
  python3 "${SKILL_DIR}/scripts/notify_on_violation.py" --summary-file "${SUMMARY_OUT}" || true
  python3 "${SKILL_DIR}/scripts/port_monitor.py" --json > "${PORT_OUT}"
  python3 "${SKILL_DIR}/scripts/egress_monitor.py" --json > "${EGRESS_OUT}"

  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Completed auto security cycle"
} >> "${RUN_LOG}" 2>&1
