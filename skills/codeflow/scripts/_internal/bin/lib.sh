#!/bin/bash

codeflow_state_dir() {
  local script_dir="${1:?script_dir required}"
  local base dir

  base="${XDG_STATE_HOME:-${HOME:-}/.local/state}"
  dir="${base%/}/codeflow"

  if [ -n "$base" ] && mkdir -p "$dir" 2>/dev/null; then
    chmod 700 "$dir" 2>/dev/null || true
    echo "$dir"
    return 0
  fi

  echo "$script_dir"
  return 0
}

codeflow_require_python310() {
  local script_dir="${CODEFLOW_SCRIPT_DIR:-}"
  if [ -z "$script_dir" ]; then
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  fi

  if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: python3 not found (requires Python >= 3.10)" >&2
    exit 1
  fi

  PYTHONPATH="$script_dir${PYTHONPATH:+:$PYTHONPATH}" python3 -c '
from py_compat import require_python310
require_python310(prog="codeflow")
'
}

codeflow_trim() {
  local s="${1-}"
  s="${s#"${s%%[!$' \t\r\n']*}"}"
  s="${s%"${s##*[!$' \t\r\n']}"}"
  printf '%s' "$s"
}

codeflow_parse_task_line() {
  local line="${1-}"
  local trimmed dir_raw prompt_raw dir prompt

  if [[ "$line" =~ ^[[:space:]]*# ]]; then
    return 1
  fi
  trimmed="$(codeflow_trim "$line")"
  [ -z "$trimmed" ] && return 1

  [[ "$line" != *"|"* ]] && return 2
  dir_raw="${line%%|*}"
  prompt_raw="${line#*|}"
  dir="$(codeflow_trim "$dir_raw")"
  prompt="$(codeflow_trim "$prompt_raw")"

  if [[ ${#dir} -ge 2 && "$dir" == \"*\" && "$dir" == *\" ]]; then
    dir="${dir:1:-1}"
  fi
  if [[ ${#dir} -ge 2 && "$dir" == \'*\' && "$dir" == *\' ]]; then
    dir="${dir:1:-1}"
  fi
  if [[ ${#prompt} -ge 2 && "$prompt" == \"*\" && "$prompt" == *\" ]]; then
    prompt="${prompt:1:-1}"
  fi
  if [[ ${#prompt} -ge 2 && "$prompt" == \'*\' && "$prompt" == *\' ]]; then
    prompt="${prompt:1:-1}"
  fi

  dir="$(codeflow_trim "$dir")"
  prompt="$(codeflow_trim "$prompt")"
  [ -z "$dir" ] && return 2
  [ -z "$prompt" ] && return 2

  printf '%s\t%s' "$dir" "$prompt"
  return 0
}

codeflow_infer_platform() {
  local script_dir="${1:?script_dir required}"
  local requested="${2:-auto}"
  local state_file_read="${3:-}"
  local tg_chat_id="${4:-}"
  local tg_thread_id="${5:-}"
  local platform state_chat state_thread

  platform="$(printf '%s' "$requested" | tr '[:upper:]' '[:lower:]')"
  [ -z "$platform" ] && platform="auto"

  if [ "$platform" != "auto" ]; then
    printf '%s' "$platform"
    return 0
  fi

  codeflow_resolve_openclaw_session_context

  state_chat=""
  state_thread=""
  if [ -n "$state_file_read" ] && [ -f "$state_file_read" ]; then
    state_chat="$(codeflow_state_get "$state_file_read" telegram_chat_id)"
    state_thread="$(codeflow_state_get "$state_file_read" telegram_thread_id)"
  fi

  if [ -n "$tg_chat_id" ] || [ -n "${TELEGRAM_CHAT_ID:-}" ] || [ -n "${CODEFLOW_TELEGRAM_CHAT_ID:-}" ] || [ -n "$state_chat" ]; then
    printf '%s' "telegram"
    return 0
  fi

  if [ -s "$script_dir/.webhook-url" ]; then
    printf '%s' "discord"
    return 0
  fi

  printf '%s' "telegram"
  return 0
}

codeflow_init_default_paths() {
  local script_dir="${1:?script_dir required}"
  CODEFLOW_SCRIPT_DIR="$script_dir"
  CODEFLOW_STATE_DIR="$(codeflow_state_dir "$script_dir")"

  if [ "$CODEFLOW_STATE_DIR" = "$script_dir" ]; then
    CODEFLOW_STATE_FILE_DEFAULT="$script_dir/.codeflow-state.json"
    CODEFLOW_GUARD_FILE_DEFAULT="$script_dir/.codeflow-guard.json"
    CODEFLOW_AUDIT_FILE_DEFAULT="$script_dir/.codeflow-audit.jsonl"
  fi

  if [ "$CODEFLOW_STATE_DIR" != "$script_dir" ]; then
    CODEFLOW_STATE_FILE_DEFAULT="$CODEFLOW_STATE_DIR/dev-relay-state.json"
    CODEFLOW_GUARD_FILE_DEFAULT="$CODEFLOW_STATE_DIR/guard.json"
    CODEFLOW_AUDIT_FILE_DEFAULT="$CODEFLOW_STATE_DIR/guard-audit.jsonl"
  fi
}

codeflow_state_get() {
  local path="${1:?path required}"
  local key="${2:?key required}"
  python3 - "$path" "$key" <<'PY'
import json
import sys
path, key = sys.argv[1], sys.argv[2]
try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    val = data.get(key, "") if isinstance(data, dict) else ""
    if isinstance(val, str):
        print(val)
except Exception:
    pass
PY
}

codeflow_state_set() {
  local path="${1:?path required}"
  local key="${2:?key required}"
  local value="${3:-}"
  python3 - "$path" "$key" "$value" <<'PY'
import fcntl
import json
import os
import sys
import tempfile

path, key, value = sys.argv[1], sys.argv[2], sys.argv[3]
obj = {}

dir_path = os.path.dirname(path) or "."
os.makedirs(dir_path, exist_ok=True)
lock_path = path + ".lock"
lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    try:
        with open(path, "r", encoding="utf-8") as f:
            cur = json.load(f)
            if isinstance(cur, dict):
                obj = cur
    except Exception:
        obj = {}

    obj[key] = value

    fd, tmp = tempfile.mkstemp(prefix="codeflow-state-", dir=dir_path)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(tmp, path)
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass

        try:
            dfd = os.open(dir_path, os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            pass
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass
finally:
    try:
        os.close(lock_fd)
    except Exception:
        pass
PY
}

codeflow_resolve_openclaw_session_context() {
  local session_key="${OPENCLAW_SESSION_KEY:-${OPENCLAW_SESSION:-}}"
  [ -z "$session_key" ] && return 0

  if [[ "$session_key" == *":telegram:group:"* ]]; then
    local tail chat
    tail="${session_key##*:telegram:group:}"
    chat="${tail%%:*}"
    if [ -n "$chat" ]; then
      TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-$chat}"
    fi

    if [[ "$tail" == *":topic:"* ]]; then
      local topic
      topic="${tail##*:topic:}"
      topic="${topic%%:*}"
      TELEGRAM_THREAD_ID="${TELEGRAM_THREAD_ID:-$topic}"
    fi
    return 0
  fi

  if [[ "$session_key" == *":telegram:direct:"* ]]; then
    local direct
    direct="${session_key##*:telegram:direct:}"
    direct="${direct%%:*}"
    TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-$direct}"
    TELEGRAM_THREAD_ID=""
  fi
}
