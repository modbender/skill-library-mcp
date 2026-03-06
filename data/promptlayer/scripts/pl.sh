#!/usr/bin/env bash
# pl.sh — PromptLayer REST API CLI wrapper
# Aligned with official docs: https://docs.promptlayer.com/reference/rest-api-reference
set -euo pipefail

BASE_URL="${PROMPTLAYER_BASE_URL:-https://api.promptlayer.com}"
API_KEY="${PROMPTLAYER_API_KEY:?Set PROMPTLAYER_API_KEY env var}"

json_header="Content-Type: application/json"
api_key_header="X-API-KEY: $API_KEY"

# URL-encode a string
urlencode() { python3 -c "import sys,urllib.parse;print(urllib.parse.quote(sys.stdin.read().strip(),safe=''))"; }

# API call helper
api() {
  local method="$1" path="$2"; shift 2
  curl -sS -X "$method" "${BASE_URL}${path}" \
    -H "$api_key_header" -H "$json_header" "$@"
}

usage() {
  cat <<'EOF'
Usage: pl.sh <command> [subcommand] [args...]

Prompt Templates:
  templates list [--name <filter>] [--label <label>]
  templates get <name|id> [--label <label>] [--version <n>] [--provider openai|anthropic]
  templates publish                         Publish template (JSON on stdin)
  templates labels                          List release labels

Tracking (all under /rest/):
  log                                       Log an LLM request (JSON on stdin)
  track-prompt <req_id> <prompt_name> [--version <n>] [--vars '{}']
  track-score <req_id> <score> [--name <name>]
  track-metadata <req_id> --json '{}'
  track-group <req_id> <group_id>

Datasets & Evaluations (v2 API):
  datasets list [--name <filter>]
  evals list [--name <filter>]
  evals run <eval_id>
  evals get <eval_id>

Agents:
  agents list
  agents run <agent_id> --input '{}'

Other:
  help                                      Show this help
EOF
}

# --- Templates (path: /prompt-templates) ---
cmd_templates() {
  local sub="${1:-}"; shift || true
  case "$sub" in
    list)
      local params=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --name)  params+="&name=$2"; shift 2 ;;
          --label) params+="&label=$2"; shift 2 ;;
          --page)  params+="&page=$2"; shift 2 ;;
          *) shift ;;
        esac
      done
      params="${params:+?${params:1}}"
      api GET "/prompt-templates${params}"
      ;;
    get)
      local id="${1:?Usage: pl.sh templates get <name|id> [--label <label>] [--version <n>]}"; shift
      local body="{}"
      local parts=()
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --label)    parts+=("\"label\": \"$2\""); shift 2 ;;
          --version)  parts+=("\"version\": $2"); shift 2 ;;
          --provider) parts+=("\"provider\": \"$2\""); shift 2 ;;
          *) shift ;;
        esac
      done
      if [[ ${#parts[@]} -gt 0 ]]; then
        local IFS=','; body="{${parts[*]}}"
      fi
      local encoded; encoded="$(echo "$id" | urlencode)"
      api POST "/prompt-templates/${encoded}" -d "$body"
      ;;
    publish)
      local body; body="$(cat)"
      api POST "/rest/prompt-templates" -d "$body"
      ;;
    labels)
      api GET "/prompt-templates/labels"
      ;;
    *)
      echo "Usage: pl.sh templates [list|get|publish|labels]" >&2; exit 1
      ;;
  esac
}

# --- Logging (path: /rest/log-request) ---
cmd_log() {
  local body; body="$(cat)"
  api POST "/log-request" -d "$body"
}

# --- Tracking (paths: /rest/track-*) ---
cmd_track_prompt() {
  local req_id="${1:?}" prompt_name="${2:?}"; shift 2
  local parts=("\"request_id\": $req_id" "\"prompt_name\": \"$prompt_name\"")
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --version) parts+=("\"version\": $2"); shift 2 ;;
      --vars)    parts+=("\"prompt_input_variables\": $2"); shift 2 ;;
      *) shift ;;
    esac
  done
  local IFS=','; api POST "/rest/track-prompt" -d "{${parts[*]}}"
}

cmd_track_score() {
  local req_id="${1:?}" score="${2:?}"; shift 2
  local name=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name) name="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  local body="{\"request_id\": $req_id, \"score\": $score"
  [[ -n "$name" ]] && body+=", \"name\": \"$name\""
  body+="}"
  api POST "/rest/track-score" -d "$body"
}

cmd_track_metadata() {
  local req_id="${1:?}"; shift
  local json="{}"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --json) json="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  api POST "/rest/track-metadata" \
    -d "{\"request_id\": $req_id, \"metadata\": $json}"
}

cmd_track_group() {
  local req_id="${1:?}" group_id="${2:?}"
  api POST "/rest/track-group" \
    -d "{\"request_id\": $req_id, \"group_id\": $group_id}"
}

# --- Datasets (path: /api/public/v2/datasets) ---
cmd_datasets() {
  local sub="${1:-list}"; shift || true
  case "$sub" in
    list)
      local params=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --name) params+="&name=$2"; shift 2 ;;
          --page) params+="&page=$2"; shift 2 ;;
          *) shift ;;
        esac
      done
      params="${params:+?${params:1}}"
      api GET "/api/public/v2/datasets${params}"
      ;;
    *) echo "Usage: pl.sh datasets list [--name <filter>]" >&2; exit 1 ;;
  esac
}

# --- Evaluations (path: /api/public/v2/evaluations) ---
cmd_evals() {
  local sub="${1:-}"; shift || true
  case "$sub" in
    list)
      local params=""
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --name) params+="&name=$2"; shift 2 ;;
          --page) params+="&page=$2"; shift 2 ;;
          *) shift ;;
        esac
      done
      params="${params:+?${params:1}}"
      api GET "/api/public/v2/evaluations${params}"
      ;;
    run)
      local eval_id="${1:?Usage: pl.sh evals run <eval_id>}"
      api POST "/api/public/v2/evaluations/${eval_id}/run"
      ;;
    get)
      local eval_id="${1:?Usage: pl.sh evals get <eval_id>}"
      api GET "/api/public/v2/evaluations/${eval_id}"
      ;;
    *)
      echo "Usage: pl.sh evals [list|run|get]" >&2; exit 1
      ;;
  esac
}

# --- Agents (path: /workflows) ---
cmd_agents() {
  local sub="${1:-}"; shift || true
  case "$sub" in
    list)
      api GET "/workflows"
      ;;
    run)
      local agent_id="${1:?Usage: pl.sh agents run <id> --input '{}'}"
      shift
      local input="{}"
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --input) input="$2"; shift 2 ;;
          *) shift ;;
        esac
      done
      api POST "/workflows/${agent_id}/run" -d "$input"
      ;;
    *)
      echo "Usage: pl.sh agents [list|run]" >&2; exit 1
      ;;
  esac
}

# --- Main ---
cmd="${1:-help}"; shift || true
case "$cmd" in
  templates)      cmd_templates "$@" ;;
  log)            cmd_log "$@" ;;
  track-prompt)   cmd_track_prompt "$@" ;;
  track-score)    cmd_track_score "$@" ;;
  track-metadata) cmd_track_metadata "$@" ;;
  track-group)    cmd_track_group "$@" ;;
  datasets)       cmd_datasets "$@" ;;
  evals)          cmd_evals "$@" ;;
  agents)         cmd_agents "$@" ;;
  help|--help|-h) usage ;;
  *)              echo "Unknown command: $cmd" >&2; usage; exit 1 ;;
esac
