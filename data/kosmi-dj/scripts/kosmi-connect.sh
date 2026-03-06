#!/usr/bin/env bash
# =============================================================================
# kosmi-connect.sh — Connect to a Kosmi room via agent-browser
#
# Reads .env from plugin root, opens the room URL, handles nickname/login
# prompts, and verifies the agent is in the room.
#
# Usage:
#   ./kosmi-connect.sh
#
# Environment (loaded from .env):
#   KOSMI_ROOM_URL           — Full room URL (required)
#   KOSMI_EMAIL              — Login email (optional, for auth)
#   KOSMI_PASSWORD           — Login password (optional, for auth)
#   KOSMI_BOT_NAME           — Display name (default: clawdbot)
#   AGENT_BROWSER_SESSION_NAME — Session key (default: kosmi-dj-session)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ---------------------------------------------------------------------------
# Load .env
# ---------------------------------------------------------------------------
ENV_FILE="${PLUGIN_ROOT}/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

KOSMI_ROOM_URL="${KOSMI_ROOM_URL:?KOSMI_ROOM_URL is required — set it in $ENV_FILE}"
KOSMI_BOT_NAME="${KOSMI_BOT_NAME:-clawdbot}"
AGENT_BROWSER_SESSION_NAME="${AGENT_BROWSER_SESSION_NAME:-kosmi-dj-session}"
export AGENT_BROWSER_SESSION_NAME

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
ab() {
  agent-browser "$@"
}

# Take a snapshot and return JSON. Retries once after a short wait.
take_snapshot() {
  local json
  json="$(ab snapshot -i -C --json 2>/dev/null)" || true

  if [[ -z "$json" ]] || ! echo "$json" | jq -e '.success' &>/dev/null; then
    sleep 2
    json="$(ab snapshot -i -C --json 2>/dev/null)" || true
  fi

  echo "$json"
}

# Find a ref ID in snapshot JSON by role and name substring (case-insensitive).
# Usage: find_ref "$snapshot_json" "button" "join"
# Returns: @refXXX or empty string
find_ref() {
  local json="$1" role="$2" name_pattern="$3"
  echo "$json" | jq -r --arg role "$role" --arg pat "$name_pattern" '
    .data.refs // {} | to_entries[]
    | select(
        (.value.role | ascii_downcase) == ($role | ascii_downcase)
        and ((.value.name // "") | ascii_downcase | contains($pat | ascii_downcase))
      )
    | "@\(.key)"
  ' | head -n1
}

# ---------------------------------------------------------------------------
# Main: Connect to Room
# ---------------------------------------------------------------------------
echo "[kosmi-dj] Connecting to room: $KOSMI_ROOM_URL"

# 1. Navigate to room
ab open "$KOSMI_ROOM_URL"
ab wait 2000

# 2. Snapshot the page
SNAP="$(take_snapshot)"

if [[ -z "$SNAP" ]]; then
  echo "[kosmi-dj] ERROR: Could not take snapshot after opening room." >&2
  exit 1
fi

# 3. Handle nickname/name prompt (guest join flow)
NAME_BOX="$(find_ref "$SNAP" "textbox" "name")"
if [[ -n "$NAME_BOX" ]]; then
  echo "[kosmi-dj] Nickname prompt detected — entering name: $KOSMI_BOT_NAME"
  ab fill "$NAME_BOX" "$KOSMI_BOT_NAME"
  ab wait 300

  JOIN_BTN="$(find_ref "$SNAP" "button" "join")"
  if [[ -z "$JOIN_BTN" ]]; then
    JOIN_BTN="$(find_ref "$SNAP" "button" "enter")"
  fi
  if [[ -z "$JOIN_BTN" ]]; then
    JOIN_BTN="$(find_ref "$SNAP" "button" "continue")"
  fi

  if [[ -n "$JOIN_BTN" ]]; then
    echo "[kosmi-dj] Clicking join button: $JOIN_BTN"
    ab click "$JOIN_BTN"
    ab wait 1500
  else
    echo "[kosmi-dj] No join button found — pressing Enter"
    ab press Enter
    ab wait 1500
  fi

  # Re-snapshot after joining
  SNAP="$(take_snapshot)"
fi

# 4. Handle login prompt (if room requires auth and creds are set)
if [[ -n "${KOSMI_EMAIL:-}" ]] && [[ -n "${KOSMI_PASSWORD:-}" ]]; then
  EMAIL_BOX="$(find_ref "$SNAP" "textbox" "email")"
  PASS_BOX="$(find_ref "$SNAP" "textbox" "password")"

  if [[ -n "$EMAIL_BOX" ]] && [[ -n "$PASS_BOX" ]]; then
    echo "[kosmi-dj] Login prompt detected — entering credentials"
    ab fill "$EMAIL_BOX" "$KOSMI_EMAIL"
    ab wait 200
    ab fill "$PASS_BOX" "$KOSMI_PASSWORD"
    ab wait 200

    LOGIN_BTN="$(find_ref "$SNAP" "button" "log in")"
    if [[ -z "$LOGIN_BTN" ]]; then
      LOGIN_BTN="$(find_ref "$SNAP" "button" "login")"
    fi
    if [[ -z "$LOGIN_BTN" ]]; then
      LOGIN_BTN="$(find_ref "$SNAP" "button" "sign in")"
    fi

    if [[ -n "$LOGIN_BTN" ]]; then
      echo "[kosmi-dj] Clicking login button: $LOGIN_BTN"
      ab click "$LOGIN_BTN"
    else
      echo "[kosmi-dj] No login button found — pressing Enter"
      ab press Enter
    fi
    ab wait 2000

    # Re-snapshot after login
    SNAP="$(take_snapshot)"
  fi
fi

# 5. Verify we are in the room
# Look for common room UI elements (chat input, video player, member list, etc.)
CHAT_BOX="$(find_ref "$SNAP" "textbox" "message")"
CHAT_BOX2="$(find_ref "$SNAP" "textbox" "chat")"

if [[ -n "$CHAT_BOX" ]] || [[ -n "$CHAT_BOX2" ]]; then
  echo "[kosmi-dj] Successfully connected to Kosmi room."
else
  echo "[kosmi-dj] WARNING: Could not verify room connection."
  echo "[kosmi-dj] The room may still be loading. Run kosmi-snapshot-debug.sh to inspect."
fi

echo "[kosmi-dj] Connection routine complete."
