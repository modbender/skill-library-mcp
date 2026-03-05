#!/bin/bash
# Skill Security Scanner - Helper Script
# Usage: ./scan-skill.sh <skill-path>

SKILL_PATH="$1"

if [ -z "$SKILL_PATH" ]; then
    echo "Usage: scan-skill.sh <skill-path>"
    exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
    echo "Error: $SKILL_PATH does not exist"
    exit 1
fi

SKILL_NAME=$(basename "$SKILL_PATH")
SKILL_FILE="$SKILL_PATH/SKILL.md"

if [ ! -f "$SKILL_FILE" ]; then
    echo "Error: SKILL.md not found in $SKILL_PATH"
    exit 1
fi

echo "🔍 Scanning: $SKILL_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check for suspicious patterns (in actual code, not examples)
ISSUES=()
GREEN_FLAGS=()

# Network exfiltration - look for actual calls, not examples
if grep -qE "^\s*(curl|wget|fetch|axios).*https?://" "$SKILL_FILE" 2>/dev/null; then
    if ! grep -qE "api\.(github|openclaw)" "$SKILL_FILE" 2>/dev/null; then
        ISSUES+=("[MEDIUM] Makes network calls to external domains")
    fi
fi

# Check metadata for env vars requesting secrets
if grep -qE "env:.*(KEY|TOKEN|SECRET|PASSWORD)" "$SKILL_FILE" 2>/dev/null; then
    ISSUES+=("[LOW] Requests API keys/tokens - verify needed")
    GREEN_FLAGS+=("Standard for integration skills")
fi

# Check for bins
BINS=$(grep -E "^\s*-\s+[a-z]" "$SKILL_FILE" 2>/dev/null | head -10 | sed 's/^[[:space:]]*- //' | tr '\n' ',' || echo "none")
if [ -z "$BINS" ]; then
    BINS="none"
fi

# Check metadata
if grep -qE "(name:|description:)" "$SKILL_FILE" 2>/dev/null; then
    GREEN_FLAGS+=("Has proper metadata")
fi

# Check for documentation
if grep -qE "^## " "$SKILL_FILE" 2>/dev/null; then
    GREEN_FLAGS+=("Well documented")
fi

# Calculate trust score
SCORE=70  # Base score

# Deduct for issues
for issue in "${ISSUES[@]}"; do
    if [[ "$issue" == *"[HIGH]"* ]]; then
        SCORE=$((SCORE - 20))
    elif [[ "$issue" == *"[MEDIUM]"* ]]; then
        SCORE=$((SCORE - 10))
    elif [[ "$issue" == *"[LOW]"* ]]; then
        SCORE=$((SCORE - 5))
    fi
done

# Add for green flags (max +15)
GREEN_COUNT=${#GREEN_FLAGS[@]}
if [ $GREEN_COUNT -gt 0 ]; then
    ADDED=$((GREEN_COUNT * 5))
    if [ $ADDED -gt 15 ]; then ADDED=15; fi
    SCORE=$((SCORE + ADDED))
fi

# Check for official skills
if [[ "$SKILL_PATH" == *"openclaw/skills"* ]] || [[ "$SKILL_PATH" == *"/openclaw/skills/"* ]]; then
    SCORE=$((SCORE + 20))
    GREEN_FLAGS+=("Official OpenClaw skill")
fi

# Clamp score
if [ $SCORE -lt 0 ]; then SCORE=0; fi
if [ $SCORE -gt 100 ]; then SCORE=100; fi

# Risk level
if [ $SCORE -ge 80 ]; then
    RISK="🟢 Low"
elif [ $SCORE -ge 60 ]; then
    RISK="🟡 Medium"
elif [ $SCORE -ge 40 ]; then
    RISK="🟠 High"
else
    RISK="🔴 Critical"
fi

echo "📊 Trust Score: $SCORE/100 ($RISK)"
echo ""
echo "📋 Permissions:"
echo "   • bins: $BINS"
echo ""

if [ ${#ISSUES[@]} -gt 0 ]; then
    echo "⚠️ Issues Found:"
    for issue in "${ISSUES[@]}"; do
        echo "   • $issue"
    done
    echo ""
fi

if [ ${#GREEN_FLAGS[@]} -gt 0 ]; then
    echo "✅ Positive Signs:"
    for flag in "${GREEN_FLAGS[@]}"; do
        echo "   • $flag"
    done
    echo ""
fi

# Recommendation
echo "💡 Recommendation:"
if [ $SCORE -ge 80 ]; then
    echo "   Safe to use - well documented, standard permissions"
elif [ $SCORE -ge 60 ]; then
    echo "   Review before use, monitor usage"
elif [ $SCORE -ge 40 ]; then
    echo "   Use with caution in sandbox"
else
    echo "   Review carefully - multiple risk factors"
fi
