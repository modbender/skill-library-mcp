#!/usr/bin/env bash
# Stock Market Intelligence CLI helper for OpenClaw agents.
# Usage: agenthc.sh <module_name> [--ticker TICKER] [--format FORMAT]
#
# Requires: AGENTHC_API_KEY environment variable
# Example: agenthc.sh market_intelligence
# Example: agenthc.sh technical_analysis --ticker AAPL --format agent

set -euo pipefail

BASE_URL="https://api.traderhc.com"

if [ -z "${AGENTHC_API_KEY:-}" ]; then
  echo "Error: AGENTHC_API_KEY not set" >&2
  echo "Register: curl -s -X POST '$BASE_URL/api/v1/agents/register' -H 'Content-Type: application/json' -d '{\"name\": \"MyAgent\"}'" >&2
  exit 1
fi

MODULE="${1:-}"
if [ -z "$MODULE" ]; then
  echo "Usage: agenthc.sh <module_name> [--ticker TICKER] [--format FORMAT]" >&2
  echo "Modules: market_intelligence, news_sentiment, crypto_intelligence, economic_calendar, technical_analysis, bond_intelligence, fed_intelligence, macro_intelligence, correlation_tracker, volatility_analyzer, sector_rotation, alpha_signals, regime_engine, tail_risk_engine, ..." >&2
  exit 1
fi

# Sanitize inputs: only allow alphanumeric, underscore, hyphen
if [[ ! "$MODULE" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Error: Invalid module name" >&2
  exit 1
fi

shift

# Parse optional arguments
TICKER=""
FORMAT="compact"
while [ $# -gt 0 ]; do
  case "$1" in
    --ticker) TICKER="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Sanitize ticker and format
if [ -n "$TICKER" ] && [[ ! "$TICKER" =~ ^[a-zA-Z0-9._-]+$ ]]; then
  echo "Error: Invalid ticker" >&2
  exit 1
fi
if [[ ! "$FORMAT" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Error: Invalid format" >&2
  exit 1
fi

# Build URL with sanitized inputs
URL="$BASE_URL/api/v1/intelligence/$MODULE?format=$FORMAT"
if [ -n "$TICKER" ]; then
  URL="$URL&ticker=$TICKER"
fi

curl -s "$URL" -H "X-API-Key: $AGENTHC_API_KEY" | jq '.'
