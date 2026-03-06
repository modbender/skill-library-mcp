#!/bin/bash
# OpenClaw Cooldown Reset Script
# Usage: ./reset_cooldowns.sh
# 
# IMPORTANT: This resets ALL auth profile cooldowns and error states
# Use when experiencing "all providers unavailable" despite valid credentials

set -e

AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"

echo "🔧 OpenClaw Cooldown Reset"
echo "=========================="

# Check if file exists
if [[ ! -f "$AUTH_FILE" ]]; then
    echo "❌ Auth file not found: $AUTH_FILE"
    exit 1
fi

echo "✅ Auth file found: $AUTH_FILE"

# Backup before modifying
BACKUP_DIR="$HOME/openclaw-backups/cooldown-reset-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp "$AUTH_FILE" "$BACKUP_DIR/"
echo "📦 Backed up auth file to: $BACKUP_DIR"

# Reset cooldowns using Python
python3 << 'EOF'
import json

auth_file = '/Users/admin/.openclaw/agents/main/agent/auth-profiles.json'

with open(auth_file, 'r') as f:
    data = json.load(f)

reset_count = 0

# Clear all cooldowns and error states
for key in data.get('usageStats', {}):
    profile = data['usageStats'][key]
    
    if 'cooldownUntil' in profile:
        del profile['cooldownUntil']
        reset_count += 1
        print(f"  ✓ Cleared cooldown from {key}")
    
    if 'errorCount' in profile:
        profile['errorCount'] = 0
    
    if 'lastFailureAt' in profile:
        del profile['lastFailureAt']
    
    if 'failureCounts' in profile:
        profile['failureCounts'] = {}

with open(auth_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Reset {reset_count} cooldowns")
print("💡 Restart gateway if issues persist: openclaw gateway restart")
EOF

echo ""
echo "🎉 Cooldown reset complete!"
echo ""
echo "⚠️  NOTE: This is a workaround for a bug where in-memory"
echo "   cooldown state doesn't refresh when file timestamps expire."
echo "   The root cause needs to be fixed in OpenClaw core."