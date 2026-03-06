#!/bin/bash
# Search docs by keyword in titles and paths
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

if [[ -z "$1" ]]; then
  echo "Usage: search.sh <keyword> [keyword2 ...]"
  echo "Searches doc titles, paths, and full-text index (if built)"
  exit 1
fi

query="$*"
ensure_cache_dir

echo "Searching for: ${query}"
echo "================================"

# Search titles and paths from llms.txt
echo
echo "-- Title/Path matches --"
match_count=0
while IFS=$'\t' read -r title url category path; do
  combined="${title} ${path}"
  if echo "$combined" | grep -qi "$query"; then
    printf "  %-40s /%s\n" "$title" "$path"
    match_count=$(( match_count + 1 ))
  fi
done < <(parse_llms_entries)

if (( match_count == 0 )); then
  echo "  (no matches in titles/paths)"
fi

# Search full-text index if available
index_file="${CACHE_INDEX}/fulltext.tsv"
if [[ -f "$index_file" ]]; then
  echo
  echo "-- Full-text index matches --"
  ft_results=$(grep -i "$query" "$index_file" | cut -f1 | sort | uniq -c | sort -rn | head -20)
  if [[ -n "$ft_results" ]]; then
    echo "$ft_results" | while read -r count path; do
      printf "  %3d hits  /%s\n" "$count" "$path"
    done
  else
    echo "  (no full-text matches)"
  fi
else
  echo
  echo "(full-text index not built -- run build-index.sh fetch && build-index.sh build)"
fi

echo
echo "Total title/path matches: ${match_count}"
