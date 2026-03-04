#!/usr/bin/env bash
set -euo pipefail

DIR="${1:-}"
if [[ "$DIR" == "--dir" ]]; then
  DIR="${2:-}"
fi
[[ -n "$DIR" ]] || { echo "Usage: list-souls.sh --dir <path>"; exit 1; }
[[ -d "$DIR" ]] || { echo "Not found: $DIR"; exit 1; }

find "$DIR" -maxdepth 2 \( -name manifest.json -o -name '*.tar.gz' \) | sort
