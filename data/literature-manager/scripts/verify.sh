#!/usr/bin/env bash
# Verify a PDF+MD pair: valid PDF, title extractable, MD matches.
# Usage: verify.sh <paper.pdf> [paper.md]

set -euo pipefail

PDF="$1"
MD="${2:-${PDF%.pdf}.md}"
ERRORS=0
WARNINGS=0

# Check PDF exists and is valid
if [[ ! -f "$PDF" ]]; then
  echo "❌ PDF not found: $PDF"; exit 1
fi

if ! file -b "$PDF" | grep -q "PDF"; then
  echo "❌ Not a valid PDF (may be HTML): $PDF"; exit 1
fi

# Extract title
TITLE=$(pdftotext "$PDF" - 2>/dev/null | head -20 | grep -v '^$' | head -3)
echo "📄 $PDF"
echo "   Title: $(echo "$TITLE" | head -1)"

# Check MD exists and is non-empty
if [[ ! -f "$MD" ]]; then
  echo "❌ Markdown not found: $MD"
  ERRORS=$((ERRORS + 1))
elif [[ ! -s "$MD" ]]; then
  echo "❌ Markdown is empty: $MD"
  ERRORS=$((ERRORS + 1))
else
  MD_SIZE=$(wc -c < "$MD")
  echo "   Markdown: $MD ($MD_SIZE bytes)"
  
  # Size ratio check: MD should be at least 1% of PDF size
  PDF_SIZE=$(wc -c < "$PDF")
  if [[ $MD_SIZE -lt $((PDF_SIZE / 100)) ]]; then
    echo "⚠️  Markdown suspiciously small relative to PDF (scanned PDF?)"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

if [[ $ERRORS -eq 0 ]]; then
  echo "✅ PASS"
  exit 0
else
  echo "❌ FAIL ($ERRORS errors)"
  exit 1
fi
