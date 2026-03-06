#!/bin/bash
# Fetch a specific doc page and output raw markdown
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

if [[ -z "$1" ]]; then
  echo "Usage: fetch-doc.sh <path>"
  echo "Example: fetch-doc.sh gateway/configuration"
  echo "         fetch-doc.sh channels/discord"
  exit 1
fi

ensure_cache_dir

# Normalize path: strip leading /, ensure .md suffix
path="$1"
path="${path#/}"
[[ "$path" == *.md ]] || path="${path}.md"

url="${DOCS_BASE}/${path}"
cache_file="${CACHE_DOCS}/${path}"
cache_dir="$(dirname "$cache_file")"
mkdir -p "$cache_dir"

# Use cache if fresh
if is_fresh "$cache_file" "$CACHE_TTL"; then
  cat "$cache_file"
  exit 0
fi

# Fetch with atomic write
tmp="${cache_file}.tmp.$$"
http_code=$(curl -sfL --max-time 30 -o "$tmp" -w '%{http_code}' "$url" 2>/dev/null)

if [[ "$http_code" == "200" ]] && [[ -s "$tmp" ]]; then
  mv "$tmp" "$cache_file"
  cat "$cache_file"
elif [[ -f "$cache_file" ]]; then
  rm -f "$tmp"
  echo "[warn] Fetch failed (HTTP ${http_code}), using stale cache" >&2
  cat "$cache_file"
else
  rm -f "$tmp"
  echo "[error] Failed to fetch ${url} (HTTP ${http_code})" >&2
  echo "Check path with: ./sitemap.sh | grep <keyword>" >&2
  exit 1
fi
