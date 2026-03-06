#!/usr/bin/env bash
# request-secret.sh — One-command secret request for AI agents
# Handles server lifecycle, request creation, and tunnel detection automatically.
#
# Usage:
#   ./request-secret.sh --label "API Key" --service openai
#   ./request-secret.sh --label "Token" --save ~/.config/myapp/token.txt
#   ./request-secret.sh --label "Password" --tunnel  (starts localtunnel for remote access)
#
# Options:
#   --label <text>      Description shown on the web form (required)
#   --service <name>    Auto-save to ~/.config/<name>/api_key
#   --save <path>       Auto-save to explicit path
#   --env <varname>     Also set env var (requires --service or --save)
#   --port <number>     Server port (default: 3000)
#   --timeout <secs>    Max wait for server/tunnel startup (default: 30)
#   --tunnel            Start a localtunnel if no tunnel is detected (for remote users)
#   --json              Output JSON instead of human-readable text

set -euo pipefail

# Emit an error message respecting --json mode
emit_error() {
  local msg="$1" code="${2:-UNKNOWN}" hint="${3:-}"
  if $JSON_OUTPUT; then
    jq -n --arg m "$msg" --arg c "$code" --arg h "$hint" \
      '{"error":$m, "code":$c, "hint":(if $h == "" then null else $h end)}' >&2
  else
    echo "Error: $msg" >&2
    [[ -n "$hint" ]] && echo "  $hint" >&2
  fi
}

# Smart CLI resolution: global binary > npx fallback (auto-accept install)
confidant_cmd() {
  if command -v confidant &>/dev/null; then
    confidant "$@"
  else
    npx --yes @aiconnect/confidant "$@"
  fi
}

LABEL=""
SERVICE=""
SAVE_PATH=""
ENV_VAR=""
PORT="${CONFIDANT_PORT:-3000}"
TIMEOUT=30
JSON_OUTPUT=false
START_TUNNEL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --label)    LABEL="$2"; shift 2 ;;
    --service)  SERVICE="$2"; shift 2 ;;
    --save)     SAVE_PATH="$2"; shift 2 ;;
    --env)      ENV_VAR="$2"; shift 2 ;;
    --port)     PORT="$2"; shift 2 ;;
    --timeout)  TIMEOUT="$2"; shift 2 ;;
    --tunnel)   START_TUNNEL=true; shift ;;
    --json)     JSON_OUTPUT=true; shift ;;
    *)          echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$LABEL" ]]; then
  emit_error "--label is required" "MISSING_LABEL" \
    "Usage: request-secret.sh --label \"API Key\" [--service name] [--save path]"
  exit 1
fi

# --- Dependency check ---

if ! command -v curl &>/dev/null; then
  emit_error "curl is required but not installed" "MISSING_DEPENDENCY" \
    "Ubuntu/Debian: apt-get install -y curl | macOS: brew install curl"
  exit 2
fi

if ! command -v jq &>/dev/null; then
  emit_error "jq is required but not installed" "MISSING_DEPENDENCY" \
    "Ubuntu/Debian: apt-get install -y jq | macOS: brew install jq"
  exit 2
fi

# --- Cleanup trap ---

SERVER_PID=""
LT_PID=""
SERVER_LOG="/tmp/confidant-server-${PORT}.log"
STARTED_SERVER=false

cleanup() {
  [[ -n "${LT_PID:-}" ]] && kill "$LT_PID" 2>/dev/null || true
  [[ "$STARTED_SERVER" == true && -n "${SERVER_PID:-}" ]] && kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# --- Step 1: Ensure server is running ---

server_running() {
  curl -sf "http://localhost:${PORT}/health" > /dev/null 2>&1
}

if server_running; then
  : # Server already running
else
  # Start server — log output to a temp file so we can diagnose failures
  confidant_cmd serve --port "$PORT" > "$SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  STARTED_SERVER=true

  elapsed=0
  while ! server_running; do
    # Check if server process died
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      server_err=$(tail -5 "$SERVER_LOG" 2>/dev/null | tr '\n' ' ' || echo "unknown error")
      emit_error "Server process died during startup" "SERVER_CRASH" "$server_err"
      exit 3
    fi
    sleep 1
    elapsed=$((elapsed + 1))
    if [[ $elapsed -ge $TIMEOUT ]]; then
      server_err=$(tail -5 "$SERVER_LOG" 2>/dev/null | tr '\n' ' ' || echo "check port ${PORT}")
      emit_error "Server failed to start within ${TIMEOUT}s" "SERVER_TIMEOUT" \
        "Try increasing --timeout or check if port ${PORT} is in use. Last log: ${server_err}"
      exit 3
    fi
  done
fi

# --- Step 2: Create the request via API (curl) ---
# Using the REST API directly avoids the CLI `request` command which enters
# an infinite polling loop and would hang the $() capture forever.

REQUEST_BODY=$(jq -n --arg lbl "$LABEL" '{"expiresIn": 86400, "label": $lbl}')

REQUEST_OUTPUT=$(curl -sf -X POST "http://localhost:${PORT}/requests" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY" 2>&1) || {
  emit_error "Failed to create request via API" "REQUEST_FAILED" \
    "Server may not be ready. curl output: ${REQUEST_OUTPUT:-empty}"
  exit 4
}

LOCAL_URL=$(echo "$REQUEST_OUTPUT" | jq -r '.url // empty' 2>/dev/null || echo "")
REQUEST_ID=$(echo "$REQUEST_OUTPUT" | jq -r '.id // empty' 2>/dev/null || echo "")
REQUEST_HASH=$(echo "$REQUEST_OUTPUT" | jq -r '.hash // empty' 2>/dev/null || echo "")

# Fallback: build URL from hash if .url was not returned
if [[ -z "$LOCAL_URL" && -n "$REQUEST_HASH" ]]; then
  LOCAL_URL="http://localhost:${PORT}/requests/${REQUEST_HASH}"
fi

if [[ -z "$LOCAL_URL" ]]; then
  emit_error "Failed to create request — no URL in API response" "REQUEST_FAILED" \
    "API response: $(echo "$REQUEST_OUTPUT" | tr '\n' ' ')"
  exit 4
fi

# --- Step 3: Detect or start tunnel ---

PUBLIC_URL=""
TUNNEL_PROVIDER=""
STARTED_TUNNEL=false

detect_tunnel() {
  # Try ngrok first
  local ngrok_url
  ngrok_url=$(curl -s "localhost:4040/api/tunnels" 2>/dev/null \
    | jq -r '.tunnels[] | select(.config.addr | test("'"$PORT"'")) | .public_url' 2>/dev/null \
    | head -1 || echo "")
  if [[ -n "$ngrok_url" ]]; then
    PUBLIC_URL="${LOCAL_URL/http:\/\/localhost:${PORT}/${ngrok_url}}"
    TUNNEL_PROVIDER="ngrok"
    return 0
  fi

  # Try localtunnel (check if running by looking for the process)
  local lt_pid
  lt_pid=$(pgrep -f "localtunnel.*--port.*${PORT}" 2>/dev/null | head -1 || echo "")
  if [[ -n "$lt_pid" ]]; then
    # localtunnel doesn't have an API — check if we saved the URL
    if [[ -f "/tmp/confidant-lt-url-${PORT}" ]]; then
      local lt_url
      lt_url=$(cat "/tmp/confidant-lt-url-${PORT}")
      if [[ -n "$lt_url" ]]; then
        PUBLIC_URL="${LOCAL_URL/http:\/\/localhost:${PORT}/${lt_url}}"
        TUNNEL_PROVIDER="localtunnel"
        return 0
      fi
    fi
  fi

  return 1
}

if detect_tunnel; then
  : # Tunnel already available
elif $START_TUNNEL; then
  # Start localtunnel in background
  LT_LOG="/tmp/confidant-lt-log-${PORT}"
  # Use global lt if available, otherwise npx
  if command -v lt &>/dev/null; then
    lt --port "$PORT" > "$LT_LOG" 2>&1 &
  else
    npx --yes localtunnel --port "$PORT" > "$LT_LOG" 2>&1 &
  fi
  LT_PID=$!
  STARTED_TUNNEL=true

  # Wait for localtunnel to output the URL
  elapsed=0
  while [[ $elapsed -lt $TIMEOUT ]]; do
    sleep 1
    elapsed=$((elapsed + 1))
    lt_url=$(grep -oE 'https://[^[:space:]]+' "$LT_LOG" 2>/dev/null | head -1 || echo "")
    if [[ -n "$lt_url" ]]; then
      echo "$lt_url" > "/tmp/confidant-lt-url-${PORT}"
      PUBLIC_URL="${LOCAL_URL/http:\/\/localhost:${PORT}/${lt_url}}"
      TUNNEL_PROVIDER="localtunnel"
      break
    fi
  done

  if [[ -z "$PUBLIC_URL" ]]; then
    if $JSON_OUTPUT; then
      echo "{\"error\":\"localtunnel failed to capture a URL\",\"code\":\"TUNNEL_FAILED\",\"hint\":\"Check localtunnel logs at ${LT_LOG}\"}" >&2
    else
      echo "Warning: localtunnel failed to start. Using local URL only." >&2
    fi
  fi
fi

# --- Step 4: Output ---

SHARE_URL="${PUBLIC_URL:-$LOCAL_URL}"

if [[ -n "$SERVICE" ]]; then
  SAVE_INFO="~/.config/${SERVICE}/api_key"
elif [[ -n "$SAVE_PATH" ]]; then
  SAVE_INFO="$SAVE_PATH"
else
  SAVE_INFO=""
fi

if $JSON_OUTPUT; then
  jq -n \
    --arg url "$SHARE_URL" \
    --arg localUrl "$LOCAL_URL" \
    --arg publicUrl "$PUBLIC_URL" \
    --arg tunnelProvider "$TUNNEL_PROVIDER" \
    --arg requestId "$REQUEST_ID" \
    --arg requestHash "$REQUEST_HASH" \
    --arg saveTo "$SAVE_INFO" \
    --argjson startedServer "$STARTED_SERVER" \
    --argjson startedTunnel "$STARTED_TUNNEL" \
    '{
      url: $url,
      localUrl: $localUrl,
      publicUrl: (if $publicUrl == "" then null else $publicUrl end),
      tunnelProvider: (if $tunnelProvider == "" then null else $tunnelProvider end),
      requestId: $requestId,
      requestHash: $requestHash,
      saveTo: (if $saveTo == "" then null else $saveTo end),
      startedServer: $startedServer,
      startedTunnel: $startedTunnel
    }'
else
  echo "🔐 Secure link created!"
  echo ""
  echo "URL: $SHARE_URL"
  if [[ -n "$PUBLIC_URL" && -n "$TUNNEL_PROVIDER" ]]; then
    echo "  (tunnel: $TUNNEL_PROVIDER | local: $LOCAL_URL)"
  elif [[ -z "$PUBLIC_URL" ]]; then
    echo "  ⚠️  Local URL only — user must have network access to this machine"
    echo "  Tip: use --tunnel to start a localtunnel for remote access"
  fi
  if [[ -n "$SAVE_INFO" ]]; then
    echo "Save to: $SAVE_INFO"
  fi
  echo ""
  echo "Share the URL above with the user. Secret expires after submission or 24h."
fi

# --- Step 5: Delegate polling + save to the CLI ---
# The Confidant CLI already handles polling, saving to disk, env vars, and cleanup.
# No need to reimplement that logic in bash.

POLL_ARGS=(--poll "$REQUEST_ID" --api-url "http://localhost:${PORT}")

if [[ -n "$SERVICE" ]]; then
  POLL_ARGS+=(--service "$SERVICE")
fi

if [[ -n "$SAVE_PATH" ]]; then
  POLL_ARGS+=(--save "$SAVE_PATH")
fi

if [[ -n "$ENV_VAR" ]]; then
  POLL_ARGS+=(--env "$ENV_VAR")
fi

$JSON_OUTPUT && POLL_ARGS+=(--json)

# confidant request --poll <id> will block until secret is submitted,
# then save to ~/.config/<service>/api_key and exit.
confidant_cmd request "${POLL_ARGS[@]}"
