#!/bin/bash
# OpenClaw skill-auto-attach
# Monitors workspace for file changes and attaches files to Telegram

# Configuration
WATCH_DIR="/home/elodyzen/.openclaw/workspace"
TMP_DIR="/tmp/openclaw-skills"
LOG_FILE="/home/elodyzen/.openclaw/skills/skill-auto-attach/auto-attach.log"

# Create directories if missing
mkdir -p "$TMP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Log function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Auto-attach script started. Watching $WATCH_DIR"

# Clean up temp files on exit
trap 'log "Script exiting - cleaning temp files"; rm -f "$TMP_DIR"/*; log "Watcher stopped"' EXIT INT TERM

# Watch for file changes
inotifywait -m -e create,modify -r --format '%w%f %e' "$WATCH_DIR" | while read -r file_path event; do
  # Skip if not a regular file
  if [[ ! -f "$file_path" ]]; then
    continue
  fi

  filename=$(basename "$file_path")
  log "Detected change ($event): $filename"

  temp_file="$TMP_DIR/$filename"

  # Copy file
  if cp -f "$file_path" "$temp_file"; then
    log "Copied $filename to $temp_file"

    # Send to Telegram using --target and --media
    if openclaw message send --target=telegram --message="[FILE] $filename" --media="$temp_file"; then
      log "SUCCESS: Attached $filename"
    else
      log "ERROR: Failed to send $filename"
    fi

    # Clean up
    rm -f "$temp_file"
    log "Cleaned up temp file for $filename"
  else
    log "ERROR: Failed to copy $filename"
  fi
done

log "Watcher loop ended unexpectedly"