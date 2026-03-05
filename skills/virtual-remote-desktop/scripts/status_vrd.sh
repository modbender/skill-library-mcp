#!/usr/bin/env bash
set -euo pipefail

WORKDIR="${WORKDIR:-$HOME/.openclaw/vrd-data}"
PIDFILE="${WORKDIR}/pids.env"

is_alive() {
  local pid="$1"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
    echo "up (${pid})"
  else
    echo "down"
  fi
}

if [[ ! -f "${PIDFILE}" ]]; then
  echo "status: down (no pidfile)"
  exit 1
fi

# shellcheck disable=SC1090
source "${PIDFILE}"

KASM_USER_VALUE="${KASM_USER:-}"
if [[ -z "${KASM_USER_VALUE}" && -f "${KASM_USER_FILE:-}" ]]; then
  KASM_USER_VALUE="$(tr -d '\r\n' < "${KASM_USER_FILE}" || true)"
fi

COOKIE_FILE="${CHROME_PROFILE_DIR:-}/Default/Cookies"
LOGIN_STATE="missing"
if [[ -f "${COOKIE_FILE}" ]]; then
  LOGIN_STATE="present"
fi

URL_HOST="127.0.0.1"
if [[ "${KASM_BIND:-127.0.0.1}" == "0.0.0.0" ]]; then
  URL_HOST="${PUBLIC_HOST:-0.0.0.0}"
fi

echo "status:"
echo "  kasmvnc:   $(is_alive "${KASM_PID:-}")"
echo "  watcher:   $(is_alive "${WATCHER_PID:-}")"
echo "  chrome:    $(is_alive "${CHROME_PID:-}")"
echo "  display:   ${DISPLAY:-unknown}"
echo "  geom:      ${GEOM:-unknown}"
echo "  depth:     ${DEPTH:-unknown}"
echo "  max_fps:   ${KASM_MAX_FPS:-unknown}"
echo "  mobile:    mode=${MOBILE_MODE:-0} preset=${MOBILE_PRESET:-phone}"
echo "  bind:      ${KASM_BIND:-unknown}"
echo "  web_port:  ${KASM_PORT:-unknown}"
echo "  rfb_port:  ${RFB_PORT:-unknown}"
echo "  user:      ${KASM_USER_VALUE:-unknown}"
echo "  profile:   ${CHROME_PROFILE_DIR:-unknown}"
echo "  browser_mobile: mode=${BROWSER_MOBILE_MODE:-0} device=${BROWSER_DEVICE:-iphone14pro}"
echo "  cookies:   ${LOGIN_STATE} (${COOKIE_FILE})"
echo "  url:       https://${URL_HOST}:${KASM_PORT:-unknown}/"
echo "  pidfile:   ${PIDFILE}"
