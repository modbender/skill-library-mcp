#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - Test API
# Test your API through the gateway

GATEWAY_URL="https://gateway.apiosk.com"

# Default values
SLUG=""
PATH_SUFFIX="/"
METHOD="GET"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --slug)
      SLUG="$2"
      shift 2
      ;;
    --path)
      PATH_SUFFIX="$2"
      shift 2
      ;;
    --method)
      METHOD="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 --slug SLUG [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --slug SLUG       API slug to test (required)"
      echo "  --path PATH       Path to test (default: /)"
      echo "  --method METHOD   HTTP method (default: GET)"
      echo "  --help            Show this help"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate required fields
if [[ -z "$SLUG" ]]; then
  echo "Error: --slug is required"
  echo "Run '$0 --help' for usage"
  exit 1
fi

# Build URL
URL="${GATEWAY_URL}/${SLUG}${PATH_SUFFIX}"

echo "Testing API..."
echo "  URL: $URL"
echo "  Method: $METHOD"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Make request
if [[ "$METHOD" == "GET" ]]; then
  curl -i "$URL"
elif [[ "$METHOD" == "HEAD" ]]; then
  curl -I "$URL"
else
  curl -i -X "$METHOD" "$URL"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Note: This probe sends no x402 payment proof."
echo "If the endpoint is paid, you may receive HTTP 402."
