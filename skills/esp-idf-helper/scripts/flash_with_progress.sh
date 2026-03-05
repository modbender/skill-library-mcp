#!/usr/bin/env bash
set -euo pipefail

# Real-time flash with progress + optional usbipd auto-attach retries
# Supports automatic second retry on serial disconnect/open failures.

PROJECT_DIR=""
IDF_DIR=""
PORT="/dev/ttyACM0"
BAUD="1152000"
MODE="flash" # flash | app-flash | encrypted-app-flash | encrypted-flash | partition-table-flash | storage-flash
KEYWORD="ESP32"
AUTO_ATTACH=1
RETRIES=2

usage(){
  cat <<'EOF'
Usage:
  flash_with_progress.sh --project <PROJECT_DIR> --idf <IDF_DIR> [--port <PORT>] [--baud <BAUD>] [--mode <MODE>] [--keyword <TEXT>] [--retries <N>] [--no-auto-attach]

Modes:
  flash | app-flash | encrypted-app-flash | encrypted-flash | partition-table-flash | storage-flash

Notes:
  - Retries are full re-run retries (cannot resume partial esptool writes).
  - Progress is printed in real time (Writing at ... xx%).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT_DIR="$2"; shift 2;;
    --idf) IDF_DIR="$2"; shift 2;;
    --port) PORT="$2"; shift 2;;
    --baud) BAUD="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --keyword) KEYWORD="$2"; shift 2;;
    --retries) RETRIES="$2"; shift 2;;
    --no-auto-attach) AUTO_ATTACH=0; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 2;;
  esac
done

[[ -n "$PROJECT_DIR" && -n "$IDF_DIR" ]] || { usage; exit 2; }

BASE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
ATTACH="$BASE_DIR/scripts/usbipd_attach_serial.sh"

run_flash(){
  cd "$PROJECT_DIR"
  # shellcheck disable=SC1090
  source "$IDF_DIR/export.sh"
  stdbuf -oL -eL idf.py -p "$PORT" -b "$BAUD" "$MODE"
}

is_retryable_error(){
  local log="$1"
  grep -Eiq "Could not open .*${PORT}|Could not exclusively lock port|Resource temporarily unavailable|No such file or directory: '${PORT}'|Serial port ${PORT}|failed to connect|connection closed|No /dev/ttyACM|No /dev/ttyUSB" "$log"
}

print_error_summary(){
  local log="$1"
  echo "[error] 失败关键信息："
  grep -Ei "fatal|error|failed|Could not open|No such file|Resource temporarily unavailable|CMake Error|ninja failed" "$log" | tail -n 20 || true
}

attempt=0
max_attempts=$((RETRIES + 1))

while (( attempt < max_attempts )); do
  attempt=$((attempt + 1))
  echo "[flash] attempt ${attempt}/${max_attempts}: mode=${MODE}, port=${PORT}, baud=${BAUD}"

  log_file=$(mktemp /tmp/flash_with_progress.XXXXXX.log)
  set +e
  run_flash 2>&1 | tee "$log_file"
  rc=${PIPESTATUS[0]}
  set -e

  if [[ $rc -eq 0 ]]; then
    echo "[flash] success on attempt ${attempt}/${max_attempts}"
    rm -f "$log_file"
    exit 0
  fi

  print_error_summary "$log_file"

  if [[ $AUTO_ATTACH -eq 1 ]] && is_retryable_error "$log_file" && (( attempt < max_attempts )); then
    echo "[auto] 检测到串口/连接异常，执行 usbipd 映射后重试..."
    bash "$ATTACH" --keyword "$KEYWORD" || true
    sleep 2
    rm -f "$log_file"
    continue
  fi

  echo "[flash] 失败且不再重试（rc=$rc）"
  rm -f "$log_file"
  exit $rc
done
