#!/bin/bash
# Audit all installed skills
# Usage: ./audit-all.sh

SCRIPT_DIR=$(dirname "$0")
AUDIT_SCRIPT="$SCRIPT_DIR/audit.sh"

echo "========================================"
echo "🔒 FULL SKILL SECURITY AUDIT"
echo "========================================"
echo ""

TOTAL_CRITICAL=0
TOTAL_HIGH=0
TOTAL_CLEAN=0

# Audit built-in skills
echo "📦 Built-in Skills:"
echo "-------------------"
BUILTIN_DIR="$HOME/.npm-global/lib/node_modules/openclaw/skills"
if [ -d "$BUILTIN_DIR" ]; then
    for skill in "$BUILTIN_DIR"/*/; do
        name=$(basename "$skill")
        result=$("$AUDIT_SCRIPT" "$skill" 2>&1 | tail -5)
        
        if echo "$result" | grep -q "CRITICAL"; then
            echo "  🚨 $name - CRITICAL"
            TOTAL_CRITICAL=$((TOTAL_CRITICAL + 1))
        elif echo "$result" | grep -q "HIGH"; then
            echo "  🔴 $name - HIGH"
            TOTAL_HIGH=$((TOTAL_HIGH + 1))
        elif echo "$result" | grep -q "MEDIUM"; then
            echo "  🟡 $name - MEDIUM"
        else
            echo "  ✅ $name"
            TOTAL_CLEAN=$((TOTAL_CLEAN + 1))
        fi
    done
fi

echo ""

# Audit custom skills
echo "📦 Custom Skills:"
echo "-----------------"
CUSTOM_DIR="$HOME/skills"
if [ -d "$CUSTOM_DIR" ]; then
    for skill in "$CUSTOM_DIR"/*/; do
        name=$(basename "$skill")
        
        # Skip self
        if [ "$name" = "skill-security" ]; then
            echo "  ⏭️  $name (self)"
            continue
        fi
        
        result=$("$AUDIT_SCRIPT" "$skill" 2>&1 | tail -5)
        
        if echo "$result" | grep -q "CRITICAL"; then
            echo "  🚨 $name - CRITICAL"
            TOTAL_CRITICAL=$((TOTAL_CRITICAL + 1))
        elif echo "$result" | grep -q "HIGH"; then
            echo "  🔴 $name - HIGH"
            TOTAL_HIGH=$((TOTAL_HIGH + 1))
        elif echo "$result" | grep -q "MEDIUM"; then
            echo "  🟡 $name - MEDIUM"
        else
            echo "  ✅ $name"
            TOTAL_CLEAN=$((TOTAL_CLEAN + 1))
        fi
    done
fi

echo ""
echo "========================================"
echo "📊 OVERALL SUMMARY"
echo "========================================"
echo "  Clean:    $TOTAL_CLEAN"
echo "  Critical: $TOTAL_CRITICAL"
echo "  High:     $TOTAL_HIGH"

if [ $TOTAL_CRITICAL -gt 0 ]; then
    echo ""
    echo "⛔ ACTION REQUIRED: $TOTAL_CRITICAL skills have critical issues!"
    exit 2
elif [ $TOTAL_HIGH -gt 0 ]; then
    echo ""
    echo "⚠️  REVIEW NEEDED: $TOTAL_HIGH skills need manual review"
    exit 1
else
    echo ""
    echo "✅ All skills passed security audit"
    exit 0
fi
