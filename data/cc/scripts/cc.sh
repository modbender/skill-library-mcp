#!/usr/bin/env bash
set -euo pipefail

# === Binary discovery (override via env) ===
BASH_BIN="${BASH_BIN:-$(command -v bash 2>/dev/null || true)}"
TMUX="${TMUX:-$(command -v tmux 2>/dev/null || true)}"
FIND="${FIND:-$(command -v find 2>/dev/null || true)}"
SORT="${SORT:-$(command -v sort 2>/dev/null || true)}"
AWK="${AWK:-$(command -v awk 2>/dev/null || true)}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Locate relay.sh: env > sibling skill dir > managed skills
find_relay() {
  # 1. Explicit env
  if [[ -n "${CLAUDE_RELAY_DIR:-}" ]]; then
    local candidate="${CLAUDE_RELAY_DIR}/scripts/relay.sh"
    [[ -f "${candidate}" ]] && { echo "${candidate}"; return 0; }
  fi

  # 2. Sibling skill directory (workspace or managed layout)
  local sibling
  sibling="$(cd "${SCRIPT_DIR}/../../claude-relay/scripts" 2>/dev/null && pwd)/relay.sh"
  [[ -f "${sibling}" ]] && { echo "${sibling}"; return 0; }

  # 3. OpenClaw managed skills directory
  local state_dir="${OPENCLAW_STATE_DIR:-${XDG_STATE_HOME:-$HOME/.local/state}/openclaw}"
  for search_dir in "${state_dir}/workspace/skills" "${state_dir}/skills"; do
    local managed="${search_dir}/claude-relay/scripts/relay.sh"
    [[ -f "${managed}" ]] && { echo "${managed}"; return 0; }
  done

  return 1
}

RELAY="$(find_relay)" || {
  echo "claude-relay skill not found. Install it first: openclaw skills install claude-relay" >&2
  exit 2
}

# Locate projects.map from relay skill dir
RELAY_SKILL_DIR="$(cd "$(dirname "${RELAY}")/.." && pwd)"
MAP_FILE="${CLAUDE_RELAY_MAP:-${RELAY_SKILL_DIR}/projects.map}"
PROJECT_ROOT="${CLAUDE_RELAY_ROOT:-${HOME}/projects}"

first="${1:-}"
shift || true

run_relay() {
  ${BASH_BIN} "${RELAY}" "$@"
}

generate_project_pairs() {
  {
    if [[ -f "${MAP_FILE}" ]]; then
      ${AWK} -F'=' '
        /^[[:space:]]*#/ { next }
        /^[[:space:]]*$/ { next }
        {
          k=$1
          v=substr($0, index($0, "=")+1)
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", k)
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", v)
          if (k != "" && v != "") print k "|" v
        }
      ' "${MAP_FILE}"
    fi

    if [[ -d "${PROJECT_ROOT}" ]]; then
      ${FIND} "${PROJECT_ROOT}" -mindepth 1 -maxdepth 1 -type d ! -name '.*' -printf '%f|%p\n' 2>/dev/null
    fi
  } | ${AWK} -F'|' '
      NF >= 2 && $1 != "" && $2 != "" {
        key=tolower($1)
        if (!seen[key]++) print $1 "|" $2
      }
    '
}

list_projects() {
  local lines
  lines="$(generate_project_pairs | ${SORT} -f || true)"
  if [[ -z "${lines}" ]]; then
    echo "no projects found"
    return 0
  fi
  echo "available projects:"
  while IFS='|' read -r alias path; do
    [[ -n "${alias}" && -n "${path}" ]] || continue
    printf ' - %-22s %s\n' "${alias}" "${path}"
  done <<< "${lines}"
}

resolve_project_keyword() {
  local key="${1:-}"
  [[ -n "${key}" ]] || return 1

  if [[ "${key}" == /* ]]; then
    [[ -d "${key}" ]] || {
      echo "directory not found: ${key}" >&2
      return 1
    }
    echo "${key}"
    return 0
  fi

  # Exact alias match (case-sensitive)
  local exact
  exact="$(generate_project_pairs | ${AWK} -F'|' -v k="${key}" '$1==k {print $2; exit}')"
  if [[ -n "${exact}" ]]; then
    echo "${exact}"
    return 0
  fi

  # Case-insensitive exact alias match
  mapfile -t exact_ci < <(generate_project_pairs | ${AWK} -F'|' -v k="${key,,}" 'tolower($1)==k {print $2}')
  if (( ${#exact_ci[@]} == 1 )); then
    echo "${exact_ci[0]}"
    return 0
  fi
  if (( ${#exact_ci[@]} > 1 )); then
    echo "ambiguous project key '${key}'" >&2
    return 1
  fi

  # Fuzzy alias/path contains
  mapfile -t fuzzy < <(generate_project_pairs | ${AWK} -F'|' -v k="${key,,}" 'index(tolower($1),k)>0 || index(tolower($2),k)>0 {print $1 "|" $2}')
  if (( ${#fuzzy[@]} == 1 )); then
    echo "${fuzzy[0]#*|}"
    return 0
  fi
  if (( ${#fuzzy[@]} > 1 )); then
    echo "ambiguous project '${key}', candidates:" >&2
    for row in "${fuzzy[@]}"; do
      local a p
      a="${row%%|*}"
      p="${row#*|}"
      printf ' - %-22s %s\n' "${a}" "${p}" >&2
    done
    return 1
  fi

  return 1
}

case "${first}" in
  projects|list)
    list_projects
    ;;
  on|start)
    keyword="${1:-}"
    [[ -n "${keyword}" ]] || { echo "usage: /cc on <project-or-keyword>" >&2; exit 1; }
    resolved="$(resolve_project_keyword "${keyword}")" || exit 1
    run_relay start "${resolved}"
    ;;
  off|stop)
    # project optional; relay defaults to last project
    if [[ $# -gt 0 ]]; then
      if resolved="$(resolve_project_keyword "$1" 2>/dev/null)"; then
        run_relay stop "${resolved}"
      else
        run_relay stop "$1"
      fi
    else
      run_relay stop
    fi
    ;;
  tail)
    if [[ $# -eq 0 ]]; then
      run_relay tail "" 120
    elif [[ $# -eq 1 ]]; then
      # Could be project keyword or lines
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        run_relay tail "" "$1"
      else
        if resolved="$(resolve_project_keyword "$1" 2>/dev/null)"; then
          run_relay tail "${resolved}" 120
        else
          run_relay tail "$1" 120
        fi
      fi
    else
      target="$1"
      lines="$2"
      if resolved="$(resolve_project_keyword "${target}" 2>/dev/null)"; then
        run_relay tail "${resolved}" "${lines}"
      else
        run_relay tail "${target}" "${lines}"
      fi
    fi
    ;;
  status)
    run_relay status
    ;;
  "")
    echo "usage: /cc on <project> | /cc projects | /cc tail [project] [lines] | /cc off [project] | /cc <message>" >&2
    exit 1
    ;;
  *)
    # Default send mode:
    # - If first token resolves to an ACTIVE project session, use it as explicit target.
    # - Else send full raw text to last project session.
    if resolved="$(resolve_project_keyword "${first}" 2>/dev/null)"; then
      if session_name="$(${BASH_BIN} "${RELAY}" session "${resolved}" 2>/dev/null)" && ${TMUX} has-session -t "${session_name}" 2>/dev/null; then
        msg="$*"
        [[ -n "${msg}" ]] || { echo "message required after project name" >&2; exit 1; }
        run_relay send "${resolved}" "${msg}"
        exit 0
      fi
    fi

    msg="${first}"
    if [[ $# -gt 0 ]]; then
      msg+=" $*"
    fi
    run_relay send "" "${msg}"
    ;;
esac
