#!/usr/bin/env bash
set -euo pipefail

API_KEY="${WORTHCLIP_API_KEY:?Set WORTHCLIP_API_KEY}"
BASE="https://greedy-mallard-11.convex.site/api/v1"

curl -s "$BASE/usage" \
  -H "Authorization: Bearer $API_KEY" | jq '.data'
