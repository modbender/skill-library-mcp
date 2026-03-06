#!/bin/bash
# ============================================================
# GuavaGuard Soul Watchdog — Self-Healing Identity Protection
# ============================================================
# Monitors SOUL.md and IDENTITY.md for ANY modification.
# If tampered, instantly restores from git and re-locks.
# Runs as LaunchAgent (survives reboot).
#
# Usage:
#   ./soul-watchdog.sh              # foreground
#   ./soul-watchdog.sh --install    # install as LaunchAgent
#   ./soul-watchdog.sh --uninstall  # remove LaunchAgent
#   ./soul-watchdog.sh --status     # check if running
# ============================================================

WORKSPACE="${HOME}/.openclaw/workspace"
IDENTITY_FILES=("SOUL.md" "IDENTITY.md")
LOG_FILE="${HOME}/.openclaw/guava-guard/soul-watchdog.log"
HASH_FILE="${HOME}/.openclaw/guava-guard/soul-hashes-watchdog.json"
PLIST_NAME="com.guava-guard.soul-watchdog"
PLIST_PATH="${HOME}/Library/LaunchAgents/${PLIST_NAME}.plist"

mkdir -p "$(dirname "$LOG_FILE")"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Compute SHA-256 hash of a file
compute_hash() {
  shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1
}

# Store trusted hashes (current state = trusted baseline)
store_hashes() {
  local json="{"
  local first=true
  for f in "${IDENTITY_FILES[@]}"; do
    local fp="${WORKSPACE}/${f}"
    if [ -f "$fp" ]; then
      local h=$(compute_hash "$fp")
      if [ "$first" = true ]; then first=false; else json+=","; fi
      json+="\"${f}\":\"${h}\""
    fi
  done
  json+="}"
  echo "$json" > "$HASH_FILE"
  log "INIT: Stored trusted hashes → ${HASH_FILE}"
}

# Restore identity file from git and re-lock
restore_and_lock() {
  local file="$1"
  local fp="${WORKSPACE}/${file}"
  
  log "🚨 TAMPER DETECTED: ${file} — restoring from git..."
  
  # Unlock (if locked)
  chflags nouchg "$fp" 2>/dev/null
  
  # Restore from git
  cd "$WORKSPACE"
  if git checkout -- "$file" 2>/dev/null; then
    log "✅ RESTORED: ${file} from git"
  else
    # If git fails, restore from hash-verified backup
    log "⚠️ Git restore failed for ${file}, file may be untracked"
  fi
  
  # Re-lock
  chflags uchg "$fp" 2>/dev/null
  log "🔒 RE-LOCKED: ${file} (chflags uchg)"
  
  # Update stored hash
  store_hashes
}

# Check integrity against stored hashes
check_integrity() {
  if [ ! -f "$HASH_FILE" ]; then
    store_hashes
    return
  fi
  
  for f in "${IDENTITY_FILES[@]}"; do
    local fp="${WORKSPACE}/${f}"
    if [ -f "$fp" ]; then
      local current=$(compute_hash "$fp")
      local stored=$(python3 -c "import json; d=json.load(open('${HASH_FILE}')); print(d.get('${f}',''))" 2>/dev/null)
      
      if [ -n "$stored" ] && [ "$current" != "$stored" ]; then
        restore_and_lock "$f"
      fi
    fi
  done
}

# --- Install/Uninstall LaunchAgent ---

install_agent() {
  local script_path="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  
  cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${PLIST_NAME}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${script_path}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${LOG_FILE}</string>
  <key>StandardErrorPath</key>
  <string>${LOG_FILE}</string>
</dict>
</plist>
EOF
  
  launchctl load "$PLIST_PATH" 2>/dev/null
  log "✅ INSTALLED: LaunchAgent ${PLIST_NAME}"
  echo "✅ Installed and started: ${PLIST_NAME}"
  echo "   Log: ${LOG_FILE}"
}

uninstall_agent() {
  launchctl unload "$PLIST_PATH" 2>/dev/null
  rm -f "$PLIST_PATH"
  log "🗑️ UNINSTALLED: LaunchAgent ${PLIST_NAME}"
  echo "🗑️ Uninstalled: ${PLIST_NAME}"
}

status_agent() {
  if launchctl list | grep -q "$PLIST_NAME"; then
    echo "✅ Running: ${PLIST_NAME}"
    echo "   PID: $(launchctl list | grep "$PLIST_NAME" | awk '{print $1}')"
    echo "   Log: ${LOG_FILE}"
    tail -5 "$LOG_FILE" 2>/dev/null
  else
    echo "❌ Not running: ${PLIST_NAME}"
  fi
}

# --- Handle CLI args ---
case "${1:-}" in
  --install)   install_agent; exit 0 ;;
  --uninstall) uninstall_agent; exit 0 ;;
  --status)    status_agent; exit 0 ;;
esac

# --- Main Loop (fswatch-based) ---

# Check if fswatch is available
if ! command -v fswatch &>/dev/null; then
  log "ERROR: fswatch not found. Install with: brew install fswatch"
  # Fallback to polling mode
  log "FALLBACK: Using polling mode (5s interval)"
  store_hashes
  while true; do
    check_integrity
    sleep 5
  done
  exit 0
fi

# Initialize
log "🍈🛡️ GuavaGuard Soul Watchdog starting..."
log "   Workspace: ${WORKSPACE}"
log "   Watching: ${IDENTITY_FILES[*]}"
store_hashes

# Build watch paths
WATCH_PATHS=()
for f in "${IDENTITY_FILES[@]}"; do
  WATCH_PATHS+=("${WORKSPACE}/${f}")
done

# Watch for changes with fswatch (macOS FSEvents backend)
fswatch -o "${WATCH_PATHS[@]}" | while read -r count; do
  log "⚡ File change detected (${count} events)"
  check_integrity
done
