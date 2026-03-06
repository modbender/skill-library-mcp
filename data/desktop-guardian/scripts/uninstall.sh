#!/usr/bin/env bash
# Desktop Guardian v2 — Uninstall Script
set -euo pipefail

LAUNCH_AGENT_LABEL="com.openclaw.desktop-guardian"
LAUNCH_AGENT_PLIST="$HOME/Library/LaunchAgents/${LAUNCH_AGENT_LABEL}.plist"
CONFIG_DIR="$HOME/.openclaw/skills/desktop-guardian"
LOG_DIR="$HOME/Library/Logs/desktop-guardian"
HS_SPOON="$HOME/.hammerspoon/Spoons/DesktopGuardian.spoon"
INIT_LUA="$HOME/.hammerspoon/init.lua"

info() { echo "✅ $*"; }
warn() { echo "⚠️  $*"; }

echo "Desktop Guardian v2 — Uninstall"
echo ""

# 1. Remove LaunchAgent
if [[ -f "$LAUNCH_AGENT_PLIST" ]]; then
    launchctl bootout "gui/$(id -u)/$LAUNCH_AGENT_LABEL" 2>/dev/null || \
        launchctl bootout "gui/$(id -u)" "$LAUNCH_AGENT_PLIST" 2>/dev/null || true
    rm -f "$LAUNCH_AGENT_PLIST"
    info "LaunchAgent removed"
else
    info "LaunchAgent not found (already removed)"
fi

# 2. Remove Spoon
if [[ -d "$HS_SPOON" ]]; then
    rm -rf "$HS_SPOON"
    info "Spoon removed from ~/.hammerspoon/Spoons/"
fi

# 3. Remove Spoon load from init.lua
if [[ -f "$INIT_LUA" ]]; then
    if grep -q 'desktop-guardian' "$INIT_LUA"; then
        # Remove the marked block
        sed -i '' '/-- BEGIN desktop-guardian/,/-- END desktop-guardian/d' "$INIT_LUA"
        # Also remove standalone loadSpoon line if present
        sed -i '' '/hs\.loadSpoon.*DesktopGuardian/d' "$INIT_LUA"
        info "Removed DesktopGuardian from init.lua"
    fi
fi

# 4. Reload Hammerspoon
if command -v hs &>/dev/null && pgrep -x "Hammerspoon" &>/dev/null; then
    hs -c "hs.reload()" 2>/dev/null || true
    info "Hammerspoon config reloaded"
fi

# 5. Config preservation
echo ""
read -rp "Remove config directory ($CONFIG_DIR)? [y/N] " REMOVE_CONFIG
if [[ "${REMOVE_CONFIG,,}" == "y" ]]; then
    rm -rf "$CONFIG_DIR"
    info "Config removed"
else
    info "Config preserved at $CONFIG_DIR"
fi

# 6. Log preservation
read -rp "Remove log directory ($LOG_DIR)? [y/N] " REMOVE_LOGS
if [[ "${REMOVE_LOGS,,}" == "y" ]]; then
    rm -rf "$LOG_DIR"
    info "Logs removed"
else
    info "Logs preserved at $LOG_DIR"
fi

echo ""
echo "✅ Desktop Guardian v2 uninstalled"
echo "Note: Hammerspoon itself was NOT removed (you may use it for other things)"
