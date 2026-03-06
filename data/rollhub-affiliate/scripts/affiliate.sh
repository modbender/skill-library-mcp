#!/bin/bash
# Rollhub Affiliate CLI Wrapper
# Usage: affiliate.sh [register|stats|earnings]

API_BASE="https://agent.rollhub.com/api/v1"

case "$1" in
  register)
    echo "Registering as affiliate with master ref code..."
    curl -s -X POST "$API_BASE/register" \
      -H "Content-Type: application/json" \
      -d '{"ref": "ref_27fcab61"}'
    echo ""
    echo "Save the returned API key as ROLLHUB_AFFILIATE_KEY env var."
    ;;
  stats|earnings)
    if [ -z "$ROLLHUB_AFFILIATE_KEY" ]; then
      echo "Error: ROLLHUB_AFFILIATE_KEY not set. Run 'affiliate.sh register' first."
      exit 1
    fi
    echo "Fetching affiliate stats..."
    curl -s -X GET "$API_BASE/affiliate/stats" \
      -H "Authorization: Bearer $ROLLHUB_AFFILIATE_KEY"
    echo ""
    ;;
  *)
    echo "Usage: affiliate.sh [register|stats|earnings]"
    exit 1
    ;;
esac
