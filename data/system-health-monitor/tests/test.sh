#!/bin/bash
# Test suite for System Health Monitor
# Version: 1.1.1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
HEALTH_CHECK="$PARENT_DIR/scripts/health-check.sh"

echo "==================================="
echo "System Health Monitor Test Suite"
echo "==================================="
echo ""

# Check script exists
if [[ ! -f "$HEALTH_CHECK" ]]; then
    echo "❌ FAIL: health-check.sh not found at $HEALTH_CHECK"
    exit 1
fi
echo "✅ Script found: $HEALTH_CHECK"

# Check script is executable
if [[ ! -x "$HEALTH_CHECK" ]]; then
    echo "❌ FAIL: health-check.sh is not executable"
    exit 1
fi
echo "✅ Script is executable"

# Test help command
echo ""
echo "Testing: help command"
if "$HEALTH_CHECK" help > /dev/null 2>&1; then
    echo "✅ Help command works"
else
    echo "❌ FAIL: Help command failed"
    exit 1
fi

# Test hash command
echo ""
echo "Testing: hash command"
if "$HEALTH_CHECK" hash > /dev/null 2>&1; then
    echo "✅ Hash command works"
else
    echo "❌ FAIL: Hash command failed"
    exit 1
fi

# Test status command (may fail if services not running, but should not crash)
echo ""
echo "Testing: status command"
if "$HEALTH_CHECK" status > /dev/null 2>&1; then
    echo "✅ Status command executed"
else
    echo "⚠️  Status command returned non-zero (services may not be running)"
fi

# Test layer commands (1-8)
echo ""
echo "Testing: layer commands (1-8)"
for layer in {1..8}; do
    if "$HEALTH_CHECK" layer "$layer" > /dev/null 2>&1; then
        echo "  ✅ Layer $layer check executed"
    else
        echo "  ⚠️  Layer $layer returned non-zero"
    fi
done

# Check for hardcoded paths
echo ""
echo "Testing: No hardcoded /root paths"
if grep -q "/root/.openclaw" "$HEALTH_CHECK"; then
    echo "❌ FAIL: Found hardcoded /root path in script"
    exit 1
else
    echo "✅ No hardcoded /root paths found"
fi

# Check for sudo usage
echo ""
echo "Testing: No sudo usage"
if grep -q "sudo " "$HEALTH_CHECK"; then
    echo "❌ FAIL: Found sudo usage in script"
    exit 1
else
    echo "✅ No sudo usage found"
fi

# Check metadata files
echo ""
echo "Testing: Metadata files"
if [[ -f "$PARENT_DIR/SKILL.md" ]]; then
    echo "✅ SKILL.md exists"
else
    echo "❌ FAIL: SKILL.md missing"
    exit 1
fi

if [[ -f "$PARENT_DIR/config/health-monitor.json" ]]; then
    echo "✅ config/health-monitor.json exists"
else
    echo "❌ FAIL: config/health-monitor.json missing"
    exit 1
fi

# Validate JSON config
echo ""
echo "Testing: JSON config validation"
if jq empty "$PARENT_DIR/config/health-monitor.json" 2>/dev/null; then
    echo "✅ Config JSON is valid"
else
    echo "❌ FAIL: Config JSON is invalid"
    exit 1
fi

echo ""
echo "==================================="
echo "Test Suite Complete"
echo "==================================="
