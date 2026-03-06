#!/usr/bin/env bash
# format.sh — WeChat article formatting (baoyu renderer)
# Usage: bash format.sh <draft-dir> [draft-file] [theme]
# Themes: default (recommended), grace, simple
set -euo pipefail

DRAFT_DIR="${1:?Usage: format.sh <draft-dir> [draft-file] [theme]}"
DRAFT_FILE="${2:-draft.md}"
THEME="${3:-default}"
DRAFT_PATH="$DRAFT_DIR/$DRAFT_FILE"
FORMATTED="$DRAFT_DIR/formatted.html"
DRAFT_HTML="${DRAFT_PATH%.md}.html"

if [[ ! -f "$DRAFT_PATH" ]]; then
  echo "ERROR: Draft not found: $DRAFT_PATH" >&2; exit 1
fi

BUN="$HOME/.bun/bin/bun"
BAOYU="$(cd "$(dirname "$0")" && pwd)/renderer/main.ts"

if [[ ! -f "$BUN" ]]; then
  echo "ERROR: bun not installed" >&2; exit 1
fi
if [[ ! -f "$BAOYU" ]]; then
  echo "ERROR: baoyu skill missing at $BAOYU" >&2; exit 1
fi

echo "Rendering baoyu/$THEME ..."

# Run baoyu in the draft dir so relative image paths resolve correctly
# baoyu outputs <draft-file>.html next to the input file
"$BUN" "$BAOYU" "$DRAFT_PATH" --theme "$THEME" --keep-title 2>&1 | grep -v '^{'

if [[ ! -f "$DRAFT_HTML" ]]; then
  echo "ERROR: baoyu did not produce $DRAFT_HTML" >&2; exit 1
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
{
  printf '<meta charset="utf-8">\n'
  printf '<div style="background:#fff3cd;padding:8px;font-size:12px;color:#856404;border-bottom:1px solid #ffc107;text-align:center;">Preview: %s | baoyu/%s</div>\n' "$TIMESTAMP" "$THEME"
  cat "$DRAFT_HTML"
} > "$FORMATTED"

rm -f "$DRAFT_HTML"
echo "formatted.html: $(wc -c < "$FORMATTED") bytes"
echo "Done: $FORMATTED"
# NOTE: Preview server = systemd wechat-preview.service (port 8898). Do NOT restart from here.
