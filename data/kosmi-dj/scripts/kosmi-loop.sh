#!/usr/bin/env bash
# =============================================================================
# kosmi-loop.sh — Auto-loop DJ mode for Kosmi
#
# Connects to the room and enters a play→poll→next cycle. Reads video URLs
# from a playlist file (one URL per line) or accepts them via a named pipe
# (FIFO) for dynamic queuing.
#
# Usage:
#   ./kosmi-loop.sh [PLAYLIST_FILE]
#   ./kosmi-loop.sh                      # Uses dynamic FIFO queue
#   ./kosmi-loop.sh /path/to/playlist.txt # Uses static playlist
#
# Control:
#   Stop:   kill $(cat /tmp/kosmi-dj-loop.pid)
#   Status: cat /tmp/kosmi-dj-loop.status
#   Queue:  echo "https://youtube.com/watch?v=xxx" >> /tmp/kosmi-dj-queue.fifo
#
# Environment:
#   KOSMI_DJ_POLL_INTERVAL — Seconds between video-end checks (default: 30)
#   KOSMI_DJ_MAX_IDLE      — Max seconds to idle with no video before sleeping (default: 300)
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

AGENT_BROWSER_SESSION_NAME="${AGENT_BROWSER_SESSION_NAME:-kosmi-dj-session}"
export AGENT_BROWSER_SESSION_NAME

POLL_INTERVAL="${KOSMI_DJ_POLL_INTERVAL:-30}"
MAX_IDLE="${KOSMI_DJ_MAX_IDLE:-300}"

PID_FILE="/tmp/kosmi-dj-loop.pid"
STATUS_FILE="/tmp/kosmi-dj-loop.status"
QUEUE_FIFO="/tmp/kosmi-dj-queue.fifo"
PLAYLIST_FILE="${1:-}"

# ---------------------------------------------------------------------------
# PID management
# ---------------------------------------------------------------------------
# Kill any existing loop
if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" 2>/dev/null)" || true
  if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "[kosmi-dj-loop] Stopping existing loop (PID $OLD_PID)..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
  fi
fi

echo $$ > "$PID_FILE"

cleanup() {
  rm -f "$PID_FILE" "$STATUS_FILE"
  # Don't remove FIFO — other processes may be writing to it
  echo "[kosmi-dj-loop] Stopped."
}
trap cleanup EXIT

write_status() {
  echo "{\"state\":\"$1\",\"video\":\"${2:-}\",\"timestamp\":\"$(date -Iseconds)\",\"pid\":$$}" > "$STATUS_FILE"
}

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

find_ref_any() {
  local json="$1" role="$2"
  shift 2
  for pat in "$@"; do
    local ref
    ref="$(find_ref "$json" "$role" "$pat")"
    if [[ -n "$ref" ]]; then
      echo "$ref"
      return
    fi
  done
  echo ""
}

# Check if a video is currently playing by looking for player/pause/progress elements
is_video_playing() {
  local snap="$1"
  local pause_btn progress_bar

  pause_btn="$(find_ref_any "$snap" "button" "pause")"
  progress_bar="$(find_ref_any "$snap" "progressbar" "progress" "time" "seek")"

  if [[ -n "$pause_btn" ]] || [[ -n "$progress_bar" ]]; then
    return 0  # playing
  fi
  return 1  # not playing
}

# ---------------------------------------------------------------------------
# Build the video queue
# ---------------------------------------------------------------------------
declare -a VIDEO_QUEUE=()
QUEUE_INDEX=0

if [[ -n "$PLAYLIST_FILE" ]] && [[ -f "$PLAYLIST_FILE" ]]; then
  echo "[kosmi-dj-loop] Loading playlist from: $PLAYLIST_FILE"
  while IFS= read -r line; do
    # Skip empty lines and comments
    line="$(echo "$line" | sed 's/#.*//' | xargs)"
    if [[ -n "$line" ]]; then
      VIDEO_QUEUE+=("$line")
    fi
  done < "$PLAYLIST_FILE"
  echo "[kosmi-dj-loop] Loaded ${#VIDEO_QUEUE[@]} videos from playlist."
else
  echo "[kosmi-dj-loop] No playlist file — using FIFO queue at $QUEUE_FIFO"
  echo "[kosmi-dj-loop] To add videos: echo 'https://...' >> $QUEUE_FIFO"

  # Create FIFO if it doesn't exist
  if [[ ! -p "$QUEUE_FIFO" ]]; then
    mkfifo "$QUEUE_FIFO"
  fi
fi

# Get next video URL from queue or FIFO
next_video() {
  # If we have a static playlist, cycle through it
  if [[ ${#VIDEO_QUEUE[@]} -gt 0 ]]; then
    local url="${VIDEO_QUEUE[$QUEUE_INDEX]}"
    QUEUE_INDEX=$(( (QUEUE_INDEX + 1) % ${#VIDEO_QUEUE[@]} ))
    echo "$url"
    return
  fi

  # Otherwise read from FIFO (with timeout)
  local url=""
  if [[ -p "$QUEUE_FIFO" ]]; then
    # Non-blocking read with timeout
    url="$(timeout 5 cat "$QUEUE_FIFO" 2>/dev/null | head -n1)" || true
  fi
  echo "$url"
}

# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------
echo "[kosmi-dj-loop] Starting DJ loop..."
write_status "connecting"

# Step 1: Connect
bash "$SCRIPT_DIR/kosmi-connect.sh"
write_status "connected"

IDLE_SECONDS=0

while true; do
  # Get next video
  NEXT_URL="$(next_video)"

  if [[ -z "$NEXT_URL" ]]; then
    echo "[kosmi-dj-loop] No video in queue. Waiting..."
    write_status "idle"
    sleep "$POLL_INTERVAL"
    IDLE_SECONDS=$((IDLE_SECONDS + POLL_INTERVAL))

    if [[ $IDLE_SECONDS -ge $MAX_IDLE ]]; then
      echo "[kosmi-dj-loop] Max idle time reached ($MAX_IDLE s). Sleeping..."
      write_status "sleeping"
      # Sleep longer when idle to save tokens
      sleep 120
      IDLE_SECONDS=0
    fi
    continue
  fi

  IDLE_SECONDS=0

  # Play the video
  echo "[kosmi-dj-loop] Playing: $NEXT_URL"
  write_status "playing" "$NEXT_URL"

  bash "$SCRIPT_DIR/kosmi-play.sh" "$NEXT_URL" || {
    echo "[kosmi-dj-loop] WARNING: Failed to play $NEXT_URL — skipping."
    write_status "error" "$NEXT_URL"
    sleep 5
    continue
  }

  # Poll until video ends
  echo "[kosmi-dj-loop] Monitoring playback..."
  PLAY_CHECK_COUNT=0

  while true; do
    sleep "$POLL_INTERVAL"
    PLAY_CHECK_COUNT=$((PLAY_CHECK_COUNT + 1))

    SNAP="$(take_snapshot)"

    if is_video_playing "$SNAP"; then
      # Still playing — keep waiting
      if (( PLAY_CHECK_COUNT % 4 == 0 )); then
        echo "[kosmi-dj-loop] Still playing... (check #$PLAY_CHECK_COUNT)"
      fi
    else
      echo "[kosmi-dj-loop] Video appears to have ended."
      write_status "ended" "$NEXT_URL"
      sleep 3
      break
    fi

    # Safety: if we've been polling for over 2 hours, assume something is wrong
    if [[ $PLAY_CHECK_COUNT -ge $(( 7200 / POLL_INTERVAL )) ]]; then
      echo "[kosmi-dj-loop] Max playback poll time reached. Moving to next video."
      break
    fi
  done
done
