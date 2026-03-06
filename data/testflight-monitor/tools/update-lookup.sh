#!/bin/bash
# Update TestFlight lookup table from awesome-testflight-link repo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_FILE="$SKILL_ROOT/config/testflight-codes.json"
REPO_URL="https://raw.githubusercontent.com/pluwen/awesome-testflight-link/main/README.md"

echo "Fetching awesome-testflight-link README..."
README=$(curl -sSL "$REPO_URL")

echo "Parsing TestFlight codes..."

# Extract all TestFlight links and app names from markdown tables
# Format: | App Name | [link](https://testflight.apple.com/join/CODE) | Status | Date |
echo "$README" | grep -oE '\| [^|]+ \| \[https://testflight\.apple\.com/join/[A-Za-z0-9]+\]' | \
  sed -E 's/\| ([^|]+) \| \[https:\/\/testflight\.apple\.com\/join\/([A-Za-z0-9]+)\]/\2|\1/' | \
  awk -F'|' '
    BEGIN { print "{" }
    NR > 1 { print "," }
    {
      # Trim whitespace from app name
      gsub(/^[ \t]+|[ \t]+$/, "", $2)
      # Escape quotes in app name
      gsub(/"/, "\\\"", $2)
      printf "  \"%s\": \"%s\"", $1, $2
    }
    END { print "\n}" }
  ' > "$OUTPUT_FILE"

COUNT=$(grep -c '"' "$OUTPUT_FILE" || true)
echo "✓ Extracted $COUNT TestFlight codes to $OUTPUT_FILE"
