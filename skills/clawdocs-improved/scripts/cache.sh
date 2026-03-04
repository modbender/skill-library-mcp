#!/bin/bash
# Cache management for clawddocs
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

show_status() {
  ensure_cache_dir
  echo "Cache directory: ${CACHE_DIR}"
  echo "================================"

  # llms.txt cache
  local llms_cache="${CACHE_DIR}/llms.txt"
  if [[ -f "$llms_cache" ]]; then
    local age=$(( $(date +%s) - $(stat -c %Y "$llms_cache") ))
    local size=$(stat -c %s "$llms_cache")
    local fresh="STALE"
    (( age < CACHE_TTL )) && fresh="FRESH"
    echo "llms.txt:    $(human_size $size)  $(human_age $age)  [${fresh}]"
  else
    echo "llms.txt:    (not cached)"
  fi

  # Docs cache
  if [[ -d "$CACHE_DOCS" ]]; then
    local doc_count=$(find "$CACHE_DOCS" -type f -name '*.md' 2>/dev/null | wc -l)
    local doc_size=$(du -sb "$CACHE_DOCS" 2>/dev/null | cut -f1)
    echo "docs/:       ${doc_count} files  $(human_size ${doc_size:-0})"
    if (( doc_count > 0 )); then
      local oldest_age=$(( $(date +%s) - $(find "$CACHE_DOCS" -type f -printf '%T@\n' 2>/dev/null | sort -n | head -1 | cut -d. -f1) ))
      local newest_age=$(( $(date +%s) - $(find "$CACHE_DOCS" -type f -printf '%T@\n' 2>/dev/null | sort -rn | head -1 | cut -d. -f1) ))
      echo "             oldest: $(human_age $oldest_age)  newest: $(human_age $newest_age)"
    fi
  else
    echo "docs/:       (empty)"
  fi

  # Index cache
  if [[ -d "$CACHE_INDEX" ]]; then
    local idx_file="${CACHE_INDEX}/fulltext.tsv"
    if [[ -f "$idx_file" ]]; then
      local idx_size=$(stat -c %s "$idx_file")
      local idx_age=$(( $(date +%s) - $(stat -c %Y "$idx_file") ))
      local idx_lines=$(wc -l < "$idx_file")
      echo "index/:      $(human_size $idx_size)  ${idx_lines} lines  $(human_age $idx_age)"
    else
      echo "index/:      (not built)"
    fi
  else
    echo "index/:      (empty)"
  fi

  # Snapshots
  if [[ -d "$CACHE_SNAPSHOTS" ]]; then
    local snap_count=$(find "$CACHE_SNAPSHOTS" -type f 2>/dev/null | wc -l)
    echo "snapshots/:  ${snap_count} snapshots"
  else
    echo "snapshots/:  (none)"
  fi

  echo
  local total_size=$(du -sb "$CACHE_DIR" 2>/dev/null | cut -f1)
  echo "Total cache: $(human_size ${total_size:-0})"
}

do_refresh() {
  ensure_cache_dir
  echo "Refreshing llms.txt cache..."
  local llms_cache="${CACHE_DIR}/llms.txt"
  rm -f "$llms_cache"
  if fetch_llms > /dev/null; then
    echo "Done. $(wc -l < "$llms_cache") lines cached."
  else
    echo "Refresh failed."
    exit 1
  fi
}

do_clear() {
  echo "Clearing all caches..."
  rm -rf "${CACHE_DIR:?}/"*
  ensure_cache_dir
  echo "Cache cleared."
}

case "${1:-status}" in
  status)  show_status ;;
  refresh) do_refresh ;;
  clear)   do_clear ;;
  *)
    echo "Usage: cache.sh {status|refresh|clear}"
    exit 1
    ;;
esac
