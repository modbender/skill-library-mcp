#!/usr/bin/env bash
set -euo pipefail

base_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
}

normalize_project_name() {
  printf '%s' "$1" | tr -cs '[:alnum:]' '-'
}

session_name_from_project() {
  local project_name
  project_name="$(normalize_project_name "$1")"
  printf '%s-code-session\n' "$project_name"
}

session_name() {
  session_name_from_project "$(basename "$(pwd)")"
}

require_tmux() {
  if ! command -v tmux >/dev/null 2>&1; then
    echo "tmux not found. Install tmux first." >&2
    exit 1
  fi
}

has_session() {
  local session
  session="$(session_name)"
  tmux has-session -t "$session" 2>/dev/null
}

ensure_session() {
  local session
  session="$(session_name)"
  require_tmux

  if has_session; then
    return 0
  fi

  tmux new-session -d -s "$session" -c "$(pwd)"
  echo "Created session: $session"
}

pct_now_utc() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

pct_state_path() {
  printf '%s/.pct-state.json\n' "$(pwd)"
}

pct_json_escape() {
  printf '%s' "$1" | awk '
    BEGIN { first = 1 }
    {
      gsub(/\\/, "\\\\")
      gsub(/"/, "\\\"")
      gsub(/\r/, "\\r")
      gsub(/\t/, "\\t")
      if (first == 0) {
        printf "\\n"
      }
      printf "%s", $0
      first = 0
    }
  '
}

pct_json_quote_or_null() {
  if [ -z "${1:-}" ]; then
    printf 'null'
    return 0
  fi

  printf '"%s"' "$(pct_json_escape "$1")"
}

pct_state_read_token() {
  local field="$1"
  local file
  file="$(pct_state_path)"

  if [ ! -f "$file" ]; then
    return 1
  fi

  awk -v key="\"$field\"" '
    $1 == key {
      sub(/^[^:]*:[[:space:]]*/, "")
      sub(/[[:space:]]*,?[[:space:]]*$/, "")
      print
      exit
    }
  ' "$file"
}

pct_state_read_string() {
  local field="$1"
  local token

  token="$(pct_state_read_token "$field" 2>/dev/null || true)"
  if [ -z "$token" ] || [ "$token" = "null" ]; then
    printf ''
    return 0
  fi

  token="${token#\"}"
  token="${token%\"}"
  token="${token//\\n/$'\n'}"
  token="${token//\\r/$'\r'}"
  token="${token//\\t/$'\t'}"
  token="${token//\\\"/\"}"
  token="${token//\\\\/\\}"
  printf '%s' "$token"
}

pct_state_write() {
  local project_dir="$1"
  local session="$2"
  local last_command="$3"
  local last_exit_code_token="$4"
  local phase="$5"
  local updated_at="$6"
  local state_file
  local phase_json

  state_file="$(pct_state_path)"

  if [ -z "$last_exit_code_token" ]; then
    last_exit_code_token="null"
  fi

  if [ -z "$phase" ]; then
    phase_json="null"
  else
    phase_json="\"$(pct_json_escape "$phase")\""
  fi

  cat >"$state_file" <<EOF_STATE
{
  "projectDir": "$(pct_json_escape "$project_dir")",
  "session": "$(pct_json_escape "$session")",
  "lastCommand": "$(pct_json_escape "$last_command")",
  "lastExitCode": ${last_exit_code_token},
  "phase": ${phase_json},
  "updatedAt": "$(pct_json_escape "$updated_at")"
}
EOF_STATE
}

pct_state_update_start() {
  local session_override="${1:-}"
  local project_dir
  local session
  local updated_at
  local last_command
  local last_exit
  local phase

  project_dir="$(pwd -P)"
  if [ -n "$session_override" ]; then
    session="$session_override"
  else
    session="$(session_name)"
  fi
  updated_at="$(pct_now_utc)"
  last_command="$(pct_state_read_string "lastCommand")"
  last_exit="$(pct_state_read_token "lastExitCode" 2>/dev/null || true)"
  phase="$(pct_state_read_string "phase")"

  if [ -z "$last_exit" ]; then
    last_exit="null"
  fi

  pct_state_write "$project_dir" "$session" "$last_command" "$last_exit" "$phase" "$updated_at"
}

pct_state_update_send() {
  local command="$1"
  local phase="${2:-}"
  local project_dir
  local session
  local updated_at

  project_dir="$(pwd -P)"
  session="$(session_name)"
  updated_at="$(pct_now_utc)"

  pct_state_write "$project_dir" "$session" "$command" "null" "$phase" "$updated_at"
}

pct_state_update_read_exit() {
  local maybe_exit="$1"
  local project_dir
  local session
  local updated_at
  local last_command
  local last_exit
  local phase

  project_dir="$(pwd -P)"
  session="$(session_name)"
  updated_at="$(pct_now_utc)"
  last_command="$(pct_state_read_string "lastCommand")"
  phase="$(pct_state_read_string "phase")"

  if [ -n "$maybe_exit" ]; then
    last_exit="$maybe_exit"
  else
    last_exit="$(pct_state_read_token "lastExitCode" 2>/dev/null || true)"
    if [ -z "$last_exit" ]; then
      last_exit="null"
    fi
  fi

  pct_state_write "$project_dir" "$session" "$last_command" "$last_exit" "$phase" "$updated_at"
}
