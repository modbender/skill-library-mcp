#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <file> <description> [public|secret] [lang]" >&2
  exit 1
fi

FILE="$1"
DESC="$2"
VIS="${3:-secret}"
LANG="${4:-}"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install GitHub CLI first." >&2
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "File not found: $FILE" >&2
  exit 1
fi

EXT_FROM_LANG=""
LANG_LC="$(printf '%s' "$LANG" | tr '[:upper:]' '[:lower:]')"
case "$LANG_LC" in
  py|python) EXT_FROM_LANG=".py" ;;
  js|javascript) EXT_FROM_LANG=".js" ;;
  ts|typescript) EXT_FROM_LANG=".ts" ;;
  jsx) EXT_FROM_LANG=".jsx" ;;
  tsx) EXT_FROM_LANG=".tsx" ;;
  sh|bash|zsh) EXT_FROM_LANG=".sh" ;;
  json) EXT_FROM_LANG=".json" ;;
  yaml|yml) EXT_FROM_LANG=".yml" ;;
  md|markdown) EXT_FROM_LANG=".md" ;;
  html) EXT_FROM_LANG=".html" ;;
  css) EXT_FROM_LANG=".css" ;;
  go) EXT_FROM_LANG=".go" ;;
  java) EXT_FROM_LANG=".java" ;;
  rs|rust) EXT_FROM_LANG=".rs" ;;
  c) EXT_FROM_LANG=".c" ;;
  cpp|cxx|cc) EXT_FROM_LANG=".cpp" ;;
  *) EXT_FROM_LANG="" ;;
esac

UPLOAD_FILE="$FILE"
TMP_FILE=""

if [[ -n "$EXT_FROM_LANG" && "$FILE" != *.* ]]; then
  TMP_FILE="$(mktemp "/tmp/code-share-XXXXXX$EXT_FROM_LANG")"
  cp "$FILE" "$TMP_FILE"
  UPLOAD_FILE="$TMP_FILE"
fi

if [[ "$VIS" == "public" ]]; then
  gh gist create "$UPLOAD_FILE" --public --desc "$DESC"
else
  gh gist create "$UPLOAD_FILE" --desc "$DESC"
fi

if [[ -n "$TMP_FILE" && -f "$TMP_FILE" ]]; then
  rm -f "$TMP_FILE"
fi
