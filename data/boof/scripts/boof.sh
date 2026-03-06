#!/usr/bin/env bash
# boof.sh — Convert a PDF/document to markdown and index it for RAG retrieval
# Usage: boof.sh <input_file> [--collection <name>] [--output-dir <dir>]
#
# Requirements:
#   - marker-pdf (Python venv at $MARKER_ENV or ~/.openclaw/tools/marker-env)
#   - qmd (installed via: bun install -g https://github.com/tobi/qmd)
#
# What it does:
#   1. Converts PDF → markdown using Marker (local, no API calls)
#   2. Indexes the markdown into QMD for RAG retrieval
#   3. Outputs the path to the converted markdown file

set -euo pipefail

# --- Config ---
MARKER_ENV="${MARKER_ENV:-$HOME/.openclaw/tools/marker-env}"
QMD_BIN="${QMD_BIN:-$(command -v qmd 2>/dev/null || echo "$HOME/.bun/bin/qmd")}"
DEFAULT_OUTPUT_DIR="${BOOF_OUTPUT_DIR:-$HOME/.openclaw/workspace/knowledge/boofed}"

# --- Parse args ---
INPUT_FILE=""
COLLECTION=""
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --collection) COLLECTION="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: boof.sh <input_file> [--collection <name>] [--output-dir <dir>]"
      echo ""
      echo "Convert a PDF to markdown and index it for RAG retrieval."
      echo ""
      echo "Options:"
      echo "  --collection <name>   QMD collection name (default: derived from filename)"
      echo "  --output-dir <dir>    Output directory (default: $DEFAULT_OUTPUT_DIR)"
      echo ""
      echo "Environment variables:"
      echo "  MARKER_ENV            Path to marker-pdf venv (default: ~/.openclaw/tools/marker-env)"
      echo "  QMD_BIN               Path to qmd binary (default: ~/.bun/bin/qmd)"
      echo "  BOOF_OUTPUT_DIR       Default output directory"
      exit 0
      ;;
    *) INPUT_FILE="$1"; shift ;;
  esac
done

if [[ -z "$INPUT_FILE" ]]; then
  echo "Error: No input file specified." >&2
  echo "Usage: boof.sh <input_file> [--collection <name>] [--output-dir <dir>]" >&2
  exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Error: File not found: $INPUT_FILE" >&2
  exit 1
fi

# --- Validate dependencies ---
MARKER_BIN="$MARKER_ENV/bin/marker_single"
if [[ ! -f "$MARKER_BIN" ]]; then
  echo "Error: marker-pdf not found at $MARKER_ENV" >&2
  echo "Install: python3.13 -m venv $MARKER_ENV && $MARKER_ENV/bin/pip install marker-pdf psutil" >&2
  exit 1
fi

if [[ ! -x "$QMD_BIN" ]] && [[ ! -f "$QMD_BIN" ]]; then
  echo "Error: qmd not found at $QMD_BIN" >&2
  echo "Install: bun install -g https://github.com/tobi/qmd" >&2
  exit 1
fi

# --- Derive names ---
BASENAME=$(basename "$INPUT_FILE" | sed 's/\.[^.]*$//')
SAFE_NAME=$(echo "$BASENAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
COLLECTION="${COLLECTION:-$SAFE_NAME}"

# --- Step 1: Convert to markdown ---
echo "🍑 Boofing: $INPUT_FILE"
echo "   → Converting to markdown..."
mkdir -p "$OUTPUT_DIR"

"$MARKER_BIN" "$INPUT_FILE" \
  --output_dir "$OUTPUT_DIR" \
  --output_format markdown \
  --disable_image_extraction \
  2>&1 | grep -v "^$" | sed 's/^/   /'

# Find the output markdown file
MD_FILE=$(find "$OUTPUT_DIR" -name "*.md" -newer "$INPUT_FILE" -o -name "${BASENAME}*.md" 2>/dev/null | head -1)
if [[ -z "$MD_FILE" ]]; then
  # Marker creates a subfolder with the basename
  MD_FILE=$(find "$OUTPUT_DIR/$BASENAME" -name "*.md" 2>/dev/null | head -1)
fi

if [[ -z "$MD_FILE" ]]; then
  echo "Error: Could not find converted markdown file in $OUTPUT_DIR" >&2
  exit 1
fi

echo "   ✅ Markdown: $MD_FILE"

# --- Step 2: Index with QMD ---
echo "   → Indexing for RAG retrieval..."

# Add as a collection if qmd is available
if "$QMD_BIN" collection add "$(dirname "$MD_FILE")" --name "$COLLECTION" --mask "*.md" 2>&1 | sed 's/^/   /'; then
  echo "   → Building embeddings..."
  "$QMD_BIN" embed 2>&1 | tail -3 | sed 's/^/   /'
  echo "   ✅ Indexed as collection: $COLLECTION"
else
  echo "   ⚠️  QMD indexing failed (non-fatal). Markdown file still available." >&2
fi

# --- Done ---
echo ""
echo "🍑 Boofed successfully!"
echo "   Markdown: $MD_FILE"
echo "   Collection: $COLLECTION"
echo ""
echo "Query with:"
echo "   qmd query 'your question here' -c $COLLECTION"
