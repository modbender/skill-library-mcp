#!/bin/bash
# top-slow-transactions.sh — Find the 10 slowest transactions for an app
# Usage: ./top-slow-transactions.sh <app-name> [minutes-ago]
# Example: ./top-slow-transactions.sh my-app 60

set -euo pipefail

APP="${1:?Usage: $0 <app-name> [minutes-ago]}"
SINCE="${2:-60}"

if [[ -z "${NEW_RELIC_API_KEY:-}" || -z "${NEW_RELIC_ACCOUNT_ID:-}" ]]; then
  echo "ERROR: NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID must be set"
  exit 1
fi

echo "=== Top 10 Slowest Transactions: $APP (last ${SINCE} minutes) ==="
echo ""

echo "--- By Average Duration ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT average(duration) AS 'Avg (s)', percentile(duration, 95) AS 'P95 (s)', count(*) AS 'Calls'
  FROM Transaction
  WHERE appName = '$APP'
  FACET name
  SINCE ${SINCE} minutes ago
  LIMIT 10
  ORDER BY average(duration) DESC
"

echo ""
echo "--- DB-Heavy Transactions (DB time > 50% of total) ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT average(duration) AS 'Total (s)',
         average(databaseDuration) AS 'DB (s)',
         percentage(average(databaseDuration), average(duration)) AS 'DB %'
  FROM Transaction
  WHERE appName = '$APP' AND databaseDuration > 0
  FACET name
  SINCE ${SINCE} minutes ago
  LIMIT 10
  ORDER BY average(databaseDuration) DESC
"

echo ""
echo "--- Slowest Individual DB Queries ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT average(duration) AS 'Avg (s)', count(*) AS 'Executions'
  FROM DatabaseTrace
  WHERE appName = '$APP'
  FACET statement
  SINCE ${SINCE} minutes ago
  LIMIT 10
  ORDER BY average(duration) DESC
"
