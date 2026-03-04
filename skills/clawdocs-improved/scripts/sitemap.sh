#!/bin/bash
# Display documentation sitemap grouped by category
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${SCRIPT_DIR}/_common.sh"

ensure_cache_dir

echo "OpenClaw Documentation Sitemap"
echo "Source: ${LLMS_URL}"
echo "================================"
echo

# Collect entries into a temp file for multi-pass processing
tmpfile=$(mktemp)
parse_llms_entries > "$tmpfile"

# Get ordered list of categories
categories=()
while IFS=$'\t' read -r title url category path; do
  found=0
  for c in "${categories[@]}"; do
    [[ "$c" == "$category" ]] && found=1 && break
  done
  (( found == 0 )) && categories+=("$category")
done < "$tmpfile"

total=0
for cat in "${categories[@]}"; do
  # Count pages in this category
  count=$(awk -F'\t' -v c="$cat" '$3 == c' "$tmpfile" | wc -l)
  total=$(( total + count ))

  printf "%-20s (%d pages)\n" "/${cat}/" "$count"

  # List pages in category
  while IFS=$'\t' read -r title url category path; do
    printf "  %-40s %s\n" "$title" "$path"
  done < <(awk -F'\t' -v c="$cat" '$3 == c' "$tmpfile")

  echo
done

rm -f "$tmpfile"

echo "================================"
echo "Total: ${total} pages across ${#categories[@]} categories"
