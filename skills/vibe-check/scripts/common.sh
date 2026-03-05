#!/usr/bin/env bash
# common.sh — Shared utilities for vibe-check skill
# Part of the vibe-check Agent Skill (v0.1.0)

set -euo pipefail

# ─── Resolve SKILL_DIR ───────────────────────────────────────────────
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="${SKILL_DIR}/scripts"

# ─── Constants ────────────────────────────────────────────────────────
VERSION="0.1.0"
MAX_FILE_SIZE=50000        # Skip files larger than 50KB (probably not hand-written)
MAX_FILES=50               # Max files to analyze in one run
BATCH_SIZE="${VIBE_CHECK_BATCH_SIZE:-3}"  # Files per LLM call (smaller = better analysis)
SUPPORTED_EXTENSIONS="py|ts|tsx|js|jsx|mjs|cjs"

# ─── Sin Categories with Weights ─────────────────────────────────────
# Format: "slug|label|weight|emoji"
SIN_CATEGORIES=(
  "error_handling|Error Handling|20|🛡️"
  "duplication|Copy-Paste Duplication|15|📋"
  "dead_code|Dead Code|10|💀"
  "input_validation|Input Validation|15|🔍"
  "magic_values|Magic Values|10|🔮"
  "test_coverage|Test Coverage|10|🧪"
  "naming_quality|Naming Quality|10|📛"
  "security|Security Smells|10|🔒"
)

# ─── Severity Levels ─────────────────────────────────────────────────
SEVERITY_CRITICAL="critical"
SEVERITY_WARNING="warning"
SEVERITY_INFO="info"

# ─── Color / Grade helpers ───────────────────────────────────────────
letter_grade() {
  local score="$1"
  if [ "$score" -ge 90 ]; then echo "A"
  elif [ "$score" -ge 80 ]; then echo "B"
  elif [ "$score" -ge 70 ]; then echo "C"
  elif [ "$score" -ge 60 ]; then echo "D"
  else echo "F"
  fi
}

grade_color() {
  local grade="$1"
  case "$grade" in
    A) echo "brightgreen" ;;
    B) echo "green" ;;
    C) echo "yellow" ;;
    D) echo "orange" ;;
    F) echo "red" ;;
    *) echo "lightgrey" ;;
  esac
}

verdict_text() {
  local score="$1"
  if [ "$score" -ge 90 ]; then echo "Pristine code. Minimal vibe coding detected. Ship it! 🚀"
  elif [ "$score" -ge 80 ]; then echo "Clean code with minor issues. A few human touches needed."
  elif [ "$score" -ge 70 ]; then echo "Decent code but some lazy patterns crept in. Worth a review pass."
  elif [ "$score" -ge 60 ]; then echo "Noticeable vibe coding. This code needs human attention."
  else echo "Heavy vibe coding detected. This codebase needs serious human review. 🚨"
  fi
}

# ─── Bar chart helper ────────────────────────────────────────────────
bar_chart() {
  local score="${1:-0}"
  local max_width="${2:-10}"
  local blocks
  blocks=$(SCORE_ENV="$score" MAX_WIDTH_ENV="$max_width" python3 -c "import os; print(int(round(int(os.environ['SCORE_ENV']) / 100.0 * int(os.environ['MAX_WIDTH_ENV']))))" 2>/dev/null)
  local bar=""
  for ((i = 0; i < blocks; i++)); do bar+="█"; done
  local remaining=$((max_width - blocks))
  for ((i = 0; i < remaining; i++)); do bar+="░"; done
  echo "$bar"
}

# ─── File discovery ──────────────────────────────────────────────────
# Find supported source files in a directory
discover_files() {
  local target="$1"
  local max_files="${2:-$MAX_FILES}"

  if [ -f "$target" ]; then
    # Single file — just validate extension
    if echo "$target" | grep -qE "\.(${SUPPORTED_EXTENSIONS})$"; then
      echo "$target"
    else
      err "Unsupported file type. Supported: .py, .ts, .tsx, .js, .jsx, .mjs, .cjs"
      return 1
    fi
    return 0
  fi

  if [ -d "$target" ]; then
    find "$target" -type f \( \
      -name "*.py" -o -name "*.ts" -o -name "*.tsx" \
      -o -name "*.js" -o -name "*.jsx" -o -name "*.mjs" -o -name "*.cjs" \
    \) \
      ! -path "*/node_modules/*" \
      ! -path "*/.git/*" \
      ! -path "*/dist/*" \
      ! -path "*/build/*" \
      ! -path "*/__pycache__/*" \
      ! -path "*/.venv/*" \
      ! -path "*/venv/*" \
      ! -path "*/.tox/*" \
      ! -path "*/coverage/*" \
      ! -path "*/.next/*" \
      ! -size +${MAX_FILE_SIZE}c \
      2>/dev/null | sort | head -n "$max_files"
    return 0
  fi

  err "Target not found: $target"
  return 1
}

# ─── Detect language from filename ────────────────────────────────────
detect_language() {
  local file="$1"
  case "$file" in
    *.py)                    echo "python" ;;
    *.ts|*.tsx)              echo "typescript" ;;
    *.js|*.jsx|*.mjs|*.cjs) echo "javascript" ;;
    *)                       echo "unknown" ;;
  esac
}

# ─── Safe JSON extraction (no jq — uses python3) ─────────────────────
json_get() {
  local json="$1"
  local key="$2"
  echo "$json" | KEY_ENV="$key" python3 -c "
import json, sys, os
try:
    data = json.load(sys.stdin)
    val = data.get(os.environ['KEY_ENV'], '')
    if isinstance(val, (list, dict)):
        print(json.dumps(val))
    else:
        print(val if val is not None else '')
except:
    print('')
" 2>/dev/null
}

# ─── Logging ──────────────────────────────────────────────────────────
err() {
  echo "❌ Error: $*" >&2
}

info() {
  echo "ℹ️  $*" >&2
}

warn() {
  echo "⚠️  $*" >&2
}

progress() {
  local current="$1"
  local total="$2"
  local label="${3:-files}"
  if [ -t 2 ]; then
    printf "\r  ⏳ Analyzing %s... %d/%d" "$label" "$current" "$total" >&2
  fi
}

progress_done() {
  if [ -t 2 ]; then
    printf "\r  ✅ Analysis complete!                              \n" >&2
  fi
}

# ─── URL-encode for badge ────────────────────────────────────────────
url_encode_score() {
  local score="$1"
  # shields.io expects %2F for /
  echo "${score}%2F100"
}
