#!/bin/bash
# Query transactions
# Usage: ./query.sh [command] [args]
# Commands: summary, category, range, search

STORE="${HOME}/.openclaw/workspace/finance/transactions.json"

if [ ! -f "$STORE" ]; then
  echo "No transactions found"
  exit 1
fi

case "$1" in
  summary)
    # Overall spending summary
    jq -r '.transactions | group_by(.category) | map({category: .[0].category, total: (map(.amount) | add), count: length}) | sort_by(.total) | .[] | "\(.category): $\(.total | fabs | . * 100 | floor / 100) (\(.count) txns)"' "$STORE"
    ;;
  category)
    # Filter by category
    jq --arg cat "$2" '.transactions | map(select(.category == $cat))' "$STORE"
    ;;
  range)
    # Filter by date range: ./query.sh range 2026-01-01 2026-01-31
    jq --arg start "$2" --arg end "$3" '.transactions | map(select(.date >= $start and .date <= $end))' "$STORE"
    ;;
  search)
    # Search merchant names
    jq --arg q "$2" '.transactions | map(select(.merchant | ascii_downcase | contains($q | ascii_downcase)))' "$STORE"
    ;;
  recent)
    # Last N transactions (default 10)
    N="${2:-10}"
    jq --argjson n "$N" '.transactions | sort_by(.date) | reverse | .[:$n]' "$STORE"
    ;;
  total)
    # Total spending in date range
    jq --arg start "$2" --arg end "$3" '[.transactions[] | select(.date >= $start and .date <= $end and .amount < 0) | .amount] | add | fabs' "$STORE"
    ;;
  *)
    echo "Commands: summary, category <cat>, range <start> <end>, search <term>, recent [n], total <start> <end>"
    ;;
esac
