#!/bin/bash
# Add transactions to the store
# Usage: echo '[{...}]' | ./add-transactions.sh [source_name]

FINANCE_DIR="${HOME}/.openclaw/workspace/finance"
STORE="${FINANCE_DIR}/transactions.json"
SOURCE="${1:-manual}"

mkdir -p "$FINANCE_DIR/statements"

# Initialize store if doesn't exist
if [ ! -f "$STORE" ]; then
  echo '{"transactions":[],"accounts":[]}' > "$STORE"
fi

# Read new transactions from stdin
NEW_TXS=$(cat)

# Add source and timestamp to each transaction, merge into store
jq --arg source "$SOURCE" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson new "$NEW_TXS" \
  '.transactions += ($new | map(. + {source: $source, added: $now, id: (now | tostring + "-" + (. | @base64 | .[0:8]))}))' \
  "$STORE" > "${STORE}.tmp" && mv "${STORE}.tmp" "$STORE"

echo "Added $(echo "$NEW_TXS" | jq length) transactions from $SOURCE"
