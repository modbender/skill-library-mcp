#!/bin/bash
# SearXNG Search Helper

PORT="${SEARXNG_PORT:-8080}"
HOST="${SEARXNG_HOST:-localhost}"
FORMAT="${SEARXNG_FORMAT:-json}"

if [ -z "$1" ]; then
    echo "Usage: $0 <search-query> [limit]"
    echo "Example: $0 'openclaw ai' 5"
    exit 1
fi

QUERY="$1"
LIMIT="${2:-10}"

curl -sL "http://${HOST}:${PORT}/search?q=${QUERY}&format=${FORMAT}" | jq ".results[:${LIMIT}] | .[] | {title, url, engine}"
