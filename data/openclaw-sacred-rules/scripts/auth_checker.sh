#!/bin/bash
# Safe Auth Profile Checker
# Checks auth status without directly reading auth-profiles.json

set -e

echo "🔐 OpenClaw Auth Status Check"
echo "==============================="

# Check if .env file exists (required for auth commands)
if [[ ! -f "$HOME/.openclaw/.env" ]]; then
    echo "❌ Missing .env file at ~/.openclaw/.env"
    echo "   This file should contain gateway passwords and API keys"
    exit 1
fi

echo "✅ Environment file exists"

# Check if auth-profiles.json exists (don't read it)
AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
if [[ ! -f "$AUTH_FILE" ]]; then
    echo "❌ Missing auth-profiles.json"
    echo "   Expected location: $AUTH_FILE"
    exit 1
fi

echo "✅ Auth profiles file exists"

# Check file permissions
AUTH_PERMS=$(stat -f "%A" "$AUTH_FILE" 2>/dev/null || stat -c "%a" "$AUTH_FILE" 2>/dev/null)
if [[ "$AUTH_PERMS" != "600" ]]; then
    echo "⚠️  Auth file permissions: $AUTH_PERMS (should be 600)"
else
    echo "✅ Auth file permissions correct (600)"
fi

# Check file modification time (recent changes might indicate issues)
if command -v stat > /dev/null; then
    # macOS stat
    LAST_MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$AUTH_FILE" 2>/dev/null || \
                   stat -c "%y" "$AUTH_FILE" 2>/dev/null | cut -d'.' -f1)
    echo "📅 Last modified: $LAST_MODIFIED"
fi

# Use OpenClaw CLI to check auth status (safe method)
echo ""
echo "🔍 Running OpenClaw status check..."

# Source environment and run status
if source "$HOME/.openclaw/.env" && openclaw status > /tmp/openclaw_status.txt 2>&1; then
    echo "✅ OpenClaw status command succeeded"
    
    # Check for auth-related errors in output (without showing sensitive info)
    if grep -iq "auth" /tmp/openclaw_status.txt; then
        echo "ℹ️  Auth information found in status"
    fi
    
    if grep -iq "error\|fail\|unavailable" /tmp/openclaw_status.txt; then
        echo "⚠️  Potential issues detected in status"
        echo "   Run 'openclaw status' manually to see details"
    fi
    
else
    echo "❌ OpenClaw status command failed"
    echo "   This suggests auth or gateway issues"
    echo "   Check gateway is running: openclaw gateway status"
fi

# Clean up temp file
rm -f /tmp/openclaw_status.txt

echo ""
echo "💡 If experiencing auth issues:"
echo "   1. Check gateway is running: openclaw gateway status"
echo "   2. Verify .env file has correct keys"
echo "   3. Try: source ~/.openclaw/.env && openclaw auth <provider>"
echo "   4. If all else fails: check MEMORY.md for Rule #7"

echo ""
echo "🚫 NEVER directly read auth-profiles.json"
echo "   Use CLI tools only!"