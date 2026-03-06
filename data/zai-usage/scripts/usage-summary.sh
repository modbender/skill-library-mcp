#!/bin/bash
# Z.AI Usage Monitor - Check quota and subscription status
#
# Usage:
#   ./usage-summary.sh
#
# Output:
#   Formatted usage report with progress bars and status indicators
#
# Requirements:
#   - curl, jq, bc
#   - ZAI_JWT_TOKEN environment variable
#
# Setup:
#   1. Get token from: https://z.ai/manage-apikey/subscription
#      (DevTools → Application → Local Storage → z-ai-open-platform-token-production)
#   2. Store in ~/.openclaw/secrets/zai.env:
#      ZAI_JWT_TOKEN=eyJhbGci...
#
# Source: https://github.com/zereraz/tokensight

set -e

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load token from multiple possible locations
load_token() {
    # Try environment first
    if [ -n "$ZAI_JWT_TOKEN" ]; then
        return 0
    fi

    # Try OpenClaw secrets
    if [ -f ~/.openclaw/secrets/zai.env ]; then
        source ~/.openclaw/secrets/zai.env
        [ -n "$ZAI_JWT_TOKEN" ] && return 0
    fi

    # Try skill directory
    if [ -f "$SKILL_DIR/.env" ]; then
        source "$SKILL_DIR/.env"
        [ -n "$ZAI_JWT_TOKEN" ] && return 0
    fi

    # Try home directory
    if [ -f ~/.zai.env ]; then
        source ~/.zai.env
        [ -n "$ZAI_JWT_TOKEN" ] && return 0
    fi

    return 1
}

# Check if required tools are available
check_requirements() {
    local missing=()

    command -v curl >/dev/null 2>&1 || missing+=("curl")
    command -v jq >/dev/null 2>&1 || missing+=("jq")

    if [ ${#missing[@]} -gt 0 ]; then
        echo "Error: Missing required tools: ${missing[*]}"
        echo "Install with: sudo apt install ${missing[*]}"
        exit 1
    fi
}

# Format large numbers (1000000 → 1M)
format_number() {
    local num=$1
    if command -v bc >/dev/null 2>&1; then
        if [ "$num" -ge 1000000 ] 2>/dev/null; then
            echo "scale=1; $num / 1000000" | bc | sed 's/\.0$//' | tr -d '\n'
            echo "M"
        elif [ "$num" -ge 1000 ] 2>/dev/null; then
            echo "scale=1; $num / 1000" | bc | sed 's/\.0$//' | tr -d '\n'
            echo "K"
        else
            echo "$num"
        fi
    else
        echo "$num"
    fi
}

# Format milliseconds to human-readable time
format_time() {
    local ms=$1
    local seconds=$((ms / 1000))
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))

    if [ "$hours" -gt 0 ]; then
        echo "${hours}h ${minutes}m"
    else
        echo "${minutes}m"
    fi
}

# Format timestamp to date
format_date() {
    local ts=$1
    if date -d "@$((ts / 1000))" "+%Y-%m-%d" 2>/dev/null; then
        return
    elif date -r "$((ts / 1000))" "+%Y-%m-%d" 2>/dev/null; then
        return
    else
        echo "unknown"
    fi
}

# Main
check_requirements

if ! load_token; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           Z.AI Usage - Not Configured                      ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Setup required:"
    echo ""
    echo "1. Get your token:"
    echo "   https://z.ai/manage-apikey/subscription"
    echo "   (DevTools → Application → Local Storage → z-ai-open-platform-token-production)"
    echo ""
    echo "2. Store it:"
    echo "   echo 'ZAI_JWT_TOKEN=eyJhbGci...' > ~/.openclaw/secrets/zai.env"
    echo ""
    echo "Reference: https://github.com/zereraz/tokensight"
    exit 1
fi

# Make API request
RESPONSE=$(curl -s -H "Authorization: Bearer $ZAI_JWT_TOKEN" \
  -H "Accept: application/json" \
  "https://api.z.ai/api/monitor/usage/quota/limit" 2>/dev/null)

# Check for errors
if echo "$RESPONSE" | jq -e '.success == false' >/dev/null 2>&1; then
    ERROR=$(echo "$RESPONSE" | jq -r '.msg // "Unknown error"')
    echo "❌ API Error: $ERROR"
    echo ""
    echo "Your token may have expired. Get a fresh one from:"
    echo "https://z.ai/manage-apikey/subscription"
    exit 1
fi

# Parse response
LEVEL=$(echo "$RESPONSE" | jq -r '.data.level // "unknown"')

# Print header
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Z.AI GLM Coding Plan Usage                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Subscription level
LEVEL_DISPLAY=$(echo "$LEVEL" | sed 's/\b\(.\)/\u\1/')
echo "Subscription: GLM Coding $LEVEL_DISPLAY"
echo ""

# Process each limit type
echo "$RESPONSE" | jq -r '.data.limits[] | @base64' | while read -r LIMIT_B64; do
    LIMIT_DATA=$(echo "$LIMIT_B64" | base64 -d)
    TYPE=$(echo "$LIMIT_DATA" | jq -r '.type')
    UNIT=$(echo "$LIMIT_DATA" | jq -r '.unit')
    PERCENTAGE=$(echo "$LIMIT_DATA" | jq -r '.percentage')
    NEXT_RESET=$(echo "$LIMIT_DATA" | jq -r '.nextResetTime')
    NUMBER=$(echo "$LIMIT_DATA" | jq -r '.number')

    if [ "$TYPE" = "TOKENS_LIMIT" ] && [ "$UNIT" = "3" ]; then
        echo "5-Hour Token Quota:"

        # Estimate total based on plan
        if [ "$LEVEL" = "pro" ]; then
            TOTAL=200000000
        else
            TOTAL=100000000
        fi

        USED=$((TOTAL * PERCENTAGE / 100))
        REMAINING=$((TOTAL - USED))

        echo "   $(format_number $USED) / $(format_number $TOTAL) tokens ($PERCENTAGE%)"

        # Progress bar
        FILLED=$((PERCENTAGE / 5))
        EMPTY=$((20 - FILLED))
        BAR=$(printf '█%.0s' $(seq 1 $FILLED 2>/dev/null))$(printf '░%.0s' $(seq 1 $EMPTY 2>/dev/null))
        echo "   [$BAR]"

        echo "   $(format_number $REMAINING) remaining"

        # Reset time
        if [ "$NEXT_RESET" != "null" ] && [ -n "$NEXT_RESET" ]; then
            CURRENT_TIME=$(date +%s)000
            TIME_DIFF=$((NEXT_RESET - CURRENT_TIME))
            if [ "$TIME_DIFF" -gt 0 ]; then
                echo "   Resets in: $(format_time $TIME_DIFF)"
            fi
        fi
        echo ""

    elif [ "$TYPE" = "TOKENS_LIMIT" ] && [ "$UNIT" = "6" ]; then
        echo "Monthly Quota:"
        echo "   $PERCENTAGE% used"

        if [ "$NEXT_RESET" != "null" ] && [ -n "$NEXT_RESET" ]; then
            RESET_DATE=$(format_date "$NEXT_RESET")
            echo "   Resets: $RESET_DATE"
        fi
        echo ""

    elif [ "$TYPE" = "TIME_LIMIT" ]; then
        USAGE=$(echo "$LIMIT_DATA" | jq -r '.usage')
        REMAINING=$(echo "$LIMIT_DATA" | jq -r '.remaining')

        echo "Web Tools (Monthly):"
        echo "   $USAGE / $((USAGE + REMAINING)) calls ($PERCENTAGE%)"
        echo "   $REMAINING remaining"
        echo ""
    fi
done

# Status indicator
if [ "$PERCENTAGE" -lt 50 ] 2>/dev/null; then
    echo "Status: ✅ Good"
elif [ "$PERCENTAGE" -lt 80 ] 2>/dev/null; then
    echo "Status: ⚠️  Moderate usage"
else
    echo "Status: 🔴 High usage - consider monitoring"
fi
