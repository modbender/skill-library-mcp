#!/bin/bash
# Authenticate with MoltCities using stored API key
# Usage: source moltcities-auth.sh [key-path]
# Then use $MOLTCITIES_KEY in Authorization headers

set -euo pipefail

KEY_FILE="${1:-$HOME/.moltcities/api_key}"

if [ ! -f "$KEY_FILE" ]; then
  echo "Error: API key not found at $KEY_FILE" >&2
  echo "Register first: see references/registration.md" >&2
  exit 1
fi

MOLTCITIES_KEY=$(cat "$KEY_FILE")
echo "$MOLTCITIES_KEY"
