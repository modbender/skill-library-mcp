#!/usr/bin/env bash
# Firecrawl CLI wrapper for Deep Scout Stage 3 fetching.
# Gracefully handles missing Firecrawl installation.
#
# Usage: ./firecrawl-wrap.sh <url> [max_chars]

URL="${1:-}"
MAX_CHARS="${2:-8000}"

if [[ -z "$URL" ]]; then
  echo '{"error": "URL required"}' >&2
  exit 1
fi

# Check if firecrawl CLI is available
if ! command -v firecrawl &>/dev/null; then
  echo "FIRECRAWL_UNAVAILABLE" 
  exit 0
fi

# Validate URL format (must start with http:// or https://)
if [[ ! "$URL" =~ ^https?:// ]]; then
  echo '{"error": "Invalid URL: must start with http:// or https://"}' >&2
  exit 1
fi

# Run firecrawl with timeout (-- prevents URL from being parsed as flags)
result=$(timeout 30 firecrawl scrape -- "$URL" --format markdown 2>/dev/null || echo "")

if [[ -z "$result" || ${#result} -lt 100 ]]; then
  echo "FIRECRAWL_EMPTY"
  exit 0
fi

# Truncate to max_chars
echo "${result:0:$MAX_CHARS}"
