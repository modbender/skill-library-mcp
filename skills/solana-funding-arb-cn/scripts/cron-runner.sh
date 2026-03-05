#!/bin/bash
#
# Funding Arbitrage Cron Runner
# Run via crontab: 0 */4 * * * /path/to/cron-runner.sh
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$HOME/.clawd/funding-arb/logs"
LOG_FILE="$LOG_DIR/cron-$(date +%Y%m%d).log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Load environment
if [ -f "$HOME/.secrets/.env" ]; then
  source "$HOME/.secrets/.env"
fi

# Set defaults
export SOLANA_RPC_URL="${SOLANA_RPC_URL:-https://api.mainnet-beta.solana.com}"
export NODE_OPTIONS="--max-old-space-size=512"

# Run the trader
echo "========================================" >> "$LOG_FILE"
echo "[$(date)] Starting funding arb check..." >> "$LOG_FILE"

cd "$SCRIPT_DIR"
npx ts-node --transpile-only src/trading/auto-trader.ts >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

echo "[$(date)] Completed with exit code: $EXIT_CODE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Cleanup old logs (keep 7 days)
find "$LOG_DIR" -name "cron-*.log" -mtime +7 -delete

# Send notification if error
if [ $EXIT_CODE -ne 0 ]; then
  echo "Funding arb error! Check $LOG_FILE"
fi

exit $EXIT_CODE
