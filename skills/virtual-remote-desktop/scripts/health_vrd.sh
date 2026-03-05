#!/usr/bin/env bash
set -euo pipefail

WORKDIR="${WORKDIR:-$HOME/.openclaw/vrd-data}"
PIDFILE="${WORKDIR}/pids.env"

if [[ ! -f "${PIDFILE}" ]]; then
  echo "[ERR] pidfile not found: ${PIDFILE}"
  exit 1
fi

# shellcheck disable=SC1090
source "${PIDFILE}"

ok() { echo "[OK] $*"; }
warn() { echo "[WARN] $*"; }
err() { echo "[ERR] $*"; }

check_pid() {
  local name="$1" pid="$2"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    ok "${name} pid ${pid} alive"
  else
    err "${name} not running"
  fi
}

check_pid "kasmvnc" "${KASM_PID:-}"

HTTP_CODE="$(curl -k -s -o /dev/null -w "%{http_code}" "https://127.0.0.1:${KASM_PORT}/" || true)"
if [[ "${HTTP_CODE}" == "200" || "${HTTP_CODE}" == "401" ]]; then
  ok "KasmVNC endpoint reachable (HTTP ${HTTP_CODE})"
else
  err "KasmVNC endpoint unreachable (HTTP ${HTTP_CODE:-n/a})"
fi

if [[ -n "${KASM_USER_FILE:-}" && -f "${KASM_USER_FILE}" ]]; then
  ok "user file exists: ${KASM_USER_FILE}"
else
  err "user file missing: ${KASM_USER_FILE:-unset}"
fi

if [[ -n "${KASM_SECRET_FILE:-}" && -f "${KASM_SECRET_FILE}" ]]; then
  ok "secret file exists: ${KASM_SECRET_FILE}"
else
  err "secret file missing: ${KASM_SECRET_FILE:-unset}"
fi

COOKIE_FILE="${CHROME_PROFILE_DIR:-}/Default/Cookies"
if [[ -f "${COOKIE_FILE}" ]]; then
  ok "chrome cookies file exists: ${COOKIE_FILE}"
else
  warn "chrome cookies file missing: ${COOKIE_FILE}"
fi

if [[ -f "${LOGDIR:-}/kasmvnc-start.log" ]]; then
  ok "startup log exists: ${LOGDIR}/kasmvnc-start.log"
fi

echo "health check complete"
