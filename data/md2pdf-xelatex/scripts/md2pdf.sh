#!/usr/bin/env bash
# md2pdf.sh — Convert Markdown to PDF with LaTeX math + CJK support
# Usage: md2pdf.sh <input.md> [output.pdf] [--no-toc] [--font-size=11pt] [--margin=20mm]
set -euo pipefail

INPUT="${1:?Usage: md2pdf.sh <input.md> [output.pdf] [options...]}"
OUTPUT="${2:-${INPUT%.md}.pdf}"
shift 2 2>/dev/null || shift 1 2>/dev/null || true

# Defaults
TOC="--toc"
TOC_TITLE="目录"
FONT_SIZE="10pt"
MARGIN="20mm"
HIGHLIGHT="tango"

# Parse optional flags
for arg in "$@"; do
  case "$arg" in
    --no-toc)       TOC="" ;;
    --font-size=*)  FONT_SIZE="${arg#*=}" ;;
    --margin=*)     MARGIN="${arg#*=}" ;;
    --toc-title=*)  TOC_TITLE="${arg#*=}" ;;
    --highlight=*)  HIGHLIGHT="${arg#*=}" ;;
  esac
done

# --- Check prerequisites ---
for cmd in pandoc xelatex; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: '$cmd' not found. Install: sudo apt install pandoc texlive-xetex texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra texlive-lang-chinese" >&2
    exit 1
  fi
done

# --- Detect CJK font ---
detect_cjk_font() {
  local candidates=(
    "Noto Sans CJK SC"
    "WenQuanYi Micro Hei"
    "Droid Sans Fallback"
    "AR PL UMing CN"
    "AR PL SungtiL GB"
  )
  for font in "${candidates[@]}"; do
    if fc-list -f '%{family}\n' | grep -qi "^${font}$\|, ${font}$\|^${font},"; then
      echo "$font"
      return
    fi
    # Fallback: search in full fc-list output
    if fc-list | grep -i "$font" | grep -qi "style="; then
      echo "$font"
      return
    fi
  done
  echo ""
}

CJK_FONT=$(detect_cjk_font)

# --- Detect if content has CJK ---
has_cjk() {
  grep -Pq '[\x{4e00}-\x{9fff}\x{3000}-\x{303f}\x{ff00}-\x{ffef}]' "$1" 2>/dev/null
}

# --- Create temp working dir ---
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

# --- Sanitize input (emoji + smart quotes) ---
sed \
  's/✅/[Y]/g; s/❌/[N]/g; s/⭐/*/g; s/🔗//g; s/📄//g; s/📊//g; s/🎉//g; s/💡//g; s/⚠️/[!]/g; s/🚀//g' \
  "$INPUT" \
  | sed "s/\xe2\x80\x9c/\"/g; s/\xe2\x80\x9d/\"/g; s/\xe2\x80\x98/'/g; s/\xe2\x80\x99/'/g" \
  | sed 's/—/--/g; s/→/->/g' \
  > "$TMPDIR/input.md"

# --- Build header.tex for CJK ---
HEADER_FILE="$TMPDIR/header.tex"
if has_cjk "$TMPDIR/input.md" && [ -n "$CJK_FONT" ]; then
  cat > "$HEADER_FILE" << TEXEOF
\\usepackage{xeCJK}
\\setCJKmainfont{${CJK_FONT}}
\\setCJKsansfont{${CJK_FONT}}
\\setCJKmonofont{${CJK_FONT}}
TEXEOF
  echo "CJK detected. Using font: $CJK_FONT" >&2
else
  touch "$HEADER_FILE"
  if has_cjk "$TMPDIR/input.md"; then
    echo "WARNING: CJK content detected but no CJK font found. Install fonts-noto-cjk." >&2
  fi
fi

# --- Detect main font ---
detect_main_font() {
  local candidates=("DejaVu Sans" "Liberation Sans" "FreeSans" "Noto Sans")
  for font in "${candidates[@]}"; do
    if fc-list | grep -qi "$font"; then
      echo "$font"
      return
    fi
  done
  echo "DejaVu Sans"  # fallback
}

detect_mono_font() {
  local candidates=("DejaVu Sans Mono" "Liberation Mono" "FreeMono" "Noto Sans Mono")
  for font in "${candidates[@]}"; do
    if fc-list | grep -qi "$font"; then
      echo "$font"
      return
    fi
  done
  echo "DejaVu Sans Mono"
}

MAIN_FONT=$(detect_main_font)
MONO_FONT=$(detect_mono_font)

# --- Build pandoc command ---
PANDOC_ARGS=(
  "$TMPDIR/input.md"
  -o "$OUTPUT"
  --pdf-engine=xelatex
  -f markdown-smart
  -H "$HEADER_FILE"
  -V "mainfont=$MAIN_FONT"
  -V "sansfont=$MAIN_FONT"
  -V "monofont=$MONO_FONT"
  -V "geometry:margin=$MARGIN"
  -V "fontsize=$FONT_SIZE"
  -V colorlinks=true
  -V linkcolor=blue
  -V urlcolor=blue
  --highlight-style="$HIGHLIGHT"
)

if [ -n "$TOC" ]; then
  PANDOC_ARGS+=($TOC -V "toc-title=$TOC_TITLE")
fi

# --- Run pandoc ---
echo "Converting: $INPUT -> $OUTPUT" >&2
echo "  Engine: xelatex | Font: $MAIN_FONT | Mono: $MONO_FONT | Size: $FONT_SIZE | Margin: $MARGIN" >&2

pandoc "${PANDOC_ARGS[@]}" 2>&1 | while IFS= read -r line; do
  # Filter out warnings, only show errors
  if echo "$line" | grep -q "ERROR\|error\|Error"; then
    echo "$line" >&2
  fi
done

if [ -f "$OUTPUT" ]; then
  SIZE=$(du -h "$OUTPUT" | cut -f1)
  PAGES=$(pdfinfo "$OUTPUT" 2>/dev/null | grep Pages | awk '{print $2}' || echo "?")
  echo "Done! $OUTPUT ($SIZE, ${PAGES} pages)" >&2
else
  echo "ERROR: PDF generation failed." >&2
  exit 1
fi
