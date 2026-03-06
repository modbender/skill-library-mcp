#!/usr/bin/env bash
set -euo pipefail

X="${1:-}"
Y="${2:-}"
if [[ -z "${X}" || -z "${Y}" ]]; then
  echo "Usage: $0 <x> <y>" >&2
  exit 1
fi

WORKDIR="${WORKDIR:-$HOME/.openclaw/vrd-data}"
PIDFILE="${WORKDIR}/pids.env"

# shellcheck disable=SC1090
source "${PIDFILE}"
export DISPLAY="${DISPLAY:-:${DISPLAY_NUM:-55}}"
if [[ -z "${XAUTHORITY:-}" && -n "${KASM_HOME:-}" && -f "${KASM_HOME}/.Xauthority" ]]; then
  export XAUTHORITY="${KASM_HOME}/.Xauthority"
fi

xdotool mousemove --sync "${X}" "${Y}"
echo "moved:${X},${Y}"
