#!/usr/bin/env bash
set -euo pipefail

WORKDIR="${WORKDIR:-$HOME/.openclaw/vrd-data}"
PIDFILE="${WORKDIR}/pids.env"
KILL_BROWSER="${KILL_BROWSER:-0}"

kill_if_alive() {
  local pid="$1"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}" 2>/dev/null || true
  fi
}

run_with_ssl_group() {
  if id -nG | tr ' ' '\n' | grep -qx 'ssl-cert'; then
    "$@"
    return
  fi
  if id -nG "$USER" | tr ' ' '\n' | grep -qx 'ssl-cert'; then
    local cmd
    printf -v cmd '%q ' "$@"
    sg ssl-cert -c "$cmd"
    return
  fi
  "$@"
}

if [[ -f "${PIDFILE}" ]]; then
  # shellcheck disable=SC1090
  source "${PIDFILE}"

  kill_if_alive "${WATCHER_PID:-}"

  if [[ -n "${DISPLAY_NUM:-}" ]]; then
    run_with_ssl_group env HOME="${KASM_HOME:-$HOME/.openclaw/vrd-data/kasm-home}" vncserver -kill ":${DISPLAY_NUM}" >/dev/null 2>&1 || true
  fi

  kill_if_alive "${KASM_PID:-}"

  if [[ "${KILL_BROWSER}" == "1" && -n "${CHROME_PROFILE_DIR:-}" ]]; then
    pkill -f "--user-data-dir=${CHROME_PROFILE_DIR}" 2>/dev/null || true
  else
    kill_if_alive "${CHROME_PID:-}"
  fi

  rm -f "${PIDFILE}" 2>/dev/null || true
  rm -f "${KASM_SECRET_FILE:-}" "${KASM_USER_FILE:-}" "${KASM_PASS_FILE:-}" 2>/dev/null || true
else
  echo "[WARN] PIDFILE not found: ${PIDFILE}"
fi

# Fallback cleanup for stale processes
pkill -f "Xvnc :${DISPLAY_NUM:-55}" 2>/dev/null || true
rm -f "/tmp/.X${DISPLAY_NUM:-55}-lock" "/tmp/.X11-unix/X${DISPLAY_NUM:-55}" 2>/dev/null || true

echo "Stopped virtual remote desktop stack."
