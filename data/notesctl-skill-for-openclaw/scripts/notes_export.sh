#!/usr/bin/env bash
set -euo pipefail

# Export a note via memo (interactive selection).
# Usage: notes_export.sh [query] [folder] [outdir]
QUERY="${1:-}"
FOLDER="${2:-Notes}"
OUTDIR="${3:-.}"

mkdir -p "$OUTDIR"

if [[ -n "$QUERY" ]]; then
  # Narrow down list first; export remains interactive in memo.
  memo notes -f "$FOLDER" -s "$QUERY"
fi

# memo will prompt for which note to export
(cd "$OUTDIR" && memo notes -f "$FOLDER" -ex)