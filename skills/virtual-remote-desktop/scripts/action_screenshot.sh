#!/usr/bin/env bash
set -euo pipefail

WORKDIR="${WORKDIR:-$HOME/.openclaw/vrd-data}"
PIDFILE="${WORKDIR}/pids.env"
OUT_DIR="${OUT_DIR:-${WORKDIR}/shots}"
mkdir -p "${OUT_DIR}"

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

TS="$(date +%s%N)"
FILE="${OUT_DIR}/shot_${TS}.png"
scrot -o "${FILE}" 2>/dev/null

if [[ ! -f "${FILE}" ]]; then
  echo "[ERR] failed to capture screenshot" >&2
  exit 1
fi

if [[ "${SAVE_FILE_ONLY:-0}" == "1" ]]; then
  echo "${FILE}"
else
  base64 -w0 "${FILE}"
fi
