#!/usr/bin/env bash
set -euo pipefail

KEYS="${1:-}"
if [[ -z "${KEYS}" ]]; then
  echo "Usage: $0 <key-or-combo>   e.g. Return | ctrl+l | alt+F4" >&2
  exit 1
fi

WORKDIR="${WORKDIR:-$HOME/.openclaw/vrd-data}"
PIDFILE="${WORKDIR}/pids.env"

if [[ ! -f "${PIDFILE}" ]]; then
  echo "[ERR] pidfile not found: ${PIDFILE}" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${PIDFILE}"
export DISPLAY="${DISPLAY:-:${DISPLAY_NUM:-55}}"
if [[ -z "${XAUTHORITY:-}" && -n "${KASM_HOME:-}" && -f "${KASM_HOME}/.Xauthority" ]]; then
  export XAUTHORITY="${KASM_HOME}/.Xauthority"
fi

xdotool key --clearmodifiers "${KEYS}"
echo "key:${KEYS}"

sleep 1
exec "$(dirname "$0")/action_screenshot.sh"
