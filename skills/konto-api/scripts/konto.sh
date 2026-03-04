#!/bin/bash
source ~/.openclaw/secrets/konto.env
URL="${KONTO_URL:-https://konto.angelstreet.io}"
AUTH="Authorization: Bearer $KONTO_API_KEY"

case ${1:-summary} in
  summary)      curl -s -H "$AUTH" "$URL/api/v1/summary" ;;
  accounts)     curl -s -H "$AUTH" "$URL/api/v1/accounts" ;;
  invest*)      curl -s -H "$AUTH" "$URL/api/v1/investments" ;;
  loans)        curl -s -H "$AUTH" "$URL/api/v1/loans" ;;
  assets)       curl -s -H "$AUTH" "$URL/api/v1/assets" ;;
  tx*|trans*)   curl -s -H "$AUTH" "$URL/api/v1/transactions?months=${2:-6}${3:+&category=$3}" ;;
  analytics)    curl -s -H "$AUTH" "$URL/api/v1/analytics/${2:-demographics}" ;;
  *) echo "Usage: konto.sh {summary|accounts|investments|loans|assets|transactions [months] [category]|analytics [type]}" ;;
esac
