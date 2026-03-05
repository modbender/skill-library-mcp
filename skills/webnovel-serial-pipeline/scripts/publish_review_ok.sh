#!/usr/bin/env bash
set -euo pipefail

# Publish workflow that should ONLY be run after the user says: "검수 완료".
#
# Steps:
# 1) publish_episode.py (lint + asset check + copy draft -> Quartz)
# 2) sync_index.py (refresh index episode list between markers)
#
# Safe default: copy draft into Quartz (does NOT delete the draft).

usage() {
  cat >&2 <<'EOF'
Usage:
  publish_review_ok.sh \
    --series "야간조" \
    --episode 2 \
    --slug "불-꺼지면-가지-마세요" \
    --draft-file "/abs/path/to/draft.md" \
    [--quartz-root "/absolute/path/to/8.quartz"] \
    [--series-dir  "/absolute/path/to/8.quartz/Drama/야간조"] \
    [--index-file  "/absolute/path/to/8.quartz/Drama/야간조/index.md"]

Note:
  This script is meant to be triggered only after the chat confirmation:
  "검수 완료".
EOF
}

SERIES=""
EPISODE=""
SLUG=""
DRAFT_FILE=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"

# Config comes from environment variables only.
# (We intentionally do not load any local config file automatically for safety.)
QUARTZ_ROOT="${WEBNOVEL_QUARTZ_ROOT:-}"
SERIES_DIR=""
INDEX_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --series) SERIES="$2"; shift 2;;
    --episode) EPISODE="$2"; shift 2;;
    --slug) SLUG="$2"; shift 2;;
    --draft-file) DRAFT_FILE="$2"; shift 2;;
    --quartz-root) QUARTZ_ROOT="$2"; shift 2;;
    --series-dir) SERIES_DIR="$2"; shift 2;;
    --index-file) INDEX_FILE="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

if [[ -z "$SERIES" || -z "$EPISODE" || -z "$SLUG" || -z "$DRAFT_FILE" ]]; then
  echo "Missing required args" >&2
  usage
  exit 2
fi

if [[ -z "$QUARTZ_ROOT" ]]; then
  echo "Missing QUARTZ_ROOT. Set WEBNOVEL_QUARTZ_ROOT env var or pass --quartz-root." >&2
  exit 2
fi

if [[ -z "$SERIES_DIR" ]]; then
  SERIES_DIR="$QUARTZ_ROOT/Drama/$SERIES"
fi
if [[ -z "$INDEX_FILE" ]]; then
  INDEX_FILE="$SERIES_DIR/index.md"
fi

PUBLISH_PY="$SCRIPT_DIR/publish_episode.py"
SYNC_PY="$SCRIPT_DIR/sync_index.py"

echo "[1/2] publish_episode.py"
python3 "$PUBLISH_PY" \
  --draft-file "$DRAFT_FILE" \
  --quartz-root "$QUARTZ_ROOT" \
  --series-dir "$SERIES_DIR" \
  --series "$SERIES" \
  --episode "$EPISODE" \
  --slug "$SLUG" \
  | sed -n '1p'

echo "[2/2] sync_index.py"
python3 "$SYNC_PY" \
  --index-file "$INDEX_FILE" \
  --series-dir "$SERIES_DIR" \
  --series "$SERIES" \
  | sed -n '1p'

echo "DONE"
