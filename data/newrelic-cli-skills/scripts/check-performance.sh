#!/bin/bash
# check-performance.sh — Quick performance health check across all monitored apps
# Usage: ./check-performance.sh [app-name] [minutes-ago]
# Example: ./check-performance.sh my-app 60

set -euo pipefail

APP="${1:-}"
SINCE="${2:-60}"

if [[ -z "${NEW_RELIC_API_KEY:-}" || -z "${NEW_RELIC_ACCOUNT_ID:-}" ]]; then
  echo "ERROR: NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID must be set"
  exit 1
fi

WHERE=""
if [[ -n "$APP" ]]; then
  WHERE="WHERE appName = '$APP'"
fi

echo "=== Performance Health Check (last ${SINCE} minutes) ==="
echo ""

echo "--- Response Time (avg + P95) ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT average(duration) AS 'Avg (s)', percentile(duration, 95) AS 'P95 (s)'
  FROM Transaction
  $WHERE
  FACET appName
  SINCE ${SINCE} minutes ago
  LIMIT 20
  ORDER BY average(duration) DESC
"

echo ""
echo "--- Error Rate ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT percentage(count(*), WHERE error IS true) AS 'Error %', count(*) AS 'Total Requests'
  FROM Transaction
  $WHERE
  FACET appName
  SINCE ${SINCE} minutes ago
  LIMIT 20
"

echo ""
echo "--- Throughput (RPM) ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT rate(count(*), 1 minute) AS 'RPM'
  FROM Transaction
  $WHERE
  FACET appName
  SINCE ${SINCE} minutes ago
  LIMIT 20
"

echo ""
echo "--- Top 5 Slowest Transactions ---"
newrelic nrql query --accountId "$NEW_RELIC_ACCOUNT_ID" --query "
  SELECT average(duration) AS 'Avg (s)', count(*) AS 'Calls'
  FROM Transaction
  $WHERE
  FACET appName, name
  SINCE ${SINCE} minutes ago
  LIMIT 5
  ORDER BY average(duration) DESC
"
