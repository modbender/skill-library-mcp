#!/bin/bash
set -e

CMD="${1:---about}"

case "$CMD" in
  --journal)
    echo "=== Journal Entry Template ==="
    echo "Date       | Account (Debit) | Account (Credit) | Amount"
    echo "-----------|-----------------|------------------|-------"
    echo "YYYY-MM-DD | Cash            | Revenue          | 0.00"
    echo ""
    echo "Use: ledger-engine.sh --journal to see the entry template."
    ;;
  --trial-balance)
    echo "=== Trial Balance Report ==="
    echo "Account          | Debit   | Credit"
    echo "-----------------|---------|-------"
    echo "Assets           | 0.00    |"
    echo "Liabilities      |         | 0.00"
    echo "Equity           |         | 0.00"
    echo "Revenue          |         | 0.00"
    echo "Expenses         | 0.00    |"
    echo "-----------------|---------|-------"
    echo "Total            | 0.00    | 0.00"
    ;;
  --about)
    echo "Bookkeeping Skill v0.1.0"
    echo "Copyright (c) 2026 Netsnek e.U."
    echo "Double-entry bookkeeping toolkit."
    echo "Website: https://netsnek.com"
    ;;
  *)
    echo "Unknown option: $CMD"
    echo "Usage: ledger-engine.sh [--journal|--trial-balance|--about]"
    exit 1
    ;;
esac