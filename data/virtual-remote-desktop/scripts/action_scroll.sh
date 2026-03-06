#!/usr/bin/env bash
set -euo pipefail

DIR="${1:-}"
AMOUNT="${2:-3}"
X="${3:-}"
Y="${4:-}"

if [[ -z "${DIR}" ]]; then
  echo "Usage: $0 <up|down|left|right> [amount] [x y]" >&2
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

if [[ -n "${X}" && -n "${Y}" ]]; then
  xdotool mousemove --sync "${X}" "${Y}"
fi

case "${DIR}" in
  up) BTN=4 ;;
  down) BTN=5 ;;
  left) BTN=6 ;;
  right) BTN=7 ;;
  *) echo "[ERR] unknown direction: ${DIR}" >&2; exit 1 ;;
esac

xdotool click --repeat "${AMOUNT}" "${BTN}"
echo "scrolled:${DIR}x${AMOUNT}"

sleep 1
exec "$(dirname "$0")/action_screenshot.sh"
