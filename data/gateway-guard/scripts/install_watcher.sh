#!/usr/bin/env bash
# Install the single combined gateway-guard watcher as a LaunchAgent.
# One daemon does both:
#   1) Gateway back (what-just-happened): when gateway goes down→up, trigger summary to TUI/Telegram.
#   2) Continue-on-error: when gateway.log shows "Unhandled stop reason: error", send "continue" to the agent.
# Unloads the old separate LaunchAgents (what-just-happened, continue-on-error) so you only have one.

set -e
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARD_SCRIPT="$SCRIPT_DIR/gateway_guard.py"
PLIST_SRC="$SCRIPT_DIR/com.openclaw.gateway-guard.watcher.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.openclaw.gateway-guard.watcher.plist"

if [[ ! -f "$GUARD_SCRIPT" ]]; then
  echo "Error: gateway_guard.py not found at $GUARD_SCRIPT"
  exit 1
fi
if [[ ! -f "$PLIST_SRC" ]]; then
  echo "Error: plist not found at $PLIST_SRC"
  exit 1
fi

# Unload old daemons so user has only one
launchctl unload "$HOME/Library/LaunchAgents/com.openclaw.what-just-happened.plist" 2>/dev/null || true
launchctl unload "$HOME/Library/LaunchAgents/com.openclaw.gateway-guard.continue-on-error.plist" 2>/dev/null || true

OPENCLAW_BIN="${OPENCLAW_BIN:-$(which openclaw 2>/dev/null || echo '/opt/homebrew/bin/openclaw')}"
PATH_FOR_PLIST="${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}:/usr/local/bin:/opt/homebrew/bin"
mkdir -p "$OPENCLAW_HOME/logs"
sed -e "s|OPENCLAW_HOME|$OPENCLAW_HOME|g" \
    -e "s|OPENCLAW_GUARD_SCRIPT|$GUARD_SCRIPT|g" \
    -e "s|OPENCLAW_BIN|$OPENCLAW_BIN|g" \
    -e "s|PATH_PLACEHOLDER|$PATH_FOR_PLIST|g" \
    "$PLIST_SRC" > "$PLIST_DEST"
echo "Installed $PLIST_DEST (openclaw: $OPENCLAW_BIN)"
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"
echo "Loaded. Single watcher runs every 30s: (1) gateway back → what-just-happened summary, (2) run error in gateway.log → send 'continue' to agent."
echo "To stop: launchctl unload $PLIST_DEST"
echo "Logs: $OPENCLAW_HOME/logs/gateway-guard-watcher.out.log and .err.log"
echo "Verify: launchctl list com.openclaw.gateway-guard.watcher"
