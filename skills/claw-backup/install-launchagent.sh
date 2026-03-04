#!/usr/bin/env bash
# Universal installer: probe for com.openclaw.backup.plist and existing
# LaunchDaemon/LaunchAgent, then install or update the user LaunchAgent.
# Usage: ./install-launchagent.sh [path-to-plist]
#        ./install-launchagent.sh   (auto-detect plist and state)

set -e

LABEL="com.openclaw.backup"
PLIST_NAME="${LABEL}.plist"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
LAUNCH_DAEMONS="/Library/LaunchDaemons"
AGENT_PLIST="$LAUNCH_AGENTS/$PLIST_NAME"
DAEMON_PLIST="$LAUNCH_DAEMONS/$PLIST_NAME"

# ---- Platform ----
if [ "$(uname -s)" != "Darwin" ]; then
  echo "This script is for macOS (launchd). On Linux use cron; on Windows use Task Scheduler."
  exit 1
fi

# ---- Probe: find plist ----
search_plist_paths=(
  "$HOME/clawd/scripts/$PLIST_NAME"
  "$HOME/Dev/clawd/scripts/$PLIST_NAME"
  "$HOME/Projects/clawd/scripts/$PLIST_NAME"
  "$HOME/Dev/ClawBackup/scripts/$PLIST_NAME"
  "$(pwd)/scripts/$PLIST_NAME"
  "$(pwd)/$PLIST_NAME"
)

# Optional: search under home (max depth 5) for the plist name
find_plist_under_home() {
  local found
  found=$(find "$HOME" -maxdepth 5 -type f -name "$PLIST_NAME" 2>/dev/null | head -1)
  [ -n "$found" ] && echo "$found"
}

FOUND_PLIST=""
if [ -n "$1" ]; then
  if [ -f "$1" ]; then
    FOUND_PLIST="$1"
  else
    echo "Not a file: $1"
    exit 1
  fi
else
  for p in "${search_plist_paths[@]}"; do
    if [ -f "$p" ]; then
      FOUND_PLIST="$p"
      break
    fi
  done
  if [ -z "$FOUND_PLIST" ]; then
    FOUND_PLIST=$(find_plist_under_home)
  fi
fi

# ---- Report ----
echo "=== OpenClaw backup launchd installer ==="
echo ""
echo "Plist source:"
if [ -n "$FOUND_PLIST" ]; then
  echo "  Found: $FOUND_PLIST"
else
  echo "  None found."
  echo ""
  echo "Run 'node setup.js' first (from ClawBackup or your project) to generate the plist."
  echo "Or pass the plist path: $0 /path/to/$PLIST_NAME"
  exit 1
fi

echo ""
echo "Current state:"
echo "  LaunchDaemon (system, root): $([ -f "$DAEMON_PLIST" ] && echo "installed" || echo "not installed")"
echo "  LaunchAgent (user):          $([ -f "$AGENT_PLIST" ] && echo "installed" || echo "not installed")"
echo "  Loaded in launchctl:          $(launchctl list 2>/dev/null | grep -q "$LABEL" && echo "yes" || echo "no")"
echo ""

# ---- Unload old LaunchDaemon if present ----
if [ -f "$DAEMON_PLIST" ]; then
  echo "Removing old LaunchDaemon (runs as root; backup would not see your rclone config)..."
  if sudo launchctl unload "$DAEMON_PLIST" 2>/dev/null; then
    echo "  Unloaded."
  fi
  sudo rm -f "$DAEMON_PLIST"
  echo "  Removed $DAEMON_PLIST"
  echo ""
fi

# ---- Install LaunchAgent ----
mkdir -p "$LAUNCH_AGENTS"
cp "$FOUND_PLIST" "$AGENT_PLIST"
echo "Installed: $AGENT_PLIST"

# Load (idempotent: unload first if already loaded to pick up plist changes)
if launchctl list 2>/dev/null | grep -q "$LABEL"; then
  launchctl unload "$AGENT_PLIST" 2>/dev/null || true
fi
if ! launchctl load "$AGENT_PLIST"; then
  echo "Load failed. Check that the plist path inside the file points to a valid backup script."
  exit 1
fi
echo "Loaded."
echo ""
echo "Done. Backup will run daily at the time defined in the LaunchAgent plist under your user."
echo "Verify: launchctl list | grep $LABEL"
echo "Test:   run the backup script once manually to confirm rclone and paths work."
