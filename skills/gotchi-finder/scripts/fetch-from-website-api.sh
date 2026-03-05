#!/bin/bash

GOTCHI_ID=$1

if [ -z "$GOTCHI_ID" ]; then
  echo "Usage: $0 <gotchi-id>"
  exit 1
fi

echo "Fetching gotchi #$GOTCHI_ID from Aavegotchi API..."

# Try the official API endpoint
curl -s "https://api.aavegotchi.com/v1/aavegotchi/${GOTCHI_ID}" \
  -H "Accept: application/json" | jq .

