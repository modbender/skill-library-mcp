#!/usr/bin/env bash
# common.sh — Shared utilities for meeting-autopilot
# Source this file, don't execute it directly.

set -euo pipefail

# ── Branding ──────────────────────────────────────────────
BRAND="Meeting Autopilot"
BRAND_FOOTER="Powered by Anvil AI ✈️"
VERSION="0.1.1"

# ── Colors (when stdout is a terminal) ────────────────────
if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  BLUE='\033[0;34m'
  CYAN='\033[0;36m'
  BOLD='\033[1m'
  DIM='\033[2m'
  RESET='\033[0m'
else
  RED='' GREEN='' YELLOW='' BLUE='' CYAN='' BOLD='' DIM='' RESET=''
fi

# ── Logging ───────────────────────────────────────────────
log_info()  { echo -e "${BLUE}ℹ${RESET} $*" >&2; }
log_ok()    { echo -e "${GREEN}✔${RESET} $*" >&2; }
log_warn()  { echo -e "${YELLOW}⚠${RESET} $*" >&2; }
log_error() { echo -e "${RED}✖${RESET} $*" >&2; }
log_step()  { echo -e "${CYAN}▸${RESET} ${BOLD}$*${RESET}" >&2; }

# ── Error exit with branded message ───────────────────────
die() {
  local msg="$1"
  local hint="${2:-}"
  echo "" >&2
  echo -e "${RED}✖ ${BRAND} error:${RESET} $msg" >&2
  if [ -n "$hint" ]; then
    echo -e "  ${DIM}Hint:${RESET} $hint" >&2
  fi
  echo -e "  ${DIM}$BRAND_FOOTER${RESET}" >&2
  echo "" >&2
  exit 1
}

# ── Dependency checks ────────────────────────────────────
require_cmd() {
  local cmd="$1"
  local install_hint="${2:-}"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    die "$cmd is required but not found." "$install_hint"
  fi
}

require_jq() {
  require_cmd jq "Install: apt install jq / brew install jq"
}

# ── Safe temporary directory ──────────────────────────────
make_workdir() {
  local workdir
  workdir="$(mktemp -d "${TMPDIR:-/tmp}/meeting-autopilot.XXXXXX")"
  echo "$workdir"
}

# ── History directory ─────────────────────────────────────
HISTORY_DIR="${HOME}/.meeting-autopilot/history"

ensure_history_dir() {
  mkdir -p "$HISTORY_DIR"
}

# ── Safe JSON string escaping via jq ─────────────────────
# Usage: json_str=$(safe_json_str "$user_string")
safe_json_str() {
  printf '%s' "$1" | jq -Rs .
}

# ── Read file or stdin ────────────────────────────────────
# Usage: content=$(read_input "$filepath_or_dash")
read_input() {
  local path="$1"
  if [ "$path" = "-" ] || [ -z "$path" ]; then
    cat
  elif [ -f "$path" ]; then
    cat "$path"
  else
    die "File not found: $path" "Check the file path and try again."
  fi
}

# ── Validate transcript is not empty ──────────────────────
validate_transcript() {
  local content="$1"
  local char_count
  char_count="${#content}"
  if [ "$char_count" -lt 20 ]; then
    die "Transcript is too short ($char_count chars)." \
      "Paste a meeting transcript or provide a file path. Minimum ~20 characters."
  fi
}

# ── Validate API URL base ─────────────────────────────────
# Allows only http(s) URLs to prevent unsafe curl schemes.
validate_http_url() {
  local url="$1"
  local label="${2:-URL}"
  case "$url" in
    http://*|https://*) ;;
    *)
      die "$label must use http:// or https:// scheme." "Got: $url"
      ;;
  esac
}

# ── Detect transcript format ─────────────────────────────
# Returns: vtt, srt, or txt
detect_format() {
  local content="$1"
  local first_lines
  first_lines="$(echo "$content" | head -20)"

  # WebVTT signature
  if echo "$first_lines" | grep -qi "^WEBVTT"; then
    echo "vtt"
    return
  fi

  # SRT: first line is a number, followed by timestamp with -->
  if echo "$first_lines" | grep -qE '^[0-9]+$' && \
     echo "$first_lines" | grep -qE '[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3} -->'; then
    echo "srt"
    return
  fi

  echo "txt"
}

# ── Timestamp for filenames ───────────────────────────────
timestamp_slug() {
  date -u +%Y%m%dT%H%M%SZ
}

# ── Word count helper ─────────────────────────────────────
word_count() {
  echo "$1" | wc -w | tr -d ' '
}
