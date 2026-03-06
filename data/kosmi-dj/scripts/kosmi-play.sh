#!/usr/bin/env bash
# =============================================================================
# kosmi-play.sh — Play a single video by URL in a Kosmi room
#
# Ensures the agent is connected, opens the URL media modal, fills in the
# video URL, and clicks Play.
#
# Usage:
#   ./kosmi-play.sh <VIDEO_URL>
#
# Example:
#   ./kosmi-play.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# =============================================================================

set -euo pipefail

VIDEO_URL="${1:?Usage: kosmi-play.sh <VIDEO_URL>}"

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

AGENT_BROWSER_SESSION_NAME="${AGENT_BROWSER_SESSION_NAME:-kosmi-dj-session}"
export AGENT_BROWSER_SESSION_NAME

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
ab() {
  agent-browser "$@"
}

take_snapshot() {
  local json
  json="$(ab snapshot -i -C --json 2>/dev/null)" || true
  if [[ -z "$json" ]] || ! echo "$json" | jq -e '.success' &>/dev/null; then
    sleep 2
    json="$(ab snapshot -i -C --json 2>/dev/null)" || true
  fi
  echo "$json"
}

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

# Find ref matching ANY of multiple name patterns
find_ref_any() {
  local json="$1" role="$2"
  shift 2
  local patterns=("$@")
  for pat in "${patterns[@]}"; do
    local ref
    ref="$(find_ref "$json" "$role" "$pat")"
    if [[ -n "$ref" ]]; then
      echo "$ref"
      return
    fi
  done
  echo ""
}

# ---------------------------------------------------------------------------
# Step 1: Ensure connected
# ---------------------------------------------------------------------------
echo "[kosmi-dj] Ensuring room connection..."
bash "$SCRIPT_DIR/kosmi-connect.sh"
ab wait 500

# ---------------------------------------------------------------------------
# Step 2: Check if URL textbox is already visible
# ---------------------------------------------------------------------------
echo "[kosmi-dj] Looking for URL input..."
SNAP="$(take_snapshot)"

URL_BOX="$(find_ref_any "$SNAP" "textbox" "url" "link" "http" "paste")"

# ---------------------------------------------------------------------------
# Step 3: If no URL box, open the Apps/media modal
# ---------------------------------------------------------------------------
if [[ -z "$URL_BOX" ]]; then
  echo "[kosmi-dj] URL input not visible — opening media modal..."

  # Try various button names Kosmi uses for the Apps/Add/+ modal
  APPS_BTN="$(find_ref_any "$SNAP" "button" "apps" "add" "media" "+")"

  if [[ -n "$APPS_BTN" ]]; then
    echo "[kosmi-dj] Clicking apps button: $APPS_BTN"
    ab click "$APPS_BTN"
    ab wait 800
  else
    echo "[kosmi-dj] WARNING: Could not find apps/add button. Trying screen center area..."
    # Kosmi sometimes has a large central "+" area for empty rooms
    LINK_BTN="$(find_ref_any "$SNAP" "link" "app" "add" "media")"
    if [[ -n "$LINK_BTN" ]]; then
      ab click "$LINK_BTN"
      ab wait 800
    fi
  fi

  # After modal opens, look for the URL/Link option (chain-link icon)
  SNAP2="$(take_snapshot)"
  URL_MODE_BTN="$(find_ref_any "$SNAP2" "button" "url" "link" "web" "custom")"

  if [[ -n "$URL_MODE_BTN" ]]; then
    echo "[kosmi-dj] Clicking URL mode button: $URL_MODE_BTN"
    ab click "$URL_MODE_BTN"
    ab wait 600
  fi

  # Re-snapshot to find the URL textbox
  SNAP="$(take_snapshot)"
  URL_BOX="$(find_ref_any "$SNAP" "textbox" "url" "link" "http" "paste")"
fi

# ---------------------------------------------------------------------------
# Step 4: Fill URL and play
# ---------------------------------------------------------------------------
if [[ -z "$URL_BOX" ]]; then
  echo "[kosmi-dj] ERROR: Could not find URL textbox. Run kosmi-snapshot-debug.sh to inspect UI." >&2
  echo "[kosmi-dj] Dumping current snapshot refs for debugging:" >&2
  echo "$SNAP" | jq '.data.refs // {}' >&2
  exit 1
fi

echo "[kosmi-dj] Filling URL: $VIDEO_URL"
ab fill "$URL_BOX" "$VIDEO_URL"
ab wait 300

# Look for Play/Start/Submit button
PLAY_BTN="$(find_ref_any "$SNAP" "button" "play" "start" "submit" "go" "open")"

if [[ -n "$PLAY_BTN" ]]; then
  echo "[kosmi-dj] Clicking play button: $PLAY_BTN"
  ab click "$PLAY_BTN"
else
  echo "[kosmi-dj] No play button found — pressing Enter to submit"
  ab press Enter
fi

ab wait 1500

echo "[kosmi-dj] Video queued: $VIDEO_URL"

# ---------------------------------------------------------------------------
# Step 5: Verify playback
# ---------------------------------------------------------------------------
SNAP_VERIFY="$(take_snapshot)"

# Look for video player elements or progress indicators
PLAYER_REF="$(find_ref_any "$SNAP_VERIFY" "video" "player" "media")"
PROGRESS_REF="$(find_ref_any "$SNAP_VERIFY" "progressbar" "progress" "time" "seek")"
PAUSE_BTN="$(find_ref_any "$SNAP_VERIFY" "button" "pause" "stop")"

if [[ -n "$PLAYER_REF" ]] || [[ -n "$PROGRESS_REF" ]] || [[ -n "$PAUSE_BTN" ]]; then
  echo "[kosmi-dj] Playback confirmed."
else
  echo "[kosmi-dj] WARNING: Could not confirm playback. Video may still be loading."
fi

echo "[kosmi-dj] Done."
