#!/usr/bin/env bash
#
# monitor-balance.sh - Monitor Grove account balance and alert on low balance
#
# Usage:
#   ./monitor-balance.sh [options]
#
# Options:
#   --threshold <amount>    Alert when balance drops below this (default: 0.10)
#   --interval <seconds>    Check interval in seconds (default: 300)
#   --webhook <url>         Send alerts to webhook URL
#   --log <file>            Log balance checks to file
#   --once                  Check once and exit
#   --help                  Show this help message
#
# Full documentation: https://grove.city/docs/skills
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
THRESHOLD="0.10"
INTERVAL=300  # 5 minutes
WEBHOOK_URL=""
LOG_FILE=""
CHECK_ONCE=false
ALERT_SENT=false

# Usage function
usage() {
    cat << EOF
Usage: $0 [options]

Monitor Grove account balance and alert on low balance.

Options:
    --threshold <amount>    Alert when balance < amount (default: 0.10)
    --interval <seconds>    Check interval (default: 300)
    --webhook <url>         Send alerts to webhook URL
    --log <file>            Log balance checks to file
    --once                  Check once and exit
    --help                  Show this help message

Examples:
    $0                                              # Monitor with defaults
    $0 --threshold 1.00 --interval 60               # Check every minute
    $0 --webhook https://hooks.slack.com/...        # Send Slack alerts
    $0 --log ~/balance.log                          # Log to file
    $0 --once                                       # Single check

Webhook payload (JSON):
    {
      "balance": "0.05",
      "threshold": "0.10",
      "timestamp": "2026-02-06T14:30:00Z",
      "message": "Low balance alert"
    }

EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --threshold)
            THRESHOLD="$2"
            shift 2
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --webhook)
            WEBHOOK_URL="$2"
            shift 2
            ;;
        --log)
            LOG_FILE="$2"
            shift 2
            ;;
        --once)
            CHECK_ONCE=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown argument: $1${NC}" >&2
            usage
            ;;
    esac
done

# Check if grove CLI is available
if ! command -v grove &> /dev/null; then
    echo -e "${RED}Error: grove CLI not found${NC}" >&2
    echo "Install with: curl -fsSL https://grove.city/install-cli.sh | bash" >&2
    exit 1
fi

# Check if bc is available (for floating point comparison)
if ! command -v bc &> /dev/null; then
    echo -e "${YELLOW}Warning: 'bc' not found, using integer comparison${NC}" >&2
fi

# Log function
log_message() {
    local msg="$1"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if [[ -n "$LOG_FILE" ]]; then
        echo "[$timestamp] $msg" >> "$LOG_FILE"
    fi
}

# Send webhook alert
send_webhook_alert() {
    local balance="$1"
    local threshold="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    if [[ -z "$WEBHOOK_URL" ]]; then
        return 0
    fi

    local payload=$(cat <<EOF
{
  "balance": "$balance",
  "threshold": "$threshold",
  "timestamp": "$timestamp",
  "message": "Grove balance is low: $balance USDC (threshold: $threshold USDC)"
}
EOF
)

    if command -v curl &> /dev/null; then
        curl -X POST -H "Content-Type: application/json" \
             -d "$payload" "$WEBHOOK_URL" \
             --silent --show-error > /dev/null 2>&1 || true
    fi
}

# Compare floating point numbers
compare_balance() {
    local balance="$1"
    local threshold="$2"

    if command -v bc &> /dev/null; then
        # Use bc for precise floating point comparison
        if (( $(echo "$balance < $threshold" | bc -l) )); then
            return 0  # balance < threshold
        else
            return 1  # balance >= threshold
        fi
    else
        # Fallback to integer comparison (multiply by 100 for cents)
        balance_cents=$(echo "$balance * 100" | awk '{print int($1)}')
        threshold_cents=$(echo "$threshold * 100" | awk '{print int($1)}')

        if [[ $balance_cents -lt $threshold_cents ]]; then
            return 0  # balance < threshold
        else
            return 1  # balance >= threshold
        fi
    fi
}

# Check balance function
check_balance() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Get balance
    local balance_json
    if ! balance_json=$(grove balance --json 2>&1); then
        echo -e "${RED}✗ Failed to check balance${NC}" >&2
        log_message "ERROR: Failed to check balance"
        return 1
    fi

    # Parse balance
    local balance
    if ! balance=$(echo "$balance_json" | jq -r '.total_balance' 2>/dev/null); then
        echo -e "${RED}✗ Failed to parse balance${NC}" >&2
        log_message "ERROR: Failed to parse balance"
        return 1
    fi

    # Display balance
    printf "[%s] Balance: %s USDC" "$timestamp" "$balance"

    # Check threshold
    if compare_balance "$balance" "$THRESHOLD"; then
        echo -e " ${RED}⚠️  LOW BALANCE${NC}"
        log_message "LOW BALANCE: $balance USDC (threshold: $THRESHOLD USDC)"

        # Send alert (only once until balance is restored)
        if [[ "$ALERT_SENT" == "false" ]]; then
            send_webhook_alert "$balance" "$THRESHOLD"
            ALERT_SENT=true
        fi

        return 2  # Low balance
    else
        echo -e " ${GREEN}✓${NC}"
        log_message "OK: $balance USDC (threshold: $THRESHOLD USDC)"

        # Reset alert flag when balance is restored
        ALERT_SENT=false

        return 0  # Balance OK
    fi
}

# Main monitoring loop
echo -e "${BLUE}🔍 Grove Balance Monitor${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Threshold:      $THRESHOLD USDC"
echo "Check interval: $INTERVAL seconds"
if [[ -n "$WEBHOOK_URL" ]]; then
    echo "Webhook:        Enabled"
fi
if [[ -n "$LOG_FILE" ]]; then
    echo "Log file:       $LOG_FILE"
fi
echo ""

# Check once mode
if [[ "$CHECK_ONCE" == "true" ]]; then
    check_balance
    exit $?
fi

# Continuous monitoring
echo "Monitoring... (Press Ctrl+C to stop)"
echo ""

while true; do
    check_balance

    # Wait for next check
    sleep "$INTERVAL"
done
