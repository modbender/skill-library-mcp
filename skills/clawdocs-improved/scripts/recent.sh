#!/bin/bash
# Show recently modified documentation pages
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

DAYS=${1:-7}
ensure_cache_dir

HEADERS_CACHE="${CACHE_DIR}/last-modified.tsv"

echo "Checking for docs modified in the last ${DAYS} days..."
echo "================================"
echo

threshold=$(date -d "-${DAYS} days" +%s 2>/dev/null || date -v-${DAYS}d +%s 2>/dev/null)

# Use cached headers if fresh (6h TTL)
if is_fresh "$HEADERS_CACHE" "$RECENT_CACHE_TTL"; then
  echo "(using cached Last-Modified headers)"
  echo
else
  echo "Fetching Last-Modified headers (this may take a moment)..."
  echo

  tmp="${HEADERS_CACHE}.tmp.$$"
  > "$tmp"

  while IFS=$'\t' read -r title url category path; do
    full_url="${DOCS_BASE}/${path}.md"
    last_mod=$(curl -sI --max-time 10 "$full_url" 2>/dev/null | grep -i 'last-modified' | sed 's/[Ll]ast-[Mm]odified: //' | tr -d '\r')
    if [[ -n "$last_mod" ]]; then
      epoch=$(date -d "$last_mod" +%s 2>/dev/null || date -jf '%a, %d %b %Y %H:%M:%S %Z' "$last_mod" +%s 2>/dev/null)
      [[ -n "$epoch" ]] && printf '%s\t%s\t%s\t%s\n' "$epoch" "$last_mod" "$path" "$title" >> "$tmp"
    fi
    sleep 0.1
  done < <(parse_llms_entries)

  mv "$tmp" "$HEADERS_CACHE"
fi

# Filter and display recent docs
match_count=0
sort -rn "$HEADERS_CACHE" | while IFS=$'\t' read -r epoch date path title; do
  if [[ -n "$threshold" ]] && (( epoch >= threshold )); then
    printf "  %-12s %-40s /%s\n" "$(date -d "@${epoch}" '+%Y-%m-%d' 2>/dev/null || date -r "$epoch" '+%Y-%m-%d' 2>/dev/null)" "$title" "$path"
    match_count=$(( match_count + 1 ))
  fi
done

if (( match_count == 0 )); then
  echo "(no docs modified in the last ${DAYS} days, or Last-Modified headers not available)"
fi

echo
echo "Note: Depends on server providing Last-Modified headers."
echo "Headers cached for 6 hours. Run 'cache.sh clear' to force refresh."
