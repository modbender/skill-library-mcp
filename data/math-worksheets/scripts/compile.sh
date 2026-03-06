#!/usr/bin/env bash
# compile.sh — Compile a LaTeX file to PDF using tectonic
# Usage: compile.sh <input.tex> [output-dir]
#
# Requirements: tectonic (brew install tectonic)
# Tectonic auto-downloads any missing LaTeX packages on first use.

set -euo pipefail

TEX_FILE="${1:-}"
OUT_DIR="${2:-$(dirname "$TEX_FILE")}"

if [[ -z "$TEX_FILE" ]]; then
  echo "Usage: compile.sh <input.tex> [output-dir]" >&2
  exit 1
fi

if [[ ! -f "$TEX_FILE" ]]; then
  echo "Error: File not found: $TEX_FILE" >&2
  exit 1
fi

# Locate tectonic
TECTONIC=$(command -v tectonic 2>/dev/null || echo "/opt/homebrew/bin/tectonic")
if [[ ! -x "$TECTONIC" ]]; then
  echo "Error: tectonic not found. Install with: brew install tectonic" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "Compiling: $(basename "$TEX_FILE") → $OUT_DIR/"
"$TECTONIC" "$TEX_FILE" --outdir "$OUT_DIR" 2>&1 | grep -v "^note: downloading"

PDF="${OUT_DIR}/$(basename "${TEX_FILE%.tex}").pdf"
if [[ -f "$PDF" ]]; then
  echo "✅ PDF ready: $PDF"
  echo "$PDF"
else
  echo "❌ Compilation failed — check LaTeX errors above" >&2
  exit 1
fi
