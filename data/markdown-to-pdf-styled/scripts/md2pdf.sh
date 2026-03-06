#!/usr/bin/env bash
set -euo pipefail

# md2pdf.sh <input.md> [output.pdf] [--style clean|modern|paper|/abs/path.css]

if [[ $# -lt 1 ]]; then
  echo "Usage: md2pdf.sh <input.md> [output.pdf] [--style clean|modern|paper|/abs/path.css]" >&2
  exit 1
fi

IN="$1"; shift
[[ -f "$IN" ]] || { echo "Input not found: $IN" >&2; exit 1; }

OUT=""
STYLE="clean"

if [[ $# -gt 0 && "$1" != "--style" ]]; then
  OUT="$1"; shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --style)
      STYLE="${2:-clean}"; shift 2 ;;
    *)
      echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -n "$OUT" ]] || OUT="${IN%.md}.pdf"

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
case "$STYLE" in
  clean|modern|paper) CSS="$BASE_DIR/assets/styles/${STYLE}.css" ;;
  *) CSS="$STYLE" ;;
esac

[[ -f "$CSS" ]] || { echo "Style file not found: $CSS" >&2; exit 1; }

pandoc "$IN" -o "$OUT" \
  --pdf-engine=wkhtmltopdf \
  --pdf-engine-opt=--enable-local-file-access \
  --css "$CSS"

echo "Generated: $OUT"
echo "Style: $CSS"
