#!/usr/bin/env bash
set -euo pipefail

# OpenClaw skill: local PrusaLink CLI implemented as a curl wrapper.
# Rationale: avoid pulling remote code at runtime (no uvx), keep deps minimal.

die() { echo "error: $*" >&2; exit 2; }

need_bin() {
  command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"
}

need_bin curl

HOST="${PRUSALINK_HOST:-printer.local}"
SCHEME="${PRUSALINK_SCHEME:-http}"
API_KEY="${PRUSALINK_API_KEY:-}"
USER="${PRUSALINK_USER:-}"
PASSWORD="${PRUSALINK_PASSWORD:-}"
TIMEOUT="${PRUSALINK_TIMEOUT:-10}"

usage() {
  cat <<'EOF'
PrusaLink CLI (curl wrapper)

Usage:
  run.sh [global options] <command> [args...]

Global options:
  --host <host>              (default: $PRUSALINK_HOST or printer.local)
  --scheme <http|https>      (default: $PRUSALINK_SCHEME or http)
  --api-key <key>            Use X-Api-Key auth (if supported by your PrusaLink)
  --user <user>              Digest auth username
  --password <pass>          Digest auth password (avoid; use --password-file)
  --password-file <path>     Read digest password from file
  --timeout <seconds>        curl max-time (default: $PRUSALINK_TIMEOUT or 10)
  -h, --help

Commands:
  status
  job
  cancel <job_id>
  upload <file.gcode> [--remote-name <name>] [--overwrite] [--print-after-upload]
  start <remote.gcode>

Auth:
  - Preferred: Digest auth via PRUSALINK_USER + PRUSALINK_PASSWORD (or --password-file).
  - Optional: PRUSALINK_API_KEY / --api-key (some setups support X-Api-Key).
EOF
}

curl_auth_args=()
curl_header_args=()

base_url() {
  local h="$HOST"
  if [[ "$h" == http://* || "$h" == https://* ]]; then
    echo "${h%/}"
  else
    echo "${SCHEME}://${h}"
  fi
}

read_password_file() {
  local f="$1"
  [[ -f "$f" ]] || die "password file not found: $f"
  # strip trailing newlines
  PASSWORD="$(tr -d '\r\n' < "$f")"
}

set_auth() {
  if [[ -n "$API_KEY" ]]; then
    curl_header_args+=(-H "X-Api-Key: $API_KEY")
    return 0
  fi

  if [[ -n "$USER" && -n "$PASSWORD" ]]; then
    curl_auth_args+=(--digest -u "${USER}:${PASSWORD}")
    return 0
  fi

  die "no auth configured. Set PRUSALINK_USER+PRUSALINK_PASSWORD (or --password-file), or PRUSALINK_API_KEY."
}

curl_json() {
  # shellcheck disable=SC2206
  curl -sS --fail-with-body --max-time "$TIMEOUT" "${curl_auth_args[@]}" "${curl_header_args[@]}" "$@"
}

# Parse globals.
ARGS=()
while (($#)); do
  case "$1" in
    --host) HOST="${2:-}"; shift 2;;
    --scheme) SCHEME="${2:-}"; shift 2;;
    --api-key) API_KEY="${2:-}"; shift 2;;
    --user) USER="${2:-}"; shift 2;;
    --password) PASSWORD="${2:-}"; shift 2;;
    --password-file) read_password_file "${2:-}"; shift 2;;
    --timeout) TIMEOUT="${2:-}"; shift 2;;
    -h|--help) usage; exit 0;;
    *) ARGS+=("$1"); shift;;
  esac
done

[[ ${#ARGS[@]} -ge 1 ]] || { usage; exit 2; }

CMD="${ARGS[0]}"

set_auth

BASE="$(base_url)"

case "$CMD" in
  status)
    curl_json "$BASE/api/v1/status"
    ;;
  job)
    curl_json "$BASE/api/v1/job"
    ;;
  cancel)
    [[ ${#ARGS[@]} -ge 2 ]] || die "cancel requires <job_id>"
    curl_json -X DELETE "$BASE/api/v1/job/${ARGS[1]}"
    ;;
  upload)
    [[ ${#ARGS[@]} -ge 2 ]] || die "upload requires <file.gcode>"
    FILE="${ARGS[1]}"
    [[ -f "$FILE" ]] || die "file not found: $FILE"

    REMOTE_NAME="$(basename "$FILE")"
    OVERWRITE=0
    PAAU=0

    i=2
    while [[ $i -lt ${#ARGS[@]} ]]; do
      case "${ARGS[$i]}" in
        --remote-name) REMOTE_NAME="${ARGS[$((i+1))]:-}"; i=$((i+2));;
        --overwrite) OVERWRITE=1; i=$((i+1));;
        --print-after-upload) PAAU=1; i=$((i+1));;
        *) die "unknown upload arg: ${ARGS[$i]}";;
      esac
    done

    headers=(-H "Content-Type: application/octet-stream")
    if [[ $OVERWRITE -eq 1 ]]; then headers+=(-H "Overwrite: ?1"); fi
    if [[ $PAAU -eq 1 ]]; then headers+=(-H "Print-After-Upload: ?1"); fi

    curl -sS --fail-with-body --max-time "$TIMEOUT" \
      "${curl_auth_args[@]}" "${curl_header_args[@]}" \
      "${headers[@]}" \
      -X PUT --data-binary "@$FILE" \
      "$BASE/api/v1/files/usb/$REMOTE_NAME" >/dev/null

    echo "{\"uploaded\": \"${REMOTE_NAME}\"}"
    ;;
  start)
    [[ ${#ARGS[@]} -ge 2 ]] || die "start requires <remote.gcode>"
    curl_json -X POST "$BASE/api/v1/files/usb/${ARGS[1]}" >/dev/null
    echo "{\"started\": \"${ARGS[1]}\"}"
    ;;
  *)
    die "unknown command: $CMD (use --help)"
    ;;
esac
