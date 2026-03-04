#!/bin/bash
# PT Site Search Helper

CRED_FILE="${HOME}/.clawdbot/credentials/pt-site/sites.json"
TORRENT_DIR="/tmp"

usage() {
  echo "Usage: pt-search.sh <site> <search term>"
  echo "Sites: $(jq -r '.sites | keys | join(", ")' "$CRED_FILE" 2>/dev/null)"
}

SITE="$1"
TERM="$2"

if [ -z "$SITE" ] || [ -z "$TERM" ]; then
  usage
  exit 1
fi

# Load site config
SITE_CONFIG=$(jq -r ".sites[\"$SITE\"]" "$CRED_FILE")
URL=$(echo "$SITE_CONFIG" | jq -r '.url')
COOKIE=$(echo "$SITE_CONFIG" | jq -r '.cookie')

# Search
SEARCH_URL="${URL}/torrents.php?search=$( echo "$TERM" | jq -Rs . )&search_type=0"
echo "Searching: $SEARCH_URL"

# This would be used with browser tool
echo "$SEARCH_URL"