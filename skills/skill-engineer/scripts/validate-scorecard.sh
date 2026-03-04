#!/usr/bin/env bash
# Validate that README.md Quality Scorecard math is correct
set -euo pipefail

README="$1"

if [[ ! -f "$README" ]]; then
    echo "ERROR: README file not found: $README"
    exit 1
fi

# Extract scorecard section (between "## Quality Scorecard" and next "##")
# Using portable approach (works on both GNU and BSD/macOS)
scorecard=$(sed -n '/## Quality Scorecard/,/^## [^Q]/p' "$README" | sed '$d')

if [[ -z "$scorecard" ]]; then
    echo "ERROR: No Quality Scorecard section found in README"
    exit 1
fi

# Extract individual scores using awk
scores=$(echo "$scorecard" | awk -F'|' '/\|.*\|.*\|.*\|/ && NR>2 && !/\*\*Total\*\*/ {
    gsub(/^[ \t]+|[ \t]+$/, "", $3)
    split($3, arr, "/")
    if (length(arr) == 2) {
        print arr[1]
    }
}')

# Extract claimed total
total_line=$(echo "$scorecard" | grep -E '\*\*Total\*\*')
claimed_total=$(echo "$total_line" | awk -F'|' '{gsub(/^[ \t]+|[ \t]+$/, "", $3); gsub(/\*\*/, "", $3); print $3}' | cut -d'/' -f1)

# Calculate actual sum
actual_sum=0
while IFS= read -r score; do
    actual_sum=$((actual_sum + score))
done <<< "$scores"

echo "Individual scores sum: $actual_sum"
echo "Claimed total: $claimed_total"

if [[ "$actual_sum" != "$claimed_total" ]]; then
    echo "ERROR: Scorecard math is incorrect! $actual_sum ≠ $claimed_total"
    exit 1
fi

echo "✓ Scorecard math is correct"
exit 0
