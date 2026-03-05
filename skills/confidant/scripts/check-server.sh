#!/usr/bin/env bash
# check-server.sh — Quick Confidant server & tunnel diagnostics
# No side effects — just reports current state.
#
# Usage: ./check-server.sh [--port 3000] [--json]

set -euo pipefail

PORT="${CONFIDANT_PORT:-3000}"
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --json) JSON_OUTPUT=true; shift ;;
    *)      shift ;;
  esac
done

# --- Dependency check ---

if ! command -v jq &>/dev/null; then
  if $JSON_OUTPUT; then
    echo '{"error":"jq is required but not installed","code":"MISSING_DEPENDENCY","hint":"Ubuntu/Debian: apt-get install -y jq | macOS: brew install jq"}' >&2
  else
    echo "Error: jq is required but not installed." >&2
    echo "  Ubuntu/Debian: apt-get install -y jq" >&2
    echo "  macOS: brew install jq" >&2
  fi
  exit 2
fi

# Check server health
SERVER_STATUS="stopped"
SERVER_PID=""
if curl -sf "http://localhost:${PORT}/health" > /dev/null 2>&1; then
  SERVER_STATUS="running"
  SERVER_PID=$(lsof -ti ":${PORT}" 2>/dev/null | head -1 \
    || fuser "${PORT}/tcp" 2>/dev/null | awk '{print $1}' \
    || echo "unknown")
fi

# Check tunnels
TUNNEL_STATUS="none"
TUNNEL_URL=""
TUNNEL_PROVIDER=""

# Try ngrok
NGROK_URL=$(curl -s "localhost:4040/api/tunnels" 2>/dev/null \
  | jq -r '.tunnels[] | select(.config.addr | test("'"$PORT"'")) | .public_url' 2>/dev/null \
  | head -1 || echo "")
if [[ -n "$NGROK_URL" ]]; then
  TUNNEL_STATUS="active"
  TUNNEL_URL="$NGROK_URL"
  TUNNEL_PROVIDER="ngrok"
fi

# Try localtunnel (if ngrok not found)
if [[ -z "$TUNNEL_URL" ]]; then
  LT_PID=$(pgrep -f "localtunnel.*--port.*${PORT}" 2>/dev/null | head -1 || echo "")
  if [[ -n "$LT_PID" && -f "/tmp/confidant-lt-url-${PORT}" ]]; then
    LT_URL=$(cat "/tmp/confidant-lt-url-${PORT}" 2>/dev/null || echo "")
    if [[ -n "$LT_URL" ]]; then
      TUNNEL_STATUS="active"
      TUNNEL_URL="$LT_URL"
      TUNNEL_PROVIDER="localtunnel"
    fi
  fi
fi

if $JSON_OUTPUT; then
  jq -n \
    --arg serverStatus "$SERVER_STATUS" \
    --arg serverPid "$SERVER_PID" \
    --arg port "$PORT" \
    --arg tunnelStatus "$TUNNEL_STATUS" \
    --arg tunnelUrl "$TUNNEL_URL" \
    --arg tunnelProvider "$TUNNEL_PROVIDER" \
    '{
      server: {
        status: $serverStatus,
        pid: (if $serverPid == "" then null else $serverPid end),
        port: ($port | tonumber)
      },
      tunnel: {
        status: $tunnelStatus,
        url: (if $tunnelUrl == "" then null else $tunnelUrl end),
        provider: (if $tunnelProvider == "" then null else $tunnelProvider end)
      }
    }'
else
  echo "=== Confidant Server ==="
  echo "Status: $SERVER_STATUS"
  echo "Port:   $PORT"
  if [[ -n "$SERVER_PID" ]]; then
    echo "PID:    $SERVER_PID"
  fi
  echo ""
  echo "=== Tunnel ==="
  echo "Status:   $TUNNEL_STATUS"
  if [[ -n "$TUNNEL_URL" ]]; then
    echo "Provider: $TUNNEL_PROVIDER"
    echo "URL:      $TUNNEL_URL"
  fi
fi
