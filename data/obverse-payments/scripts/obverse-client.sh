#!/usr/bin/env bash
# Obverse API client helper for OpenClaw agents
# Requires: OBVERSE_API_URL and OBVERSE_API_KEY environment variables

set -euo pipefail

if [ -z "${OBVERSE_API_URL:-}" ]; then
  echo "Error: OBVERSE_API_URL is not set" >&2
  exit 1
fi

if [ -z "${OBVERSE_API_KEY:-}" ]; then
  echo "Error: OBVERSE_API_KEY is not set" >&2
  exit 1
fi

AUTH_HEADER="X-API-Key: $OBVERSE_API_KEY"

usage() {
  cat <<EOF
Usage: obverse-client.sh <command> [args]

Commands:
  get-link <linkCode>            Get payment link details
  list-payments <linkCode>       List payments for a link
  submit-payment <json-file>     Submit a payment (reads JSON from file or stdin)
  balance <userId> [chain]       Check wallet balance (chain defaults to solana)
  swagger                        Print Swagger docs URL

Examples:
  obverse-client.sh get-link x7k9m2
  obverse-client.sh list-payments x7k9m2
  obverse-client.sh balance 123456789 solana
  echo '{"linkCode":"x7k9m2",...}' | obverse-client.sh submit-payment -
EOF
  exit 1
}

[ $# -lt 1 ] && usage

case "$1" in
  get-link)
    [ $# -lt 2 ] && { echo "Error: linkCode required" >&2; exit 1; }
    curl -sf -H "$AUTH_HEADER" -H "Accept: application/json" \
      "$OBVERSE_API_URL/payment-links/$2"
    ;;

  list-payments)
    [ $# -lt 2 ] && { echo "Error: linkCode required" >&2; exit 1; }
    curl -sf -H "$AUTH_HEADER" \
      "$OBVERSE_API_URL/payments/link/$2"
    ;;

  submit-payment)
    [ $# -lt 2 ] && { echo "Error: JSON file path or - for stdin required" >&2; exit 1; }
    if [ "$2" = "-" ]; then
      curl -sf -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
        -d @- "$OBVERSE_API_URL/payments"
    else
      curl -sf -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
        -d @"$2" "$OBVERSE_API_URL/payments"
    fi
    ;;

  balance)
    [ $# -lt 2 ] && { echo "Error: userId required" >&2; exit 1; }
    CHAIN="${3:-solana}"
    curl -sf -H "$AUTH_HEADER" \
      "$OBVERSE_API_URL/wallet/$2/balance?chain=$CHAIN"
    ;;

  swagger)
    echo "$OBVERSE_API_URL/api-docs"
    ;;

  *)
    echo "Unknown command: $1" >&2
    usage
    ;;
esac
