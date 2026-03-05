#!/usr/bin/env bash
# Credential Tracker - Check expiry dates
# Run weekly via cron

set -euo pipefail

CREDENTIALS_FILE="$HOME/.openclaw/workspace/.credentials.json"
STATE_FILE="$HOME/.openclaw/workspace/.credential-tracker-state.json"
ALERT_DAYS=14
CRITICAL_DAYS=7

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔐 Credential Tracker Check"
echo "============================"

if [[ ! -f "$CREDENTIALS_FILE" ]]; then
    echo "❌ No credentials file found: $CREDENTIALS_FILE"
    echo "   Create it from SKILL.md template"
    exit 1
fi

# Check if credentials array exists
if ! jq -e '.credentials' "$CREDENTIALS_FILE" >/dev/null 2>&1; then
    echo "❌ Invalid format: missing 'credentials' array"
    exit 1
fi

NOW=$(date +%s)
ALERTS=()

TOTAL=0
COUNT_OK=0
COUNT_WARNING=0
COUNT_CRITICAL=0
COUNT_EXPIRED=0

echo ""
echo "Checking credentials..."
echo ""

# Iterate credentials (avoid subshell so ALERTS persists)
while IFS= read -r cred; do
    NAME=$(echo "$cred" | jq -r '.name')
    TYPE=$(echo "$cred" | jq -r '.type')
    EXPIRES=$(echo "$cred" | jq -r '.expires')
    PROVIDER=$(echo "$cred" | jq -r '.provider // "N/A"')
    
    EXPIRES_EPOCH=$(date -d "$EXPIRES" +%s 2>/dev/null || echo "0")
    DAYS_LEFT=$(( (EXPIRES_EPOCH - NOW) / 86400 ))
    
    TOTAL=$((TOTAL+1))

    # Determine status
    if [[ "$DAYS_LEFT" -lt 0 ]]; then
        STATUS="${RED}EXPIRED!${NC}"
        LEVEL="expired"
        COUNT_EXPIRED=$((COUNT_EXPIRED+1))
    elif [[ "$DAYS_LEFT" -le "$CRITICAL_DAYS" ]]; then
        STATUS="${RED}CRITICAL ($DAYS_LEFT days)${NC}"
        LEVEL="critical"
        COUNT_CRITICAL=$((COUNT_CRITICAL+1))
    elif [[ "$DAYS_LEFT" -le "$ALERT_DAYS" ]]; then
        STATUS="${YELLOW}WARNING ($DAYS_LEFT days)${NC}"
        LEVEL="warning"
        COUNT_WARNING=$((COUNT_WARNING+1))
    else
        STATUS="${GREEN}OK ($DAYS_LEFT days)${NC}"
        LEVEL="ok"
        COUNT_OK=$((COUNT_OK+1))
    fi
    
    printf "%-30s %-15s %s\n" "$NAME" "$TYPE" "$STATUS"
    
    # Add to alerts if warning/critical/expired
    if [[ "$LEVEL" != "ok" ]]; then
        ALERTS+=("$NAME: $STATUS")
    fi
done < <(jq -c '.credentials[]' "$CREDENTIALS_FILE")

echo ""

# Summary
echo "Summary: $TOTAL total, $COUNT_EXPIRED expired, $COUNT_CRITICAL critical, $COUNT_WARNING warnings, $COUNT_OK ok"

# Output for cron (empty = all OK)
if [[ ${#ALERTS[@]} -gt 0 ]]; then
    echo ""
    echo "🚨 ALERTS:"
    for alert in "${ALERTS[@]}"; do
        echo "  - $alert"
    done
    echo ""
    # Exit with error so cron notifies
    exit 1
else
    echo ""
    echo "✅ All credentials OK"
    exit 0
fi
