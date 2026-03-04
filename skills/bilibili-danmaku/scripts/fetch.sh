#!/usr/bin/env bash
set -euo pipefail

# 用法：
# bash scripts/fetch.sh "https://www.bilibili.com/video/BVxxxx?p=1" [outdir]
# 或：bash scripts/fetch.sh --bvid BVxxxx --page 1 [outdir]

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="${2:-$BASE_DIR/output}"

if [[ "${1:-}" == "" ]]; then
  echo "Usage: bash scripts/fetch.sh <bilibili-url|--bvid BVxxxx> [outdir]"
  exit 1
fi

if [[ "$1" == "--bvid" ]]; then
  BVID="${2:-}"
  PAGE="${3:-1}"
  OUTDIR="${4:-$BASE_DIR/output}"
  python3 "$BASE_DIR/scripts/fetch_danmaku.py" --bvid "$BVID" --page "$PAGE" --outdir "$OUTDIR"
else
  URL="$1"
  python3 "$BASE_DIR/scripts/fetch_danmaku.py" --url "$URL" --outdir "$OUTDIR"
fi
