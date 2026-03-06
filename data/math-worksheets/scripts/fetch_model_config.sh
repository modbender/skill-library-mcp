#!/usr/bin/env bash
# fetch_model_config.sh — Fetch the latest math model rankings from the hosted source
#
# Outputs the path to the best available models.json (fetched or bundled fallback).
# Uses a 7-day cache so it doesn't fetch on every worksheet generation.
#
# Usage:
#   config_file=$(bash fetch_model_config.sh)
#   # config_file is a path to a valid models.json

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_DIR="${HOME}/.cache/math-worksheets-skill"
CACHE_FILE="${CACHE_DIR}/models.json"
CACHE_TTL_DAYS=7
HOSTED_URL="https://raw.githubusercontent.com/stellawuellner/math-worksheets-skill/main/references/model-rankings.json"
BUNDLED="${SKILL_DIR}/references/model-rankings.json"

mkdir -p "$CACHE_DIR"

# ── Check if cache is fresh ───────────────────────────────────────────────────
cache_is_fresh() {
  if [[ ! -f "$CACHE_FILE" ]]; then return 1; fi
  local age_days
  if command -v python3 &>/dev/null; then
    age_days=$(python3 -c "
import os, time
age = time.time() - os.path.getmtime('$CACHE_FILE')
print(int(age / 86400))
")
    [[ "$age_days" -lt "$CACHE_TTL_DAYS" ]]
  else
    # Fallback: use find
    [[ -n $(find "$CACHE_FILE" -mtime -"${CACHE_TTL_DAYS}" 2>/dev/null) ]]
  fi
}

# ── Try to fetch fresh config ─────────────────────────────────────────────────
fetch_remote() {
  if ! command -v curl &>/dev/null; then return 1; fi
  curl -sf --max-time 5 "$HOSTED_URL" -o "$CACHE_FILE.tmp" 2>/dev/null || return 1
  # Validate it's parseable JSON
  python3 -c "import json; json.load(open('$CACHE_FILE.tmp'))" 2>/dev/null || return 1
  mv "$CACHE_FILE.tmp" "$CACHE_FILE"
  return 0
}

# ── Resolve which config to use ───────────────────────────────────────────────
if cache_is_fresh; then
  echo "$CACHE_FILE"
elif fetch_remote; then
  echo "$CACHE_FILE"
elif [[ -f "$BUNDLED" ]]; then
  echo "$BUNDLED"   # bundled JSON fallback
else
  echo "NONE"       # caller will use hardcoded defaults in check_reasoning_model.sh
fi
