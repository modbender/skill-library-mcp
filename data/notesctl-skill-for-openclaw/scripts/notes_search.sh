#!/usr/bin/env bash
set -euo pipefail

# Search notes (fuzzy) optionally within a folder.
QUERY="${1:-}"
FOLDER="${2:-}"

if [[ -z "$QUERY" ]]; then
  echo "Usage: notes_search.sh <query> [folder]" >&2
  exit 1
fi

if [[ -n "$FOLDER" ]]; then
  memo notes -f "$FOLDER" -s "$QUERY"
else
  memo notes -s "$QUERY"
fi