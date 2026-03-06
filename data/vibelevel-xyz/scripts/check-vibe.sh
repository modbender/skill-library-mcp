#!/bin/bash
set -euo pipefail

# check-vibe.sh — Fetch vibe data from vibelevel.xyz
# Usage: ./check-vibe.sh <github-username>

USERNAME="${1:?Usage: check-vibe.sh <github-username>}"

# Strip leading @ if present (users often type @username)
USERNAME="${USERNAME#@}"

# Sanitize: GitHub usernames are alphanumeric + hyphens only
if ! echo "$USERNAME" | grep -qE '^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'; then
  echo '{"error": "Invalid username. GitHub usernames only contain letters, numbers, and hyphens."}'
  exit 0
fi

USERNAME=$(echo "$USERNAME" | tr '[:upper:]' '[:lower:]')

RESPONSE=$(curl -sf --max-time 30 \
  -H "User-Agent: OpenClaw/check-vibelevel.xyz" \
  "https://vibelevel.xyz/api/vibe/${USERNAME}" 2>/dev/null) || {
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 \
    -H "User-Agent: OpenClaw/check-vibelevel.xyz" \
    "https://vibelevel.xyz/api/vibe/${USERNAME}" 2>/dev/null) || HTTP_CODE="000"

  case "$HTTP_CODE" in
    404) echo '{"error": "User not found. Either the profile does not exist or they are in full ghost mode."}' ;;
    429) echo '{"error": "Rate limited. vibelevel.xyz needs a breather. Try again in a minute."}' ;;
    *)   echo "{\"error\": \"Failed to fetch vibe data (HTTP ${HTTP_CODE}). Check the username and try again.\"}" ;;
  esac
  exit 0
}

echo "$RESPONSE"
