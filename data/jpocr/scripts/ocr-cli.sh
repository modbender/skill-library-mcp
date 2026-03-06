#!/usr/bin/env bash
# jpocr — Japanese OCR skill executor
# Called by AI agents via SKILL.md. Also usable standalone.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV="$REPO_ROOT/.venv/bin/python"
OCR="$REPO_ROOT/src/ocr.py"
OUTDIR="${JPOCR_OUTPUT:-$REPO_ROOT/output}"

mkdir -p "$OUTDIR"

INPUT="$1"
shift || true

FORMAT="text"
VIZ=""
for arg in "$@"; do
  case "$arg" in
    --json) FORMAT="json" ;;
    --viz)  VIZ="True" ;;
  esac
done

if [ -d "$INPUT" ]; then
  SOURCE_ARG="--sourcedir $INPUT"
else
  SOURCE_ARG="--sourceimg $INPUT"
fi

VIZ_FLAG=""
[ -n "$VIZ" ] && VIZ_FLAG="--viz True"

"$VENV" "$OCR" $SOURCE_ARG --output "$OUTDIR" $VIZ_FLAG >/dev/null 2>&1

BASENAME=$(basename "$INPUT" | sed 's/\.[^.]*$//')

if [ "$FORMAT" = "json" ]; then
  cat "$OUTDIR/$BASENAME.json"
else
  cat "$OUTDIR/$BASENAME.txt"
fi
