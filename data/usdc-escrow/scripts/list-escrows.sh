#!/bin/bash
# List escrows with optional filters
set -e

API_URL="${ESCROW_API_URL:-https://api.payclawback.xyz}"

QUERY=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --state)
      STATE_MAP=("active=0" "released=1" "disputed=2" "refunded=3" "expired=4")
      for mapping in "${STATE_MAP[@]}"; do
        key="${mapping%%=*}"
        val="${mapping##*=}"
        if [ "$2" = "$key" ]; then
          QUERY="${QUERY:+$QUERY&}state=$val"
          break
        fi
      done
      shift 2
      ;;
    --depositor)
      QUERY="${QUERY:+$QUERY&}depositor=$2"
      shift 2
      ;;
    *)
      echo "Usage: $0 [--state active|released|disputed|refunded|expired] [--depositor 0x...]"
      exit 1
      ;;
  esac
done

curl -s "${API_URL}/api/escrows${QUERY:+?$QUERY}" | jq .
