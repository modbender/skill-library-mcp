#!/usr/bin/env bash
# Desktop Guardian v2 — Installation Script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$HOME/.openclaw/skills/desktop-guardian"
LOG_DIR="$HOME/Library/Logs/desktop-guardian"
LAUNCH_AGENT_LABEL="com.openclaw.desktop-guardian"
LAUNCH_AGENT_PLIST="$HOME/Library/LaunchAgents/${LAUNCH_AGENT_LABEL}.plist"
OLD_AGENT_LABEL="com.roy.desktop-monitor"
OLD_AGENT_PLIST="$HOME/Library/LaunchAgents/${OLD_AGENT_LABEL}.plist"
HS_SPOON_DIR="$HOME/.hammerspoon/Spoons"

info()  { echo "✅ $*"; }
warn()  { echo "⚠️  $*"; }
err()   { echo "❌ $*"; exit 1; }
step()  { echo ""; echo "▶ $*"; }

# --- Pre-checks ---
step "Checking prerequisites"
[[ "$(uname -s)" == "Darwin" ]] || err "macOS required"
command -v python3 &>/dev/null || err "python3 not found"
command -v brew &>/dev/null || err "Homebrew not found"
info "macOS + python3 + Homebrew OK"

# --- PyYAML ---
step "Checking PyYAML"
if python3 -c "import yaml" 2>/dev/null; then
    info "PyYAML already installed"
else
    echo "Installing PyYAML..."
    pip3 install --user pyyaml
    info "PyYAML installed"
fi

# --- Hammerspoon ---
step "Checking Hammerspoon"
if brew list --cask hammerspoon &>/dev/null 2>&1; then
    info "Hammerspoon already installed"
else
    echo "Installing Hammerspoon..."
    brew install --cask hammerspoon
    info "Hammerspoon installed"
fi

# Start Hammerspoon if not running
if ! pgrep -x "Hammerspoon" &>/dev/null; then
    echo "Starting Hammerspoon..."
    open -a Hammerspoon
    sleep 3
fi

# Ensure ~/.hammerspoon exists
mkdir -p "$HOME/.hammerspoon"

# --- IPC CLI ---
step "Checking hs CLI (IPC)"
# Ensure hs.ipc is loaded
INIT_LUA="$HOME/.hammerspoon/init.lua"
touch "$INIT_LUA"

if ! grep -q 'require.*hs.ipc' "$INIT_LUA" 2>/dev/null; then
    echo 'require("hs.ipc")' >> "$INIT_LUA"
    info "Added hs.ipc to init.lua"
fi

# Install the CLI tool
if command -v hs &>/dev/null; then
    info "hs CLI already available"
else
    # Try installing via Hammerspoon
    echo "Installing hs CLI..."
    # Reload to pick up hs.ipc
    if command -v hs &>/dev/null; then
        hs -c "hs.ipc.cliInstall()" 2>/dev/null || true
    else
        warn "hs CLI not found. After granting Accessibility, run: hs -c 'hs.ipc.cliInstall()'"
    fi
fi

# --- Install Spoon ---
step "Installing DesktopGuardian Spoon"
mkdir -p "$HS_SPOON_DIR"
cp -r "$PROJECT_DIR/Spoons/DesktopGuardian.spoon" "$HS_SPOON_DIR/"
info "Spoon copied to $HS_SPOON_DIR/DesktopGuardian.spoon"

# Add Spoon load to init.lua
if ! grep -q 'DesktopGuardian' "$INIT_LUA" 2>/dev/null; then
    cat >> "$INIT_LUA" << 'EOF'

-- BEGIN desktop-guardian (managed by OpenClaw)
hs.loadSpoon("DesktopGuardian")
-- END desktop-guardian
EOF
    info "Added DesktopGuardian Spoon load to init.lua"
else
    info "DesktopGuardian already in init.lua"
fi

# Reload Hammerspoon
if command -v hs &>/dev/null; then
    hs -c "hs.reload()" 2>/dev/null || true
    sleep 2
    info "Hammerspoon config reloaded"
fi

# --- Accessibility check ---
step "Checking Accessibility permission"
if command -v hs &>/dev/null; then
    ACC=$(hs -c "hs.accessibilityState()" 2>/dev/null || echo "false")
    if [[ "$ACC" == "true" ]]; then
        info "Accessibility permission granted"
    else
        warn "Hammerspoon needs Accessibility permission"
        echo "Opening System Settings → Privacy & Security → Accessibility..."
        open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" 2>/dev/null || \
            open "/System/Library/PreferencePanes/Security.prefPane" 2>/dev/null || true
        echo ""
        echo "Please add Hammerspoon.app to the Accessibility list, then press Enter..."
        
        # Poll for up to 60s
        TIMEOUT=60
        ELAPSED=0
        while [[ $ELAPSED -lt $TIMEOUT ]]; do
            ACC=$(hs -c "hs.accessibilityState()" 2>/dev/null || echo "false")
            if [[ "$ACC" == "true" ]]; then
                info "Accessibility permission granted!"
                break
            fi
            sleep 5
            ELAPSED=$((ELAPSED + 5))
        done
        
        if [[ "$ACC" != "true" ]]; then
            warn "Accessibility not granted. Running in degraded (monitor-only) mode."
        fi
    fi
else
    warn "hs CLI not available yet. Accessibility check skipped."
fi

# --- Compile Swift fallback ---
step "Compiling Swift fallback"
if swiftc -O "$SCRIPT_DIR/desktop-query.swift" -o "$SCRIPT_DIR/desktop-query" 2>/dev/null; then
    info "Swift fallback compiled"
else
    warn "Swift compilation failed. Degraded mode fallback won't be available."
fi

# --- Config directory ---
step "Setting up config directory"
mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"
if [[ ! -f "$CONFIG_DIR/policy.yaml" ]]; then
    cp "$PROJECT_DIR/assets/config.example.yaml" "$CONFIG_DIR/policy.yaml"
    chmod 600 "$CONFIG_DIR/policy.yaml"
    info "Default policy.yaml created"
else
    info "policy.yaml already exists (preserved)"
fi

# --- Log directory ---
mkdir -p "$LOG_DIR"
chmod 700 "$LOG_DIR"
info "Log directory: $LOG_DIR"

# --- Migrate old com.roy.desktop-monitor ---
step "Checking for legacy desktop-monitor"
if [[ -f "$OLD_AGENT_PLIST" ]]; then
    echo "Found legacy $OLD_AGENT_LABEL"
    echo "Unloading old LaunchAgent..."
    launchctl bootout "gui/$(id -u)" "$OLD_AGENT_PLIST" 2>/dev/null || \
        launchctl unload "$OLD_AGENT_PLIST" 2>/dev/null || true
    mv "$OLD_AGENT_PLIST" "$OLD_AGENT_PLIST.migrated"
    info "Old desktop-monitor disabled and marked as migrated"
fi

# --- Install LaunchAgent ---
step "Installing LaunchAgent"
cat > "$LAUNCH_AGENT_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LAUNCH_AGENT_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${SCRIPT_DIR}/monitor.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>60</integer>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/monitor.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/monitor.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF
chmod 644 "$LAUNCH_AGENT_PLIST"

# Bootstrap
launchctl bootout "gui/$(id -u)/$LAUNCH_AGENT_LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$LAUNCH_AGENT_PLIST"
info "LaunchAgent installed and started"

# --- Make monitor.sh executable ---
chmod +x "$SCRIPT_DIR/monitor.sh"

# --- Done ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Desktop Guardian v2 installed!"
echo ""
echo "Config:     $CONFIG_DIR/policy.yaml"
echo "Logs:       $LOG_DIR/"
echo "Kill switch: touch $CONFIG_DIR/KILL_SWITCH"
echo ""
echo "━━━ Chrome Tab Monitoring (Optional) ━━━"
echo "To enable Chrome tab counting/closing via CDP:"
echo "  1. Quit Chrome"
echo "  2. Edit Chrome launch to include: --remote-debugging-port=9222"
echo "     macOS: Add to /Applications/Google Chrome.app wrapper or alias:"
echo "     open -a 'Google Chrome' --args --remote-debugging-port=9222"
echo "  3. Or create a LaunchAgent to set the flag permanently"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
