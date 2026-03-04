#!/bin/bash
# Test script for System Health Monitor skill

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEALTH_SCRIPT="$SCRIPT_DIR/health-check.sh"

echo "=== Testing System Health Monitor Skill ==="
echo "Test started: $(date)"
echo ""

# Test 1: Basic status check
echo "Test 1: Basic status check"
echo "--------------------------"
"$HEALTH_SCRIPT" status
echo ""

# Test 2: Detailed report
echo "Test 2: Detailed report (first section)"
echo "----------------------------------------"
"$HEALTH_SCRIPT" report | head -30
echo ""

# Test 3: Check specific layers
echo "Test 3: Check monitoring layer 2 (Config Monitor)"
echo "--------------------------------------------------"
"$HEALTH_SCRIPT" layer 2
echo ""

echo "Test 4: Check monitoring layer 3 (Heartbeat Monitor)"
echo "-----------------------------------------------------"
"$HEALTH_SCRIPT" layer 3
echo ""

# Test 4: Security check
echo "Test 5: Security status"
echo "-----------------------"
"$HEALTH_SCRIPT" security | head -30
echo ""

# Test 5: Logs check
echo "Test 6: View monitoring logs"
echo "----------------------------"
"$HEALTH_SCRIPT" logs --monitor | head -10
echo ""

# Test 6: Health score calculation
echo "Test 7: Health score verification"
echo "----------------------------------"
echo "Calculating health score..."
for layer in {1..10}; do
    if "$HEALTH_SCRIPT" layer "$layer" >/dev/null 2>&1; then
        echo "Layer $layer: ✅"
    else
        echo "Layer $layer: ❌"
    fi
done
echo ""

# Verify script permissions
echo "Test 8: Script permissions and dependencies"
echo "-------------------------------------------"
echo "Health script executable: $(test -x "$HEALTH_SCRIPT" && echo "✅" || echo "❌")"
echo "jq installed: $(command -v jq >/dev/null 2>&1 && echo "✅" || echo "❌")"
echo "systemctl available: $(command -v systemctl >/dev/null 2>&1 && echo "✅" || echo "❌")"
echo "OpenClaw available: $(command -v openclaw >/dev/null 2>&1 && echo "✅" || echo "❌")"
echo ""

# Test 9: Configuration file
echo "Test 9: Configuration validation"
echo "--------------------------------"
CONFIG_FILE="$SCRIPT_DIR/../config/health-monitor.json"
if [[ -f "$CONFIG_FILE" ]]; then
    echo "Config file exists: ✅"
    if jq empty "$CONFIG_FILE" 2>/dev/null; then
        echo "Config file valid JSON: ✅"
        echo "Alert threshold: $(jq -r '.alert_threshold' "$CONFIG_FILE")"
        echo "Monitored services: $(jq -r '.monitored_services | length' "$CONFIG_FILE")"
    else
        echo "Config file valid JSON: ❌"
    fi
else
    echo "Config file exists: ❌ (using defaults)"
fi
echo ""

# Test 10: Skill documentation
echo "Test 10: Skill documentation"
echo "----------------------------"
SKILL_MD="$SCRIPT_DIR/../SKILL.md"
if [[ -f "$SKILL_MD" ]]; then
    echo "SKILL.md exists: ✅"
    echo "Skill name: $(grep -m1 "^# " "$SKILL_MD" | sed 's/^# //')"
    echo "Description: $(grep -A1 "## Description" "$SKILL_MD" | tail -1)"
    echo "Lines in SKILL.md: $(wc -l < "$SKILL_MD")"
else
    echo "SKILL.md exists: ❌"
fi
echo ""

echo "=== Test Summary ==="
echo "Tests completed: $(date)"
echo "Skill location: $SCRIPT_DIR/.."
echo ""

echo "✅ Skill development complete!"
echo "Next steps:"
echo "1. Test skill integration with OpenClaw"
echo "2. Consider publishing to ClawHub"
echo "3. Add more advanced features (alerting, historical analysis)"