#!/usr/bin/env bash
set -euo pipefail

# Starling Home Hub Developer Connect API wrapper
# Requires: STARLING_HUB_IP and STARLING_API_KEY env vars
#
# RATE LIMITS (enforced by Nest cloud):
#   - POST /devices/{id}        : max once per second
#   - GET  /devices/{id}/snapshot: max once per 10 seconds
# Exceeding these will result in errors from the hub.

HUB_IP="${STARLING_HUB_IP:-}"
API_KEY="${STARLING_API_KEY:-}"
USE_HTTPS=true   # HTTPS by default for security
RAW_OUTPUT=false
KEY_FROM_CLI=false
CACERT=""

# Curl timeouts to prevent hanging
CURL_TIMEOUT=(--connect-timeout 5 --max-time 30)

usage() {
  cat <<'EOF'
Usage: starling.sh [options] <command> [args...]

Options:
  --ip <IP>        Hub IP (default: $STARLING_HUB_IP)
  --key <KEY>      API key (WARNING: visible in process list; prefer $STARLING_API_KEY)
  --http           Use HTTP (port 3080) instead of HTTPS (port 3443) — NOT RECOMMENDED
  --cacert <FILE>  CA certificate for hub TLS verification (disables -k)
  --raw            Output raw JSON (skip jq formatting)
  -h, --help       Show this help

Commands:
  status                              Hub status and API version
  devices                             List all devices
  device <id>                         All properties of a device
  get <id> <property>                 Get a single property
  snapshot <id> [--width N] [--output file]   Camera snapshot (JPEG, rate limit: 1/10s)
  set <id> <key=value>...             Set device properties (rate limit: 1/s per device)
  stream-start <id> <offer>           Start WebRTC stream (base64 SDP offer)
  stream-extend <id> <stream-id>      Extend stream (call every 60s)
  stream-stop <id> <stream-id>        Stop stream
EOF
  exit "${1:-0}"
}

# --- Input Validation ---
# Only allow alphanumeric, hyphens, underscores, colons, and dots in IDs/properties
validate_id() {
  local val="$1" label="${2:-ID}"
  if [[ ! "$val" =~ ^[a-zA-Z0-9._:-]+$ ]]; then
    echo "Error: Invalid ${label} — only alphanumeric, hyphens, underscores, colons, dots allowed" >&2
    exit 1
  fi
}

# --- Error Handling ---
handle_http_error() {
  local code="$1" body="$2"
  case "$code" in
    400)
      echo "Error 400: Bad request — check parameters and property names" >&2
      echo "$body" | fmt_json >&2
      ;;
    401)
      echo "Error 401: Unauthorized — verify your API key is correct and has sufficient permissions" >&2
      echo "Tip: Check key permissions in the Starling Home Hub app" >&2
      ;;
    404)
      echo "Error 404: Device or property not found — verify the device ID and property name" >&2
      echo "$body" | fmt_json >&2
      ;;
    *)
      echo "Error $code: Unexpected response from hub" >&2
      echo "$body" | fmt_json >&2
      ;;
  esac
  exit 1
}

# Parse global options
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ip)    HUB_IP="$2"; shift 2 ;;
    --key)   API_KEY="$2"; KEY_FROM_CLI=true; shift 2 ;;
    --http)  USE_HTTPS=false; shift ;;
    --https) USE_HTTPS=true; shift ;;
    --cacert) CACERT="$2"; shift 2 ;;
    --raw)   RAW_OUTPUT=true; shift ;;
    -h|--help) usage 0 ;;
    -*) echo "Unknown option: $1" >&2; usage 1 ;;
    *)  break ;;
  esac
done

[[ -z "$HUB_IP" ]] && { echo "Error: Set STARLING_HUB_IP or use --ip" >&2; exit 1; }
[[ -z "$API_KEY" ]] && { echo "Error: Set STARLING_API_KEY env var" >&2; exit 1; }

if $KEY_FROM_CLI; then
  echo "WARNING: API key passed via --key is visible in process list (ps). Use STARLING_API_KEY env var instead." >&2
fi

if $USE_HTTPS; then
  BASE_URL="https://${HUB_IP}:3443/api/connect/v1"
  if [[ -n "$CACERT" ]]; then
    CURL_EXTRA=(--cacert "$CACERT")
  else
    # Starling Home Hub uses a self-signed cert; -k required on trusted local networks
    CURL_EXTRA=(-k)
  fi
else
  echo "WARNING: Using unencrypted HTTP. Local network traffic can be sniffed. Use HTTPS (default) when possible." >&2
  BASE_URL="http://${HUB_IP}:3080/api/connect/v1"
  CURL_EXTRA=()
fi

fmt_json() {
  if $RAW_OUTPUT || ! command -v jq &>/dev/null; then
    cat
  else
    jq . 2>/dev/null || cat
  fi
}

# Core HTTP functions — API key passed via env-constructed URL, never as a separate arg
# All calls have connect-timeout and max-time to prevent hanging
api_get() {
  local path="$1"; shift
  local http_code body
  body=$(curl -sfS -w '\n%{http_code}' "${CURL_TIMEOUT[@]}" ${CURL_EXTRA[@]+"${CURL_EXTRA[@]}"} "$@" "${BASE_URL}${path}?key=${API_KEY}" 2>&1) || true
  http_code=$(echo "$body" | tail -1)
  body=$(echo "$body" | sed '$d')
  if [[ "$http_code" =~ ^2 ]]; then
    echo "$body"
  else
    handle_http_error "$http_code" "$body"
  fi
}

api_get_binary() {
  local path="$1"; shift
  curl -sfS "${CURL_TIMEOUT[@]}" ${CURL_EXTRA[@]+"${CURL_EXTRA[@]}"} "$@" "${BASE_URL}${path}?key=${API_KEY}" || {
    echo "Error: Failed to fetch binary data. Verify device ID and permissions." >&2
    exit 1
  }
}

api_get_param() {
  local path="$1" params="$2"; shift 2
  local http_code body
  body=$(curl -sfS -w '\n%{http_code}' "${CURL_TIMEOUT[@]}" ${CURL_EXTRA[@]+"${CURL_EXTRA[@]}"} "$@" "${BASE_URL}${path}?key=${API_KEY}&${params}" 2>&1) || true
  http_code=$(echo "$body" | tail -1)
  body=$(echo "$body" | sed '$d')
  if [[ "$http_code" =~ ^2 ]]; then
    echo "$body"
  else
    handle_http_error "$http_code" "$body"
  fi
}

api_post() {
  local path="$1" body="$2"
  local http_code resp
  resp=$(curl -sfS -w '\n%{http_code}' "${CURL_TIMEOUT[@]}" ${CURL_EXTRA[@]+"${CURL_EXTRA[@]}"} -X POST \
    -H "Content-Type: application/json" \
    -d "$body" \
    "${BASE_URL}${path}?key=${API_KEY}" 2>&1) || true
  http_code=$(echo "$resp" | tail -1)
  resp=$(echo "$resp" | sed '$d')
  if [[ "$http_code" =~ ^2 ]]; then
    echo "$resp"
  else
    handle_http_error "$http_code" "$resp"
  fi
}

CMD="${1:-}"; shift || true

case "$CMD" in
  status)
    api_get "/status" | fmt_json
    ;;

  devices)
    api_get "/devices" | fmt_json
    ;;

  device)
    [[ -z "${1:-}" ]] && { echo "Usage: starling.sh device <id>" >&2; exit 1; }
    validate_id "$1" "device ID"
    api_get "/devices/$1" | fmt_json
    ;;

  get)
    [[ -z "${1:-}" || -z "${2:-}" ]] && { echo "Usage: starling.sh get <id> <property>" >&2; exit 1; }
    validate_id "$1" "device ID"
    validate_id "$2" "property name"
    api_get "/devices/$1/$2" | fmt_json
    ;;

  snapshot)
    # RATE LIMIT: Once per 10 seconds per camera. Nest cloud enforced.
    [[ -z "${1:-}" ]] && { echo "Usage: starling.sh snapshot <id> [--width N] [--output file]" >&2; exit 1; }
    DEV_ID="$1"; shift
    validate_id "$DEV_ID" "device ID"
    WIDTH=640
    OUTPUT=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --width)  WIDTH="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        *) echo "Unknown snapshot option: $1" >&2; exit 1 ;;
      esac
    done
    # Validate width is numeric
    [[ ! "$WIDTH" =~ ^[0-9]+$ ]] && { echo "Error: --width must be a number (max 1280)" >&2; exit 1; }
    if [[ -n "$OUTPUT" ]]; then
      api_get_binary "/devices/${DEV_ID}/snapshot" -o "$OUTPUT" --max-time 60
      # Restrict file permissions — snapshots are sensitive
      chmod 600 "$OUTPUT" 2>/dev/null || true
      echo "Saved snapshot to $OUTPUT (permissions: owner-only)"
    else
      api_get_binary "/devices/${DEV_ID}/snapshot"
    fi
    ;;

  set)
    # RATE LIMIT: Once per second per device. Nest cloud enforced.
    [[ -z "${1:-}" ]] && { echo "Usage: starling.sh set <id> <key=value>..." >&2; exit 1; }
    DEV_ID="$1"; shift
    validate_id "$DEV_ID" "device ID"
    [[ $# -eq 0 ]] && { echo "Error: No properties specified" >&2; exit 1; }
    # Build JSON from key=value pairs
    JSON="{"
    FIRST=true
    for kv in "$@"; do
      KEY="${kv%%=*}"
      VAL="${kv#*=}"
      validate_id "$KEY" "property name"
      $FIRST || JSON+=","
      FIRST=false
      # Auto-detect type: bool, number, or string
      case "$VAL" in
        true|false)    JSON+="\"$KEY\":$VAL" ;;
        ''|*[!0-9.-]*) JSON+="\"$KEY\":\"$VAL\"" ;;
        *)             JSON+="\"$KEY\":$VAL" ;;
      esac
    done
    JSON+="}"
    api_post "/devices/${DEV_ID}" "$JSON" | fmt_json
    ;;

  stream-start)
    [[ -z "${1:-}" || -z "${2:-}" ]] && { echo "Usage: starling.sh stream-start <id> <base64-sdp-offer>" >&2; exit 1; }
    validate_id "$1" "device ID"
    api_post "/devices/$1/stream" "{\"offer\":\"$2\"}" | fmt_json
    ;;

  stream-extend)
    [[ -z "${1:-}" || -z "${2:-}" ]] && { echo "Usage: starling.sh stream-extend <id> <stream-id>" >&2; exit 1; }
    validate_id "$1" "device ID"
    validate_id "$2" "stream ID"
    api_post "/devices/$1/stream/$2/extend" "{}" | fmt_json
    ;;

  stream-stop)
    [[ -z "${1:-}" || -z "${2:-}" ]] && { echo "Usage: starling.sh stream-stop <id> <stream-id>" >&2; exit 1; }
    validate_id "$1" "device ID"
    validate_id "$2" "stream ID"
    api_post "/devices/$1/stream/$2/stop" "{}" | fmt_json
    ;;

  ""|help)
    usage 0
    ;;

  *)
    echo "Unknown command: $CMD" >&2
    usage 1
    ;;
esac
