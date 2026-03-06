#!/usr/bin/env bash
# Grago — Pre-fetch data for tool-less local models
# Usage: grago <command> [options]

set -euo pipefail

VERSION="0.1.0"
CONFIG_DIR="${HOME}/.grago"
CONFIG_FILE="${CONFIG_DIR}/config.yaml"
DEFAULT_MODEL="gemma"
DEFAULT_TIMEOUT=30
DEFAULT_MAX_CHARS=16000
DEFAULT_FORMAT="markdown"

# --- Helpers ---

log() { echo "[grago] $*" >&2; }
err() { echo "[grago] ERROR: $*" >&2; exit 1; }

ensure_deps() {
  for cmd in curl jq; do
    command -v "$cmd" >/dev/null || err "Missing dependency: $cmd"
  done
}

get_config() {
  local key="$1" default="$2"
  if [[ -f "$CONFIG_FILE" ]] && command -v yq >/dev/null 2>&1; then
    local val
    val=$(yq -r ".$key // \"\"" "$CONFIG_FILE" 2>/dev/null)
    [[ -n "$val" && "$val" != "null" ]] && echo "$val" || echo "$default"
  else
    echo "$default"
  fi
}

MODEL=$(get_config "default_model" "$DEFAULT_MODEL")
TIMEOUT=$(get_config "timeout" "$DEFAULT_TIMEOUT")
MAX_CHARS=$(get_config "max_input_chars" "$DEFAULT_MAX_CHARS")
FORMAT=$(get_config "output_format" "$DEFAULT_FORMAT")

truncate_input() {
  head -c "$MAX_CHARS"
}

# --- Core: send text to local model ---

analyze() {
  local prompt="$1"
  local input
  input=$(cat | truncate_input)
  
  local system_msg="You are a research analyst. Respond in ${FORMAT} format. Be concise and focus on actionable insights."
  
  # Try Ollama first
  if command -v ollama >/dev/null 2>&1; then
    echo "${input}" | ollama run "$MODEL" "${prompt}"
    return
  fi
  
  # Fallback: OpenAI-compatible endpoint
  local api_base
  api_base=$(get_config "api_base" "http://localhost:11434/v1")
  
  local payload
  payload=$(jq -n \
    --arg model "$MODEL" \
    --arg system "$system_msg" \
    --arg user "${prompt}\n\n---\nDATA:\n${input}" \
    '{model: $model, messages: [{role: "system", content: $system}, {role: "user", content: $user}], stream: false}')
  
  curl -s "${api_base}/chat/completions" \
    -H "Content-Type: application/json" \
    -d "$payload" | jq -r '.choices[0].message.content // "Error: no response"'
}

# --- Commands ---

cmd_fetch() {
  local url="" prompt="" transform=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --analyze) prompt="$2"; shift 2 ;;
      --transform) transform="$2"; shift 2 ;;
      --model) MODEL="$2"; shift 2 ;;
      --timeout) TIMEOUT="$2"; shift 2 ;;
      *) url="$1"; shift ;;
    esac
  done
  
  [[ -z "$url" ]] && err "Usage: grago fetch <url> [--analyze <prompt>] [--transform <cmd>]"
  
  local data
  data=$(curl -sL --max-time "$TIMEOUT" "$url") || err "Failed to fetch: $url"
  
  if [[ -n "$transform" ]]; then
    data=$(echo "$data" | eval "$transform") || err "Transform failed: $transform"
  fi
  
  if [[ -n "$prompt" ]]; then
    echo "$data" | analyze "$prompt"
  else
    echo "$data"
  fi
}

cmd_research() {
  local sources_file="" prompt="" output_file=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --sources) sources_file="$2"; shift 2 ;;
      --prompt) prompt="$2"; shift 2 ;;
      --output) output_file="$2"; shift 2 ;;
      --model) MODEL="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$sources_file" ]] && err "Usage: grago research --sources <file> --prompt <question>"
  [[ ! -f "$sources_file" ]] && err "Sources file not found: $sources_file"
  
  local combined=""
  local count
  count=$(yq '.sources | length' "$sources_file" 2>/dev/null) || err "Failed to parse sources file (need yq)"
  
  for ((i=0; i<count; i++)); do
    local name url transform type
    name=$(yq -r ".sources[$i].name" "$sources_file")
    url=$(yq -r ".sources[$i].url // \"\"" "$sources_file")
    transform=$(yq -r ".sources[$i].transform // \"\"" "$sources_file")
    type=$(yq -r ".sources[$i].type // \"web\"" "$sources_file")
    
    log "Fetching: $name ($type)"
    
    local data=""
    case "$type" in
      web|api)
        data=$(curl -sL --max-time "$TIMEOUT" "$url" 2>/dev/null) || { log "WARN: Failed $name"; continue; }
        ;;
      file)
        local path
        path=$(yq -r ".sources[$i].path" "$sources_file")
        data=$(cat $path 2>/dev/null) || { log "WARN: Failed $name"; continue; }
        ;;
    esac
    
    if [[ -n "$transform" ]]; then
      data=$(echo "$data" | eval "$transform" 2>/dev/null) || data="[transform failed]"
    fi
    
    combined+="
=== SOURCE: ${name} ===
${data}

"
  done
  
  local result
  result=$(echo "$combined" | analyze "${prompt:-Analyze the following data sources and provide key insights.}")
  
  if [[ -n "$output_file" ]]; then
    echo "$result" > "$output_file"
    log "Output saved to: $output_file"
  fi
  
  echo "$result"
}

cmd_pipe() {
  local fetch_cmd="" transform_cmd="" prompt=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --fetch) fetch_cmd="$2"; shift 2 ;;
      --transform) transform_cmd="$2"; shift 2 ;;
      --analyze) prompt="$2"; shift 2 ;;
      --model) MODEL="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$fetch_cmd" ]] && err "Usage: grago pipe --fetch <cmd> [--transform <cmd>] --analyze <prompt>"
  
  local data
  data=$(eval "$fetch_cmd") || err "Fetch command failed"
  
  if [[ -n "$transform_cmd" ]]; then
    data=$(echo "$data" | eval "$transform_cmd") || err "Transform failed"
  fi
  
  echo "$data" | analyze "${prompt:-Summarize this data.}"
}

cmd_version() { echo "grago v${VERSION}"; }

cmd_help() {
  cat <<EOF
Grago v${VERSION} — Pre-fetch data for tool-less local models

Commands:
  fetch <url>                    Fetch URL, optionally analyze
    --analyze <prompt>           Send fetched data to model with prompt
    --transform <cmd>            Transform data before analysis (e.g., "jq .results")
    --model <name>               Override model
  
  research                       Multi-source fetch + analysis
    --sources <yaml>             Sources definition file
    --prompt <question>          Analysis prompt
    --output <file>              Save output to file
  
  pipe                           Chain fetch → transform → analyze
    --fetch <cmd>                Shell command to fetch data
    --transform <cmd>            Transform command
    --analyze <prompt>           Analysis prompt
  
  version                        Show version
  help                           Show this help

Config: ~/.grago/config.yaml
EOF
}

# --- Main ---

ensure_deps

case "${1:-help}" in
  fetch)    shift; cmd_fetch "$@" ;;
  research) shift; cmd_research "$@" ;;
  pipe)     shift; cmd_pipe "$@" ;;
  version)  cmd_version ;;
  help|*)   cmd_help ;;
esac
