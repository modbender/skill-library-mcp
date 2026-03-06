#!/usr/bin/env bash
# Convert PDF to markdown.
# Usage: convert.sh <input.pdf> [output.md]
# Tries pdftotext first, falls back to uvx markitdown.

set -euo pipefail

INPUT="$1"
OUTPUT="${2:-${INPUT%.pdf}.md}"
mkdir -p "$(dirname "$OUTPUT")"

if [[ ! -f "$INPUT" ]]; then
  echo "❌ File not found: $INPUT"
  exit 1
fi

if ! file -b "$INPUT" | grep -q "PDF"; then
  echo "❌ Not a valid PDF: $INPUT"
  exit 1
fi

# Try pdftotext first (most reliable)
if command -v pdftotext &>/dev/null; then
  pdftotext "$INPUT" "$OUTPUT" 2>/dev/null
  if [[ -s "$OUTPUT" ]]; then
    echo "✅ Converted with pdftotext: $OUTPUT ($(wc -c < "$OUTPUT") bytes)"
    exit 0
  fi
fi

# Fallback: uvx markitdown[pdf]
# Note: must use "markitdown[pdf]" extra — plain "uvx markitdown" does NOT handle PDFs.
if command -v uvx &>/dev/null; then
  uvx markitdown[pdf] "$INPUT" > "$OUTPUT" 2>/dev/null
  if [[ -s "$OUTPUT" ]]; then
    echo "✅ Converted with markitdown[pdf]: $OUTPUT ($(wc -c < "$OUTPUT") bytes)"
    exit 0
  fi
fi

echo "❌ Conversion failed for: $INPUT"
exit 1
