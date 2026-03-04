#!/bin/bash
# error-report.sh — Recent errors with messages and counts
# Usage: ./error-report.sh <app-name> [minutes-ago]
# Example: ./error-report.sh my-app 60

set -euo pipefail

APP="${1:?Usage: $0 <app-name> [minutes-ago]}"
SINCE="${2:-60}"

if [[ -z "${NEW_RELIC_API_KEY:-}" || -z "${NEW_RELIC_ACCOUNT_ID:-}" ]]; then
  echo "ERROR: NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID must be set"
  exit 1
fi

echo "=== Error Report: $APP (last ${SINCE} minutes) ==="
echo ""

echo "--- Overall Error Rate ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT count(*) AS 'Total Requests',
         filter(count(*), WHERE error IS true) AS 'Errors',
         percentage(count(*), WHERE error IS true) AS 'Error %'
  FROM Transaction
  WHERE appName = '$APP'
  SINCE ${SINCE} minutes ago
"

echo ""
echo "--- Errors by Transaction ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT count(*) AS 'Count'
  FROM TransactionError
  WHERE appName = '$APP'
  FACET transactionName
  SINCE ${SINCE} minutes ago
  LIMIT 10
  ORDER BY count(*) DESC
"

echo ""
echo "--- Errors by Class/Type ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT count(*) AS 'Count'
  FROM TransactionError
  WHERE appName = '$APP'
  FACET error.class
  SINCE ${SINCE} minutes ago
  LIMIT 10
  ORDER BY count(*) DESC
"

echo ""
echo "--- Recent Error Messages ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT timestamp, transactionName, error.class, message
  FROM TransactionError
  WHERE appName = '$APP'
  SINCE ${SINCE} minutes ago
  LIMIT 10
"
