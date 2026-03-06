#!/usr/bin/env bash
set -euo pipefail

KEEP_MINUTES="${1:-30}"
WORKSPACE_ROOT="${OPENCLAW_WORKSPACE:-$(pwd)}"
DIR="${REEL_DOWNLOAD_DIR:-$WORKSPACE_ROOT/downloads}"

if [[ ! -d "$DIR" ]]; then
  exit 0
fi

# Remove only reel downloads created by this workflow
find "$DIR" -maxdepth 1 -type f \
  \( -name 'reel-*.mp4' -o -name 'reel-*.mov' -o -name 'reel-*.mkv' -o -name 'reel-*.webm' \) \
  -mmin +"$KEEP_MINUTES" -print -delete
