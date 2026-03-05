#!/bin/bash
# Search for a token across all available exchanges
# Usage: ./search_token.sh --token BTC [--data trading_rules.json]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOKEN=""
DATA_FILE="$SCRIPT_DIR/../data/trading_rules.json"

while [[ $# -gt 0 ]]; do
    case $1 in
        --token) TOKEN="$2"; shift 2 ;;
        --data) DATA_FILE="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [[ -z "$TOKEN" ]]; then
    echo "Error: --token is required"
    echo "Usage: ./search_token.sh --token BTC"
    exit 1
fi

if [[ ! -f "$DATA_FILE" ]]; then
    echo "Error: Trading rules file not found: $DATA_FILE"
    echo "Run ./test_all.sh first to fetch trading rules"
    exit 1
fi

python3 << PYTHON
import json
import sys

token = "${TOKEN}".upper()
data_file = "${DATA_FILE}"

with open(data_file) as f:
    data = json.load(f)

print(f"\nSearching for {token} across all exchanges...\n")
print("| Exchange | Pair | Min Order | Min Price Inc | Order Types |")
print("|----------|------|-----------|---------------|-------------|")

found = 0
for exchange, pairs in data.items():
    for pair, rules in pairs.items():
        if token in pair.upper():
            found += 1
            min_order = rules.get('min_order_size', 'N/A')
            min_price = rules.get('min_price_increment', 'N/A')

            order_types = []
            if rules.get('supports_limit_orders'):
                order_types.append('Limit')
            if rules.get('supports_market_orders'):
                order_types.append('Market')

            # Format numbers nicely
            if isinstance(min_order, float):
                if min_order < 0.0001:
                    min_order = f"{min_order:.2e}"
                else:
                    min_order = f"{min_order:g}"
            if isinstance(min_price, float):
                if min_price < 0.0001:
                    min_price = f"{min_price:.2e}"
                else:
                    min_price = f"{min_price:g}"

            print(f"| {exchange} | {pair} | {min_order} | {min_price} | {', '.join(order_types)} |")

print(f"\nFound {found} pairs containing {token}")
PYTHON
