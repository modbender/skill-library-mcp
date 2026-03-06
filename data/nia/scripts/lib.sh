#!/bin/bash
# Shared library for Nia API scripts
# Source this file: source "$(dirname "$0")/lib.sh"

BASE_URL="https://apigcp.trynia.ai/v2"

nia_auth() {
  NIA_KEY=$(cat ~/.config/nia/api_key 2>/dev/null || echo "")
  if [ -z "$NIA_KEY" ]; then
    echo "Error: No API key found. Run: echo 'your-key' > ~/.config/nia/api_key"
    exit 1
  fi
  export NIA_KEY
}

urlencode() {
  echo "$1" | sed 's/ /%20/g; s/\//%2F/g'
}

# Generic curl wrapper: nia_curl METHOD URL [DATA]
nia_curl() {
  local method="$1" url="$2" data="${3:-}"
  local args=(-s -X "$method" "$url" -H "Authorization: Bearer $NIA_KEY")
  if [ -n "$data" ]; then
    args+=(-H "Content-Type: application/json" -d "$data")
  fi
  curl "${args[@]}"
}

nia_get()    { nia_curl GET    "$1" | jq '.'; }
nia_post()   { nia_curl POST   "$1" "$2" | jq '.'; }
nia_put()    { nia_curl PUT    "$1" "$2" | jq '.'; }
nia_patch()  { nia_curl PATCH  "$1" "$2" | jq '.'; }
nia_delete() { nia_curl DELETE "$1" | jq '.'; }

# Raw get with custom jq filter: nia_get_raw URL | jq ...
nia_get_raw() { nia_curl GET "$1"; }
nia_post_raw() { nia_curl POST "$1" "$2"; }

# Stream (SSE) — no buffering, no jq
nia_stream() { curl -s -N -X POST "$1" -H "Authorization: Bearer $NIA_KEY" -H "Content-Type: application/json" -d "$2"; }

# Form upload: nia_upload URL field1=val1 field2=val2 file=@path
nia_upload() {
  local url="$1"; shift
  local args=(-s -X POST "$url" -H "Authorization: Bearer $NIA_KEY")
  for f in "$@"; do args+=(-F "$f"); done
  curl "${args[@]}" | jq '.'
}

# Helper: build grep JSON body with all common options
build_grep_json() {
  local pattern="$1" path_prefix="${2:-}"
  jq -n \
    --arg p "$pattern" \
    --arg pp "$path_prefix" \
    --arg cs "${CASE_SENSITIVE:-}" \
    --arg ww "${WHOLE_WORD:-}" \
    --arg fs "${FIXED_STRING:-}" \
    --arg om "${OUTPUT_MODE:-}" \
    --arg hl "${HIGHLIGHT:-}" \
    --arg ex "${EXHAUSTIVE:-}" \
    --arg la "${LINES_AFTER:-}" \
    --arg lb "${LINES_BEFORE:-}" \
    --arg mpf "${MAX_PER_FILE:-}" \
    --arg mt "${MAX_TOTAL:-50}" \
    '{pattern: $p, context_lines: 3, max_total_matches: ($mt | tonumber)}
    + (if $pp != "" then {path: $pp} else {} end)
    + (if $cs != "" then {case_sensitive: ($cs == "true")} else {} end)
    + (if $ww != "" then {whole_word: ($ww == "true")} else {} end)
    + (if $fs != "" then {fixed_string: ($fs == "true")} else {} end)
    + (if $om != "" then {output_mode: $om} else {} end)
    + (if $hl != "" then {highlight: ($hl == "true")} else {} end)
    + (if $ex != "" then {exhaustive: ($ex == "true")} else {} end)
    + (if $la != "" then {A: ($la | tonumber)} else {} end)
    + (if $lb != "" then {B: ($lb | tonumber)} else {} end)
    + (if $mpf != "" then {max_matches_per_file: ($mpf | tonumber)} else {} end)'
}

# Auto-init auth on source
nia_auth
