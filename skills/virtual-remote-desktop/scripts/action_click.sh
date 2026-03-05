#!/usr/bin/env bash
set -euo pipefail

X="${1:-}"
Y="${2:-}"
BUTTON="${3:-left}"
if [[ -z "${X}" || -z "${Y}" ]]; then
  echo "Usage: $0 <x> <y> [left|right|middle|double|triple]" >&2
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

xdotool mousemove --sync "${X}" "${Y}"

case "${BUTTON}" in
  left) xdotool click 1 ;;
  right) xdotool click 3 ;;
  middle) xdotool click 2 ;;
  double) xdotool click --repeat 2 --delay 100 1 ;;
  triple) xdotool click --repeat 3 --delay 100 1 ;;
  *) echo "[ERR] unknown button: ${BUTTON}" >&2; exit 1 ;;
esac

echo "clicked:${BUTTON}@${X},${Y}"

sleep 1
exec "$(dirname "$0")/action_screenshot.sh"
