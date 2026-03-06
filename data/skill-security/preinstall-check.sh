#!/bin/bash
# Pre-installation security check
# Call this before loading/installing any new skill
# Usage: ./preinstall-check.sh /path/to/skill

set -e

SKILL_PATH="$1"
SCRIPT_DIR=$(dirname "$0")
BLOCKLIST="$SCRIPT_DIR/blocklist.txt"
ALLOWLIST="$SCRIPT_DIR/allowlist.txt"

if [ -z "$SKILL_PATH" ]; then
    echo "Usage: $0 /path/to/skill"
    exit 1
fi

SKILL_NAME=$(basename "$SKILL_PATH")

# Check blocklist first
if [ -f "$BLOCKLIST" ] && grep -q "^$SKILL_NAME:" "$BLOCKLIST"; then
    echo "⛔ BLOCKED: $SKILL_NAME is on the security blocklist"
    grep "^$SKILL_NAME:" "$BLOCKLIST"
    echo ""
    echo "Remove from blocklist to override: $BLOCKLIST"
    exit 2
fi

# Check allowlist (skip audit if verified)
if [ -f "$ALLOWLIST" ] && grep -q "^$SKILL_NAME:verified:" "$ALLOWLIST"; then
    echo "✅ ALLOWED: $SKILL_NAME is on the verified allowlist"
    grep "^$SKILL_NAME:" "$ALLOWLIST"
    exit 0
fi

# Run audit
echo "🔍 Running security audit on $SKILL_NAME..."
echo ""

"$SCRIPT_DIR/audit.sh" "$SKILL_PATH"
result=$?

if [ $result -eq 2 ]; then
    echo ""
    echo "⛔ INSTALLATION BLOCKED"
    echo "Skill has been added to blocklist: $BLOCKLIST"
    exit 2
elif [ $result -eq 1 ]; then
    echo ""
    echo "⚠️  Manual approval required"
    echo "To allow: echo '$SKILL_NAME:verified:$(date -I):manual-review' >> $ALLOWLIST"
    exit 1
else
    echo ""
    echo "✅ Security check passed"
    exit 0
fi
