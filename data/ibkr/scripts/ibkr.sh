#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$SCRIPT_DIR/ibkr_cli.py"

if [[ $# -eq 0 ]]; then
  cat <<'EOF'
Usage: ibkr.sh <command> [args]

Commands:
  account              account summary + positions
  account-summary      raw account summary tags
  positions            open positions
  portfolio            portfolio with pnl fields
  pnl                  account pnl snapshot
  quote                quote snapshot
  historical           historical bars
  place-order          place order
  cancel-order         cancel order by id
  open-orders          list open orders
  executions           list executions/fills
  contract-details     lookup contract metadata
  scanner              run scanner query

Examples:
  ibkr.sh account --account DU123456
  ibkr.sh quote --symbol AAPL --sec-type STK --market-data-type 3
  ibkr.sh historical --symbol EURUSD --sec-type CASH --duration "7 D" --bar-size "1 hour"
  ibkr.sh place-order --symbol AAPL --action BUY --quantity 10 --order-type LMT --limit-price 150
EOF
  exit 1
fi

cmd="$1"
shift

case "$cmd" in
  account)
    python3 "$CLI" account-summary "$@"
    python3 "$CLI" positions "$@"
    ;;
  account-summary|positions|portfolio|pnl|quote|historical|place-order|cancel-order|open-orders|executions|contract-details|scanner)
    python3 "$CLI" "$cmd" "$@"
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    exit 2
    ;;
esac
