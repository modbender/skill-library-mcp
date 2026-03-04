#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$SKILL_DIR/.project_os_env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

PROJECT_OS_DB="${PROJECT_OS_DB:-$HOME/.project_os/openclaw_test.db}"
PROJECT_OS_CONFIG="${PROJECT_OS_CONFIG:-$HOME/.project_os/openclaw_test_config.json}"
PROJECT_OS_MEMORY="${PROJECT_OS_MEMORY:-$HOME/.project_os/PROJECT_MEMORY.md}"
PROJECT_OS_HOST="${PROJECT_OS_HOST:-127.0.0.1}"
PROJECT_OS_PORT="${PROJECT_OS_PORT:-8765}"
PROJECT_OS_AUTO_SETUP="${PROJECT_OS_AUTO_SETUP:-0}"
PROJECT_OS_ALLOW_REMOTE_INSTALL="${PROJECT_OS_ALLOW_REMOTE_INSTALL:-0}"
PROJECT_OS_REPO_URL="${PROJECT_OS_REPO_URL:-https://github.com/LDodee/project-os.git}"
PROJECT_OS_INSTALL_DIR="${PROJECT_OS_INSTALL_DIR:-$HOME/.project_os/project-os}"
PROJECT_OS_TRUSTED_REPO_URL="${PROJECT_OS_TRUSTED_REPO_URL:-https://github.com/LDodee/project-os.git}"

export PROJECT_OS_DB
export PROJECT_OS_CONFIG
export PROJECT_OS_MEMORY
export PROJECT_OS_HOST
export PROJECT_OS_PORT
export PROJECT_OS_AUTO_SETUP
export PROJECT_OS_ALLOW_REMOTE_INSTALL
export PROJECT_OS_REPO_URL
export PROJECT_OS_INSTALL_DIR
export PROJECT_OS_TRUSTED_REPO_URL
export PROJECT_OS_PRIVACY_MODE
export PROJECT_OS_ENABLE_HOME_DISCOVERY
export PROJECT_OS_INCLUDE_CHAT_ROOTS
export PROJECT_OS_ENABLE_GITHUB_SYNC
export PROJECT_OS_EXTRA_ROOTS

_is_project_os_root() {
  local candidate="$1"
  [[ -n "$candidate" ]] || return 1
  [[ -d "$candidate" ]] || return 1
  [[ -f "$candidate/pyproject.toml" ]] || return 1
  [[ -f "$candidate/project_os/cli.py" ]] || return 1
}

_discover_project_os_root() {
  local maybe_repo_root=""
  maybe_repo_root="$(cd "$SCRIPT_DIR/../../../.." 2>/dev/null && pwd || true)"

  local candidates=(
    "${PROJECT_OS_ROOT:-}"
    "$PWD"
    "$maybe_repo_root"
    "$HOME/GitHub/04-products/project-os"
    "$HOME/GitHub/project-os"
    "$HOME/project-os"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    if _is_project_os_root "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

_install_project_os_root() {
  if [[ "$PROJECT_OS_AUTO_SETUP" != "1" || "$PROJECT_OS_ALLOW_REMOTE_INSTALL" != "1" ]]; then
    return 1
  fi
  if ! command -v git >/dev/null 2>&1; then
    printf 'Could not locate project-os and git is unavailable for remote install.\n' >&2
    return 1
  fi
  if [[ "$PROJECT_OS_REPO_URL" != "$PROJECT_OS_TRUSTED_REPO_URL" ]]; then
    printf 'Remote install blocked: PROJECT_OS_REPO_URL must match PROJECT_OS_TRUSTED_REPO_URL.\n' >&2
    return 1
  fi

  mkdir -p "$(dirname "$PROJECT_OS_INSTALL_DIR")"
  if [[ -d "$PROJECT_OS_INSTALL_DIR/.git" ]]; then
    # Existing clone is reused as-is; no forced reset/update.
    :
  elif [[ -d "$PROJECT_OS_INSTALL_DIR" ]]; then
    printf 'Remote install blocked: %s exists but is not a git clone.\n' "$PROJECT_OS_INSTALL_DIR" >&2
    return 1
  else
    git clone --depth 1 "$PROJECT_OS_REPO_URL" "$PROJECT_OS_INSTALL_DIR" >/dev/null 2>&1 || return 1
  fi

  if _is_project_os_root "$PROJECT_OS_INSTALL_DIR"; then
    printf '%s\n' "$PROJECT_OS_INSTALL_DIR"
    return 0
  fi
  return 1
}

project_os_root() {
  local root=""
  root="$(_discover_project_os_root || true)"
  if [[ -z "$root" ]]; then
    root="$(_install_project_os_root || true)"
  fi
  if [[ -z "$root" ]]; then
    printf 'Could not locate project-os repository. Set PROJECT_OS_ROOT or explicitly allow remote install (PROJECT_OS_AUTO_SETUP=1 and PROJECT_OS_ALLOW_REMOTE_INSTALL=1).\n' >&2
    return 1
  fi
  printf '%s\n' "$root"
}

project_os_python() {
  local root="${1:-}"
  if [[ -n "$root" && -x "$root/.venv/bin/python" ]]; then
    printf '%s\n' "$root/.venv/bin/python"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    printf 'python3\n'
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    printf 'python\n'
    return 0
  fi
  printf 'Python is required but was not found in PATH.\n' >&2
  return 1
}

project_os_cli() {
  local root
  local py
  root="$(project_os_root)"
  py="$(project_os_python "$root")"
  (
    cd "$root"
    "$py" -m project_os.cli --db "$PROJECT_OS_DB" --config "$PROJECT_OS_CONFIG" "$@"
  )
}

print_runtime_config() {
  local root
  root="$(project_os_root)"
  printf 'PROJECT_OS_ROOT=%s\n' "$root"
  printf 'PROJECT_OS_DB=%s\n' "$PROJECT_OS_DB"
  printf 'PROJECT_OS_CONFIG=%s\n' "$PROJECT_OS_CONFIG"
  printf 'PROJECT_OS_MEMORY=%s\n' "$PROJECT_OS_MEMORY"
  printf 'DASHBOARD_URL=http://%s:%s\n' "$PROJECT_OS_HOST" "$PROJECT_OS_PORT"
}
