#!/usr/bin/env bash
set -euo pipefail

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "MISSING: $1" >&2
    exit 2
  fi
}

need python3
need ffmpeg

echo "OK: python3, ffmpeg"
