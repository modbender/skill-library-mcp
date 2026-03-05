#!/usr/bin/env bash
# SECURITY MANIFEST:
# Environment variables accessed: MDA_API_TOKEN (only)
# External endpoints called: https://markdownanything.com/api/v1/credits (only)
# Local files read: none
# Local files written: none

set -euo pipefail

RESPONSE=$(curl --silent --fail --show-error \
    -H "Authorization: Bearer ${MDA_API_TOKEN:?MDA_API_TOKEN is not set}" \
    "https://markdownanything.com/api/v1/credits")

python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Balance: {data['balance']} credits\")
print(f\"Plan: {data.get('plan', 'Unknown')}\")
" <<< "$RESPONSE"
