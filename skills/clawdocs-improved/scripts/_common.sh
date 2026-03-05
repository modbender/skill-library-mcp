#!/bin/bash
# Shared library for clawddocs scripts
# Sources: constants, cache helpers, llms.txt parsing

DOCS_BASE="https://docs.openclaw.ai"
LLMS_URL="${DOCS_BASE}/llms.txt"
CACHE_DIR="${HOME}/.openclaw/cache/clawddocs"
CACHE_DOCS="${CACHE_DIR}/docs"
CACHE_INDEX="${CACHE_DIR}/index"
CACHE_SNAPSHOTS="${CACHE_DIR}/snapshots"
CACHE_TTL=3600          # 1 hour default
INDEX_CACHE_TTL=86400   # 24 hours for fetched docs
RECENT_CACHE_TTL=21600  # 6 hours for Last-Modified headers

ensure_cache_dir() {
  mkdir -p "${CACHE_DOCS}" "${CACHE_INDEX}" "${CACHE_SNAPSHOTS}"
}

# Check if a cached file is still fresh
# Usage: is_fresh <file> [ttl_seconds]
is_fresh() {
  local file="$1"
  local ttl="${2:-$CACHE_TTL}"
  [[ -f "$file" ]] || return 1
  local age=$(( $(date +%s) - $(stat -c %Y "$file" 2>/dev/null || echo 0) ))
  (( age < ttl ))
}

# Fetch llms.txt with caching and stale fallback
fetch_llms() {
  ensure_cache_dir
  local llms_cache="${CACHE_DIR}/llms.txt"
  if is_fresh "$llms_cache" "$CACHE_TTL"; then
    cat "$llms_cache"
    return 0
  fi
  local tmp="${llms_cache}.tmp"
  if curl -sfL --max-time 15 "$LLMS_URL" -o "$tmp" 2>/dev/null; then
    mv "$tmp" "$llms_cache"
    cat "$llms_cache"
  elif [[ -f "$llms_cache" ]]; then
    echo "[warn] Network failed, using stale cache" >&2
    cat "$llms_cache"
  else
    echo "[error] Cannot fetch llms.txt and no cache available" >&2
    return 1
  fi
}

# Parse llms.txt into tab-separated: title<TAB>url<TAB>category<TAB>path
parse_llms_entries() {
  fetch_llms | grep -E '^\- \[' | sed -E 's/^- \[([^]]+)\]\(([^)]+)\).*/\1\t\2/' | while IFS=$'\t' read -r title url; do
    local path="${url#${DOCS_BASE}/}"
    path="${path%.md}"
    local category="${path%%/*}"
    [[ "$path" == */* ]] || category="root"
    printf '%s\t%s\t%s\t%s\n' "$title" "$url" "$category" "$path"
  done
}

# Human-readable file size
human_size() {
  local bytes="$1"
  if (( bytes >= 1048576 )); then
    echo "$(( bytes / 1048576 ))M"
  elif (( bytes >= 1024 )); then
    echo "$(( bytes / 1024 ))K"
  else
    echo "${bytes}B"
  fi
}

# Human-readable age
human_age() {
  local seconds="$1"
  if (( seconds >= 86400 )); then
    echo "$(( seconds / 86400 ))d ago"
  elif (( seconds >= 3600 )); then
    echo "$(( seconds / 3600 ))h ago"
  elif (( seconds >= 60 )); then
    echo "$(( seconds / 60 ))m ago"
  else
    echo "${seconds}s ago"
  fi
}
