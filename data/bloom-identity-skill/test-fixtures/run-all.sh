#!/bin/bash
# Run all 5 test conversations and show personality + categories for each
# Usage: bash test-fixtures/run-all.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  Bloom Taste Finder - 5 Persona Test"
echo "=========================================="
echo ""

FIXTURES=(
  "01-visionary-crypto:test-visionary"
  "02-explorer-ai-wellness:test-explorer"
  "03-optimizer-productivity:test-optimizer"
  "04-innovator-dev-ai:test-innovator"
  "05-cultivator-education:test-cultivator"
)

for entry in "${FIXTURES[@]}"; do
  FILE="${entry%%:*}"
  USER_ID="${entry##*:}"

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Testing: $FILE (user: $USER_ID)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  cat "$SCRIPT_DIR/$FILE.txt" | npx tsx "$PROJECT_DIR/scripts/run-from-context.ts" \
    --user-id "$USER_ID" \
    --skip-share \
    2>&1

  echo ""
  echo ""
done

echo "=========================================="
echo "  All 5 tests complete!"
echo "=========================================="
