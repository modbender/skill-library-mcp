#!/bin/bash
set -euo pipefail

# OpenClaw Gateway FD Exhaustion One-Click Fix
# Version 1.0.0

echo "🦞 OpenClaw Gateway FD Exhaustion Fix"
echo "====================================="

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ This fix is for macOS only"
    exit 1
fi

WORKSPACE="$HOME/.openclaw/workspace"
PLIST="$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
BACKUP_PLIST="$PLIST.bak.$(date +%Y%m%d%H%M%S)"

# Step 1: Check workspace file count
echo -e "\n📊 Step 1: Checking workspace file count..."
FILE_COUNT=$(find "$WORKSPACE" -type f | wc -l | xargs)
echo "   Total files in workspace: $FILE_COUNT"

if [[ "$FILE_COUNT" -lt 1000 ]]; then
    echo "✅ Workspace file count is normal (<1000). FD exhaustion unlikely to be the issue."
else
    echo "⚠️  Workspace has >1000 files — likely cause of FD exhaustion"
fi

# Step 2: Find and clean unnecessary directories
echo -e "\n🧹 Step 2: Cleaning unnecessary dependency directories in workspace..."
echo "   Looking for .venv and node_modules directories..."

VENVS=$(find "$WORKSPACE" -name ".venv" -type d 2>/dev/null || true)
NODE_MODULES=$(find "$WORKSPACE" -name "node_modules" -type d 2>/dev/null || true)

if [[ -z "$VENVS" && -z "$NODE_MODULES" ]]; then
    echo "✅ No dependency directories found in workspace"
else
    echo "   Found directories to clean:"
    [[ -n "$VENVS" ]] && echo "$VENVS" | awk '{print "   - " $0}'
    [[ -n "$NODE_MODULES" ]] && echo "$NODE_MODULES" | awk '{print "   - " $0}'
    
    read -p "   Delete these directories? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        [[ -n "$VENVS" ]] && rm -rf $VENVS
        [[ -n "$NODE_MODULES" ]] && rm -rf $NODE_MODULES
        echo "✅ Cleaned up dependency directories"
        NEW_FILE_COUNT=$(find "$WORKSPACE" -type f | wc -l | xargs)
        echo "   New workspace file count: $NEW_FILE_COUNT"
    else
        echo "⚠️  Skipped cleaning — you will need to move these directories outside workspace manually"
    fi
fi

# Step 3: Update LaunchAgent FD limits
echo -e "\n⚙️  Step 3: Updating LaunchAgent file descriptor limits..."
if [[ ! -f "$PLIST" ]]; then
    echo "❌ LaunchAgent plist not found at $PLIST"
    echo "   Run 'openclaw gateway install' first to generate it"
    exit 1
fi

# Check if limits already exist
if grep -q "NumberOfFiles" "$PLIST"; then
    echo "✅ File descriptor limits already set in plist"
else
    echo "   Backing up existing plist to $BACKUP_PLIST"
    cp "$PLIST" "$BACKUP_PLIST"
    
    echo "   Adding FD limits to plist..."
    # Insert limits before closing </dict>
    sed -i '' '/<\/dict>/i\
    <key>HardResourceLimits</key>\
    <dict>\
      <key>NumberOfFiles</key>\
      <integer>524288</integer>\
    </dict>\
    <key>SoftResourceLimits</key>\
    <dict>\
      <key>NumberOfFiles</key>\
      <integer>524288</integer>\
    </dict>\
' "$PLIST"
    
    echo "✅ Updated plist with 524,288 file descriptor limit"
fi

# Step 4: Restart Gateway
echo -e "\n🔄 Step 4: Restarting Gateway service..."
echo "   Unloading existing LaunchAgent..."
launchctl bootout gui/$(id -u) "$PLIST" 2>/dev/null || true

echo "   Loading updated LaunchAgent..."
launchctl bootstrap gui/$(id -u) "$PLIST"

echo "   Waiting for Gateway to start (10s)..."
sleep 10

# Step 5: Verify status
echo -e "\n✅ Step 5: Verifying Gateway health..."
openclaw gateway status

echo -e "\n🎉 Fix complete!"
echo "====================================="
echo "📝 Permanent rule: NEVER put .venv/node_modules/large datasets inside ~/.openclaw/workspace/"
echo "🚀 You can now use OpenClaw normally"
