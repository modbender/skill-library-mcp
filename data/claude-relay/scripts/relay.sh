#!/usr/bin/env bash
set -euo pipefail

# === Binary discovery (override via env) ===
TMUX="${TMUX:-$(command -v tmux 2>/dev/null || true)}"
FIND="${FIND:-$(command -v find 2>/dev/null || true)}"
SORT="${SORT:-$(command -v sort 2>/dev/null || true)}"
SLEEP="${SLEEP:-$(command -v sleep 2>/dev/null || true)}"
TAIL="${TAIL:-$(command -v tail 2>/dev/null || true)}"
GREP="${GREP:-$(command -v grep 2>/dev/null || true)}"
BASENAME="${BASENAME:-$(command -v basename 2>/dev/null || true)}"
AWK="${AWK:-$(command -v awk 2>/dev/null || true)}"
CAT="${CAT:-$(command -v cat 2>/dev/null || true)}"
MKDIR="${MKDIR:-$(command -v mkdir 2>/dev/null || true)}"

ACTION="${1:-}"
shift || true

if [[ -z "${ACTION}" ]]; then
  echo "usage: relay.sh <start|send|tail|stop|status|session> [project-or-path] [args...]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MAP_FILE="${CLAUDE_RELAY_MAP:-${SKILL_DIR}/projects.map}"
PROJECT_ROOT="${CLAUDE_RELAY_ROOT:-${HOME}/projects}"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/claude-relay"
LAST_FILE="${STATE_DIR}/last_project"
CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude 2>/dev/null || true)}"

${MKDIR} -p "${STATE_DIR}"

need_bin() {
  [[ -n "$1" && -x "$1" ]] || {
    echo "missing dependency: ${2:-$1}" >&2
    exit 2
  }
}

sanitize() {
  local raw="${1,,}"
  raw="${raw//[^a-z0-9_]/_}"
  raw="${raw#__}"
  raw="${raw%%__}"
  echo "${raw:0:40}"
}

resolve_from_map() {
  local key="$1"
  [[ -f "${MAP_FILE}" ]] || return 1
  local line
  line="$(${AWK} -F'=' -v k="$key" '$1==k {print $2; exit}' "${MAP_FILE}" || true)"
  [[ -n "${line}" ]] || return 1
  [[ -d "${line}" ]] || {
    echo "alias '${key}' points to missing directory: ${line}" >&2
    exit 3
  }
  echo "${line}"
}

resolve_project() {
  local input="${1:-}"
  local resolved=""

  if [[ -z "${input}" ]]; then
    if [[ -f "${LAST_FILE}" ]]; then
      resolved="$(cat "${LAST_FILE}")"
      [[ -d "${resolved}" ]] || {
        echo "last project no longer exists: ${resolved}" >&2
        exit 4
      }
      echo "${resolved}"
      return 0
    fi
    echo "project required (or run start once to set last project)" >&2
    exit 4
  fi

  if [[ "${input}" == /* ]]; then
    [[ -d "${input}" ]] || {
      echo "directory not found: ${input}" >&2
      exit 4
    }
    echo "${input}"
    return 0
  fi

  if resolved="$(resolve_from_map "${input}" 2>/dev/null)"; then
    echo "${resolved}"
    return 0
  fi

  if [[ -d "${PROJECT_ROOT}/${input}" ]]; then
    echo "${PROJECT_ROOT}/${input}"
    return 0
  fi

  local matches
  mapfile -t matches < <(${FIND} "${PROJECT_ROOT}" -maxdepth 2 -type d -name "${input}" 2>/dev/null | ${SORT})
  if (( ${#matches[@]} == 1 )); then
    echo "${matches[0]}"
    return 0
  fi
  if (( ${#matches[@]} > 1 )); then
    echo "ambiguous project '${input}', candidates:" >&2
    printf ' - %s\n' "${matches[@]}" >&2
    exit 5
  fi

  echo "project not found: ${input}" >&2
  exit 4
}

session_name_for_project() {
  local project="$1"
  local base
  base="$(${BASENAME} "${project}")"
  echo "cc_$(sanitize "${base}")"
}

require_session() {
  local session="$1"
  ${TMUX} has-session -t "${session}" 2>/dev/null || {
    echo "session not running: ${session}" >&2
    exit 6
  }
}

start_session() {
  local project="$1"
  local session="$2"

  if ${TMUX} has-session -t "${session}" 2>/dev/null; then
    echo "session exists: ${session}"
  else
    local cmd
    cmd="cd $(printf '%q' "${project}") && $(printf '%q' "${CLAUDE_BIN}") -c"
    ${TMUX} new-session -d -s "${session}" "${cmd}"
    ${SLEEP} 1
    echo "session started: ${session}"
  fi

  echo "${project}" >"${LAST_FILE}"
  ${TMUX} list-sessions | ${GREP} -E "^${session}:" || true
}

send_text() {
  local session="$1"
  shift
  local text="$*"
  [[ -n "${text}" ]] || {
    echo "send requires text" >&2
    exit 7
  }
  ${TMUX} send-keys -t "${session}" -l -- "${text}"
  ${TMUX} send-keys -t "${session}" Enter
}

show_tail() {
  local session="$1"
  local lines="${2:-80}"
  ${TMUX} capture-pane -t "${session}" -p | ${TAIL} -n "${lines}"
}

need_bin "${TMUX}" "tmux"
need_bin "${CLAUDE_BIN}" "claude (install: npm i -g @anthropic-ai/claude-code)"

case "${ACTION}" in
  start)
    project="$(resolve_project "${1:-}")"
    session="$(session_name_for_project "${project}")"
    start_session "${project}" "${session}"
    ;;
  send)
    project="$(resolve_project "${1:-}")"
    shift || true
    session="$(session_name_for_project "${project}")"
    require_session "${session}"
    send_text "${session}" "$@"
    # Auto-tail: wait for Claude to process, then show output
    wait_secs="${RELAY_WAIT:-6}"
    ${SLEEP} "${wait_secs}"
    # If still processing, wait a bit more
    output="$(${TMUX} capture-pane -t "${session}" -p | ${TAIL} -n 5)"
    if echo "${output}" | ${GREP} -qiE "Architecting|Sautéed|Thinking|Reading.*file|Working"; then
      ${SLEEP} 4
    fi
    show_tail "${session}" 80
    ;;
  tail)
    project="$(resolve_project "${1:-}")"
    session="$(session_name_for_project "${project}")"
    lines="${2:-80}"
    require_session "${session}"
    show_tail "${session}" "${lines}"
    ;;
  stop)
    project="$(resolve_project "${1:-}")"
    session="$(session_name_for_project "${project}")"
    if ${TMUX} has-session -t "${session}" 2>/dev/null; then
      ${TMUX} kill-session -t "${session}"
      echo "session stopped: ${session}"
    else
      echo "session not running: ${session}"
    fi
    ;;
  status)
    ${TMUX} list-sessions 2>/dev/null | ${GREP} -E '^cc_' || echo "no relay sessions"
    ;;
  session)
    project="$(resolve_project "${1:-}")"
    session="$(session_name_for_project "${project}")"
    echo "${session}"
    ;;
  *)
    echo "unknown action: ${ACTION}" >&2
    exit 1
    ;;
esac
