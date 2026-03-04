#!/usr/bin/env bash
# ============================================================
# build-index.sh — Data index builder for SEA dashboard
#
# Scans data/proposals/ (and archive/) and writes
# dashboard/data-index.json so the dashboard knows which
# JSON files to fetch (python http.server can't list dirs).
#
# Usage:
#   bash dashboard/build-index.sh
#   # Run from the skill root OR from the dashboard/ dir
#
# Output: dashboard/data-index.json
# ============================================================

set -euo pipefail

# Resolve paths regardless of where script is run from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROPOSALS_DIR="$SKILL_DIR/data/proposals"
OUTPUT_FILE="$SCRIPT_DIR/data-index.json"

echo "🔍 Scanning proposals..."
echo "   Source: $PROPOSALS_DIR"
echo "   Output: $OUTPUT_FILE"

if [ ! -d "$PROPOSALS_DIR" ]; then
  echo "⚠️  Proposals directory not found: $PROPOSALS_DIR"
  echo '{"proposals":[],"generated_at":"'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'","error":"proposals directory not found"}' > "$OUTPUT_FILE"
  exit 0
fi

# Build JSON array of relative paths (relative to dashboard/)
# Include main dir + archive/
FILES_JSON="["
FIRST=true
TOTAL=0

# Scan main proposals dir
while IFS= read -r -d '' f; do
  rel="${f#$SKILL_DIR/}"   # relative to skill root → data/proposals/...
  if [ "$FIRST" = true ]; then
    FILES_JSON+="\"../$rel\""
    FIRST=false
  else
    FILES_JSON+=",\"../$rel\""
  fi
  TOTAL=$((TOTAL + 1))
done < <(find "$PROPOSALS_DIR" -maxdepth 1 -name "*.json" -print0 2>/dev/null | sort -z)

# Scan archive/
if [ -d "$PROPOSALS_DIR/archive" ]; then
  while IFS= read -r -d '' f; do
    rel="${f#$SKILL_DIR/}"
    FILES_JSON+=",\"../$rel\""
    TOTAL=$((TOTAL + 1))
  done < <(find "$PROPOSALS_DIR/archive" -name "*.json" -print0 2>/dev/null | sort -z)
fi

FILES_JSON+="]"

# Write the index JSON
cat > "$OUTPUT_FILE" <<EOF
{
  "generated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "total": $TOTAL,
  "proposals_dir": "../data/proposals",
  "files": $FILES_JSON
}
EOF

echo "✅ Index written: $TOTAL file(s) → $OUTPUT_FILE"
