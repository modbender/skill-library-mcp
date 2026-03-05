#!/usr/bin/env bash
# IP Camera RTSP CLI
# Usage: camera.sh [--cam <name>] <command> [args...]
#
# Commands:
#   info                        - Test connectivity and show camera info
#   snapshot [output.jpg]       - Capture a single frame from RTSP stream
#   record [seconds] [out.mp4]  - Record video clip
#   stream-url [main|sub]       - Print RTSP stream URL
#   list-cameras                - List all configured cameras
#
# Works with any ONVIF/RTSP IP camera. Tested with TP-Link Tapo/Vigi.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

CONFIG_FILE="${IPCAM_CONFIG:-$HOME/.config/ipcam/config.json}"

# ── Parse --cam option ───────────────────────────────────────────────────────
CAM_NAME=""
if [[ "${1:-}" == "--cam" ]]; then
  CAM_NAME="${2:-}"
  if [[ -z "$CAM_NAME" ]]; then
    echo "Error: --cam requires a camera name" >&2
    exit 1
  fi
  shift 2
fi

# ── Load config ──────────────────────────────────────────────────────────────
if [[ -f "$CONFIG_FILE" ]]; then
  HAS_CAMERAS=$(jq -r 'has("cameras")' "$CONFIG_FILE")

  if [[ "$HAS_CAMERAS" == "true" ]]; then
    if [[ -z "$CAM_NAME" ]]; then
      CAM_NAME=$(jq -r '.default // empty' "$CONFIG_FILE")
      if [[ -z "$CAM_NAME" ]]; then
        CAM_NAME=$(jq -r '.cameras | keys[0] // empty' "$CONFIG_FILE")
      fi
    fi

    CAM_EXISTS=$(jq -r --arg name "$CAM_NAME" '.cameras | has($name)' "$CONFIG_FILE")
    if [[ "$CAM_EXISTS" != "true" ]]; then
      echo "Error: Camera '$CAM_NAME' not found in config" >&2
      echo "Available: $(jq -r '.cameras | keys | join(", ")' "$CONFIG_FILE")" >&2
      exit 1
    fi

    CAM_IP="${CAM_IP:-$(jq -r --arg name "$CAM_NAME" '.cameras[$name].ip // empty' "$CONFIG_FILE")}"
    CAM_USER="${CAM_USER:-$(jq -r --arg name "$CAM_NAME" '.cameras[$name].username // empty' "$CONFIG_FILE")}"
    CAM_PASS="${CAM_PASS:-$(jq -r --arg name "$CAM_NAME" '.cameras[$name].password // empty' "$CONFIG_FILE")}"
    CAM_RTSP_PORT="${CAM_RTSP_PORT:-$(jq -r --arg name "$CAM_NAME" '.cameras[$name].rtsp_port // 554' "$CONFIG_FILE")}"
    RTSP_MAIN_PATH="${RTSP_MAIN_PATH:-$(jq -r --arg name "$CAM_NAME" '.cameras[$name].rtsp_main_path // "stream1"' "$CONFIG_FILE")}"
    RTSP_SUB_PATH="${RTSP_SUB_PATH:-$(jq -r --arg name "$CAM_NAME" '.cameras[$name].rtsp_sub_path // "stream2"' "$CONFIG_FILE")}"
  else
    CAM_NAME="default"
    CAM_IP="${CAM_IP:-$(jq -r '.ip // empty' "$CONFIG_FILE")}"
    CAM_USER="${CAM_USER:-$(jq -r '.username // empty' "$CONFIG_FILE")}"
    CAM_PASS="${CAM_PASS:-$(jq -r '.password // empty' "$CONFIG_FILE")}"
    CAM_RTSP_PORT="${CAM_RTSP_PORT:-$(jq -r '.rtsp_port // 554' "$CONFIG_FILE")}"
    RTSP_MAIN_PATH="${RTSP_MAIN_PATH:-$(jq -r '.rtsp_main_path // "stream1"' "$CONFIG_FILE")}"
    RTSP_SUB_PATH="${RTSP_SUB_PATH:-$(jq -r '.rtsp_sub_path // "stream2"' "$CONFIG_FILE")}"
  fi
fi

: "${CAM_IP:?Set CAM_IP or configure $CONFIG_FILE}"
: "${CAM_USER:?Set CAM_USER or configure $CONFIG_FILE}"
: "${CAM_PASS:?Set CAM_PASS or configure $CONFIG_FILE}"
: "${CAM_RTSP_PORT:=554}"
: "${RTSP_MAIN_PATH:=stream1}"
: "${RTSP_SUB_PATH:=stream2}"

# Output directory
OUTPUT_DIR="${CAM_OUTPUT_DIR:-${SKILL_DIR}/.tmp/snapshots}"
mkdir -p "$OUTPUT_DIR"

# ── Helpers ──────────────────────────────────────────────────────────────────
timestamp() { date '+%Y-%m-%d-%H%M%S'; }

rtsp_url() {
  local stream="${1:-main}"
  local stream_path="$RTSP_MAIN_PATH"
  [[ "$stream" == "sub" ]] && stream_path="$RTSP_SUB_PATH"

  # Safe URL-encode password via stdin (handles quotes, =, &, etc.)
  local encoded_pass
  encoded_pass=$(python3 -c "import sys,urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip(),safe=''))" <<< "$CAM_PASS")

  echo "rtsp://${CAM_USER}:${encoded_pass}@${CAM_IP}:${CAM_RTSP_PORT}/${stream_path}"
}

check_ffmpeg() {
  if ! command -v ffmpeg &>/dev/null; then
    echo "Error: ffmpeg not found. Run install.sh first." >&2
    exit 1
  fi
}

# RTSP socket I/O timeout in microseconds (ffmpeg -timeout)
RTSP_TIMEOUT_US=$(( ${RTSP_TIMEOUT:-10} * 1000000 ))

# ── Commands ─────────────────────────────────────────────────────────────────
cmd="${1:-help}"
shift || true

case "$cmd" in

  list-cameras|list)
    if [[ ! -f "$CONFIG_FILE" ]]; then
      echo "No config file found: $CONFIG_FILE" >&2; exit 1
    fi
    if jq -e 'has("cameras")' "$CONFIG_FILE" >/dev/null 2>&1; then
      DEFAULT_CAM=$(jq -r '.default // "none"' "$CONFIG_FILE")
      echo "Configured cameras (default: $DEFAULT_CAM):"
      jq -r '.cameras | to_entries[] | "  \(.key): \(.value.ip):\(.value.rtsp_port // 554)"' "$CONFIG_FILE"
    else
      echo "Single camera (legacy config):"
      echo "  default: $(jq -r '.ip' "$CONFIG_FILE"):$(jq -r '.rtsp_port // 554' "$CONFIG_FILE")"
    fi
    ;;

  info)
    check_ffmpeg
    echo "Camera [$CAM_NAME]: ${CAM_IP}:${CAM_RTSP_PORT}"
    echo "User:   ${CAM_USER}"
    echo "Stream: main=${RTSP_MAIN_PATH} sub=${RTSP_SUB_PATH}"
    echo ""
    echo "Testing RTSP connection..."
    url="$(rtsp_url main)"
    output=$(ffmpeg -rtsp_transport tcp -timeout "$RTSP_TIMEOUT_US" \
      -i "$url" -t 1 -f null - 2>&1) || true
    if echo "$output" | grep -q "Stream #0"; then
      echo "✓ RTSP reachable"
      echo "$output" | grep "Stream #0" | sed 's/^/  /'
    else
      echo "✗ Cannot reach RTSP main stream"
      echo "  URL: rtsp://${CAM_USER}:***@${CAM_IP}:${CAM_RTSP_PORT}/${RTSP_MAIN_PATH}"
      echo "  Tip: Try 'ptz.py stream-uri' to auto-detect paths."
      echo "  Tip: Camera may limit concurrent RTSP connections."
    fi
    ;;

  snapshot|snap)
    check_ffmpeg
    output="${1:-$OUTPUT_DIR/${CAM_NAME}-$(timestamp).jpg}"
    url="$(rtsp_url main)"
    echo "[$CAM_NAME] Capturing snapshot -> $output"
    if ffmpeg -y -rtsp_transport tcp -timeout "$RTSP_TIMEOUT_US" \
      -i "$url" -frames:v 1 -q:v 2 \
      "$output" 2>/dev/null && [[ -f "$output" ]]; then
      echo "✓ Saved: $output ($(du -h "$output" | cut -f1))"
    else
      echo "✗ Failed to capture snapshot" >&2
      echo "  Tip: Check RTSP connectivity with 'camera.sh info'" >&2
      exit 1
    fi
    ;;

  record|rec)
    check_ffmpeg
    duration="${1:-10}"
    shift || true
    output="${1:-$OUTPUT_DIR/${CAM_NAME}-rec-$(timestamp).mp4}"
    url="$(rtsp_url main)"
    echo "[$CAM_NAME] Recording ${duration}s -> $output"
    if ffmpeg -y -rtsp_transport tcp -timeout "$RTSP_TIMEOUT_US" \
      -i "$url" -t "$duration" -c copy \
      "$output" 2>/dev/null && [[ -f "$output" ]]; then
      echo "✓ Saved: $output ($(du -h "$output" | cut -f1))"
    else
      echo "✗ Failed to record" >&2
      echo "  Tip: Check RTSP connectivity with 'camera.sh info'" >&2
      exit 1
    fi
    ;;

  stream-url|url)
    rtsp_url "${1:-main}"
    ;;

  help|--help|-h)
    cat <<'HELP'
IP Camera RTSP CLI

Usage: camera.sh [--cam <name>] <command> [args...]

Commands:
  info                         Test RTSP connectivity
  snapshot [output.jpg]        Capture a single frame
  record [seconds] [out.mp4]   Record video clip (default: 10s)
  stream-url [main|sub]        Print RTSP stream URL
  list-cameras                 List configured cameras

Options:
  --cam <name>    Select camera (default: from config)

Config: ~/.config/ipcam/config.json
Env:    CAM_IP, CAM_USER, CAM_PASS, CAM_RTSP_PORT, RTSP_TIMEOUT (seconds)

Examples:
  camera.sh snapshot
  camera.sh --cam cam2 snapshot /tmp/cam.jpg
  camera.sh record 30
  camera.sh stream-url sub
HELP
    ;;

  *)
    echo "Unknown command: $cmd (try 'camera.sh help')" >&2
    exit 1
    ;;
esac
