#!/usr/bin/env bash
set -euo pipefail

TEXT="${1:-}"
if [[ -z "${TEXT}" ]]; then
  echo "Usage: $0 \"text\"" >&2
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

CHUNK=50
LEN=${#TEXT}
OFF=0
while [ $OFF -lt $LEN ]; do
  PART="${TEXT:$OFF:$CHUNK}"
  xdotool type --delay 12 -- "${PART}"
  OFF=$((OFF + CHUNK))
done

echo "typed:${LEN}"

sleep 1
exec "$(dirname "$0")/action_screenshot.sh"
