#!/usr/bin/env bash
# common.sh — Shared utilities for feed-diet skill
# Part of the feed-diet Agent Skill (v0.1.1)

set -euo pipefail

# ─── Resolve SKILL_DIR ───────────────────────────────────────────────
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="${SKILL_DIR}/scripts"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/feed-diet"
mkdir -p "$CACHE_DIR"

# ─── Categories ──────────────────────────────────────────────────────
CATEGORIES=(
  "deep-technical"
  "news"
  "opinion"
  "drama"
  "entertainment"
  "tutorial"
  "meta"
)

CATEGORY_EMOJI_deep_technical="🔬"
CATEGORY_EMOJI_news="📰"
CATEGORY_EMOJI_opinion="💬"
CATEGORY_EMOJI_drama="🔥"
CATEGORY_EMOJI_entertainment="🎮"
CATEGORY_EMOJI_tutorial="📚"
CATEGORY_EMOJI_meta="🪞"

CATEGORY_DESC_deep_technical="In-depth technical content, papers, systems design"
CATEGORY_DESC_news="Current events, announcements, releases"
CATEGORY_DESC_opinion="Takes, editorials, essays"
CATEGORY_DESC_drama="Controversy, outrage, interpersonal conflict"
CATEGORY_DESC_entertainment="Fun, humor, lifestyle"
CATEGORY_DESC_tutorial="How-tos, guides, educational"
CATEGORY_DESC_meta="Navel-gazing about tech industry, AI hype, meta-discussion"

# ─── Helpers ─────────────────────────────────────────────────────────

get_category_emoji() {
  local cat="$1"
  local var="CATEGORY_EMOJI_${cat//-/_}"
  echo "${!var:-❓}"
}

get_category_desc() {
  local cat="$1"
  local var="CATEGORY_DESC_${cat//-/_}"
  echo "${!var:-Unknown}"
}

# Generate a bar of █ blocks proportional to percentage
# Usage: bar_chart 45.2 [max_width]
bar_chart() {
  local pct="${1:-0}"
  local max_width="${2:-20}"
  local blocks
  blocks=$(echo "$pct $max_width" | awk '{printf "%d", ($1 / 100) * $2 + 0.5}')
  local bar=""
  for ((i = 0; i < blocks; i++)); do
    bar+="█"
  done
  # Pad with light blocks for visual reference
  local remaining=$((max_width - blocks))
  for ((i = 0; i < remaining; i++)); do
    bar+="░"
  done
  echo "$bar"
}

# Human-readable timestamp from Unix epoch
human_date() {
  local ts="$1"
  if command -v date &>/dev/null; then
    date -d "@${ts}" '+%Y-%m-%d' 2>/dev/null || date -r "${ts}" '+%Y-%m-%d' 2>/dev/null || echo "unknown"
  else
    echo "unknown"
  fi
}

# Safe JSON string extraction (no jq dependency — uses python3)
json_get() {
  local json="$1"
  local key="$2"
  echo "$json" | KEY_ENV="$key" python3 -c "
import json, sys, os
try:
    data = json.load(sys.stdin)
    val = data.get(os.environ['KEY_ENV'], '')
    if isinstance(val, list):
        print(json.dumps(val))
    else:
        print(val if val is not None else '')
except:
    print('')
" 2>/dev/null
}

# URL-safe fetch with timeout and retries
safe_fetch() {
  local url="$1"
  local max_retries="${2:-2}"
  local timeout="${3:-10}"
  local attempt=0
  while [ $attempt -lt $max_retries ]; do
    local result
    if result=$(curl -sf --max-time "$timeout" "$url" 2>/dev/null); then
      echo "$result"
      return 0
    fi
    attempt=$((attempt + 1))
    [ $attempt -lt $max_retries ] && sleep 1
  done
  return 1
}

# Progress indicator
progress() {
  local current="$1"
  local total="$2"
  local label="${3:-items}"
  if [ -t 2 ]; then
    printf "\r  ⏳ Fetching %s... %d/%d" "$label" "$current" "$total" >&2
  fi
}

progress_done() {
  if [ -t 2 ]; then
    printf "\r  ✅ Done!                              \n" >&2
  fi
}

err() {
  echo "❌ Error: $*" >&2
}

info() {
  echo "ℹ️  $*" >&2
}

warn() {
  echo "⚠️  $*" >&2
}
