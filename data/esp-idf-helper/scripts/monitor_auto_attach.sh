#!/usr/bin/env bash
set -euo pipefail

# Auto monitor helper:
# 1) Try idf.py monitor
# 2) If serial open/lock fails, auto-run usbipd_attach_serial.sh and retry once

PORT="${PORT:-/dev/ttyACM0}"
BAUD="${BAUD:-1152000}"
PROJECT_DIR="${PROJECT_DIR:-/path/to/your/project}"
IDF_DIR="${IDF_DIR:-/path/to/esp-idf}"
DISTRO="${DISTRO:-}"
KEYWORD="${KEYWORD:-ESP32}"

usage() {
  cat <<'EOF'
Usage:
  monitor_auto_attach.sh --project <PROJECT_DIR> --idf <IDF_DIR> [--port <PORT>] [--baud <BAUD>] [--distro <DISTRO>] [--keyword <TEXT>]

Example:
  bash monitor_auto_attach.sh \
    --project /path/to/your/project \
    --idf /path/to/esp-idf \
    --port /dev/ttyACM0 \
    --baud 1152000 \
    --keyword ESP32
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT_DIR="$2"; shift 2;;
    --idf) IDF_DIR="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    --baud) BAUD="$2"; shift 2;;
    --distro) DISTRO="$2"; shift 2;;
    --keyword) KEYWORD="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ "$PROJECT_DIR" == "/path/to/your/project" || "$IDF_DIR" == "/path/to/esp-idf" ]]; then
  echo "Error: please set --project and --idf" >&2
  usage
  exit 2
fi

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)
ATTACH_SCRIPT="$BASE_DIR/scripts/usbipd_attach_serial.sh"

run_monitor() {
  cd "$PROJECT_DIR"
  # shellcheck disable=SC1090
  source "$IDF_DIR/export.sh"
  idf.py -p "$PORT" -b "$BAUD" monitor
}

set +e
OUT=$(run_monitor 2>&1)
RC=$?
set -e

if [[ $RC -eq 0 ]]; then
  echo "$OUT"
  exit 0
fi

if echo "$OUT" | grep -Eq "Could not open .*${PORT}|Could not exclusively lock port|Resource temporarily unavailable|No such file or directory: '${PORT}'"; then
  echo "[auto] monitor open failed, trying usbipd auto-attach..."
  cmd=(bash "$ATTACH_SCRIPT" --keyword "$KEYWORD")
  if [[ -n "$DISTRO" ]]; then
    cmd+=(--distro "$DISTRO")
  fi
  "${cmd[@]}"
  sleep 2
  echo "[auto] retry monitor..."
  exec bash -lc "cd '$PROJECT_DIR' && source '$IDF_DIR/export.sh' && idf.py -p '$PORT' -b '$BAUD' monitor"
fi

echo "$OUT"
exit $RC
