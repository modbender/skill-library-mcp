#!/bin/bash
# Shared Zoom authentication helper
# Usage: source "$(dirname "${BASH_SOURCE[0]}")/zoom_auth.sh"

zoom_get_token() {
  local creds_file="$1"
  local account_id client_id client_secret token

  account_id=$(jq -r '.account_id' "$creds_file")
  client_id=$(jq -r '.client_id' "$creds_file")
  client_secret=$(jq -r '.client_secret' "$creds_file")

  token=$(curl -s -X POST "https://zoom.us/oauth/token" \
    -H "Authorization: Basic $(echo -n "${client_id}:${client_secret}" | base64 | tr -d '\n')" \
    -d "grant_type=account_credentials&account_id=${account_id}" | jq -r '.access_token')

  if [ -z "$token" ] || [ "$token" = "null" ]; then
    echo "ERROR: Failed to get Zoom access token" >&2
    return 1
  fi

  echo "$token"
}
