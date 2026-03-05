#!/bin/bash
# Full-text index: fetch all docs, build searchable index, query it
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

RATE_LIMIT_MS=200  # ms between requests during fetch

do_fetch() {
  ensure_cache_dir
  echo "Fetching all doc pages from ${DOCS_BASE}..."

  local count=0
  local total=0
  local skipped=0
  local failed=0

  # Collect all paths
  local paths=()
  while IFS=$'\t' read -r title url category path; do
    paths+=("${path}.md")
    total=$(( total + 1 ))
  done < <(parse_llms_entries)

  echo "Found ${total} pages to fetch"
  echo

  for rel_path in "${paths[@]}"; do
    local cache_file="${CACHE_DOCS}/${rel_path}"
    local cache_subdir="$(dirname "$cache_file")"
    mkdir -p "$cache_subdir"

    # Skip if recently cached
    if is_fresh "$cache_file" "$INDEX_CACHE_TTL"; then
      skipped=$(( skipped + 1 ))
      continue
    fi

    local url="${DOCS_BASE}/${rel_path}"
    local tmp="${cache_file}.tmp.$$"

    count=$(( count + 1 ))
    printf "\r[%d/%d] Fetching %-50s" "$count" "$(( total - skipped ))" "$rel_path"

    if curl -sfL --max-time 30 -o "$tmp" "$url" 2>/dev/null; then
      mv "$tmp" "$cache_file"
    else
      rm -f "$tmp"
      failed=$(( failed + 1 ))
    fi

    # Rate limit
    sleep "$(echo "scale=3; ${RATE_LIMIT_MS}/1000" | bc)"
  done

  echo
  echo
  echo "Fetch complete: $count downloaded, $skipped cached (fresh), $failed failed"
}

do_build() {
  ensure_cache_dir
  local index_file="${CACHE_INDEX}/fulltext.tsv"
  echo "Building full-text index..."

  local tmp="${index_file}.tmp.$$"
  local page_count=0

  find "$CACHE_DOCS" -type f -name '*.md' | sort | while read -r filepath; do
    local rel_path="${filepath#${CACHE_DOCS}/}"
    rel_path="${rel_path%.md}"
    # Output: path<TAB>line_content (one line per line of content)
    while IFS= read -r line; do
      [[ -z "$line" ]] && continue
      printf '%s\t%s\n' "$rel_path" "$line"
    done < "$filepath"
    page_count=$(( page_count + 1 ))
  done > "$tmp"

  mv "$tmp" "$index_file"
  local lines=$(wc -l < "$index_file")
  local size=$(stat -c %s "$index_file")
  echo "Index built: ${lines} lines from $(find "$CACHE_DOCS" -type f -name '*.md' | wc -l) pages ($(human_size $size))"
}

do_search() {
  local query="$*"
  if [[ -z "$query" ]]; then
    echo "Usage: build-index.sh search <query>"
    exit 1
  fi

  local index_file="${CACHE_INDEX}/fulltext.tsv"
  if [[ ! -f "$index_file" ]]; then
    echo "[error] Full-text index not built. Run: build-index.sh fetch && build-index.sh build"
    exit 1
  fi

  echo "Full-text search: ${query}"
  echo "================================"
  echo

  # Rank by hit count per page
  echo "-- Pages ranked by relevance --"
  grep -i "$query" "$index_file" | cut -f1 | sort | uniq -c | sort -rn | head -20 | while read -r count path; do
    printf "  %3d hits  /%s\n" "$count" "$path"
  done

  echo
  echo "-- Context from top results --"
  local top_path=$(grep -i "$query" "$index_file" | cut -f1 | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
  if [[ -n "$top_path" ]]; then
    echo "  [/${top_path}]"
    grep -i "$query" "$index_file" | awk -F'\t' -v p="$top_path" '$1 == p {print "    " $2}' | head -10
  fi
}

case "$1" in
  fetch)  do_fetch ;;
  build)  do_build ;;
  search)
    shift
    do_search "$@"
    ;;
  *)
    echo "Usage: build-index.sh {fetch|build|search <query>}"
    echo
    echo "  fetch   Download all doc pages (rate-limited, 24h cache)"
    echo "  build   Build full-text search index from cached pages"
    echo "  search  Search the index by keyword"
    exit 1
    ;;
esac
