#!/usr/bin/env bash
set -euo pipefail

PINNED_REPO_URL="https://github.com/Memories-ai-labs/video-sourcing-agent.git"
PINNED_TAG="v0.2.3"

OPENCLAW_HOME_DIR="${OPENCLAW_HOME:-${HOME}/.openclaw}"
MANAGED_BASE_DIR="${OPENCLAW_HOME_DIR}/data/video-sourcing-agent"
MANAGED_RELEASE_DIR="${MANAGED_BASE_DIR}/${PINNED_TAG}"
LOCK_DIR="${MANAGED_RELEASE_DIR}.lock"
BOOTSTRAP_MARKER="${MANAGED_RELEASE_DIR}/.openclaw_bootstrap_complete"

log_error() {
  echo "$1" >&2
}

require_binary() {
  local bin_name="$1"
  if ! command -v "${bin_name}" >/dev/null 2>&1; then
    log_error "Required binary not found on PATH: ${bin_name}"
    exit 2
  fi
}

require_env_key() {
  local env_key="$1"
  if [[ -z "${!env_key:-}" ]]; then
    log_error "Required environment variable is not set: ${env_key}"
    log_error "Set it in OpenClaw global env vars before running /video_sourcing."
    exit 2
  fi
}

acquire_lock() {
  mkdir -p "${MANAGED_BASE_DIR}"
  local wait_seconds=0
  local max_wait_seconds=180
  while ! mkdir "${LOCK_DIR}" 2>/dev/null; do
    sleep 1
    wait_seconds=$((wait_seconds + 1))
    if (( wait_seconds >= max_wait_seconds )); then
      log_error "Timed out waiting for bootstrap lock at ${LOCK_DIR}"
      log_error "If no install is running, remove the lock directory and retry."
      exit 2
    fi
  done
  trap 'rmdir "${LOCK_DIR}" >/dev/null 2>&1 || true' EXIT
}

bootstrap_managed_runtime() {
  require_binary git
  require_binary uv

  mkdir -p "${MANAGED_BASE_DIR}"

  if [[ -d "${MANAGED_RELEASE_DIR}" && ! -d "${MANAGED_RELEASE_DIR}/.git" ]]; then
    rm -rf "${MANAGED_RELEASE_DIR}"
  fi

  if [[ ! -d "${MANAGED_RELEASE_DIR}/.git" ]]; then
    git clone --depth 1 --branch "${PINNED_TAG}" "${PINNED_REPO_URL}" "${MANAGED_RELEASE_DIR}" \
      >/dev/null 2>&1 || {
      log_error "Failed to clone ${PINNED_REPO_URL} at tag ${PINNED_TAG}."
      log_error "Check network access and that the release tag exists."
      exit 2
    }
  else
    (
      cd "${MANAGED_RELEASE_DIR}"
      git fetch --depth 1 origin "refs/tags/${PINNED_TAG}:refs/tags/${PINNED_TAG}" >/dev/null 2>&1 || true
      git checkout --detach "${PINNED_TAG}" >/dev/null 2>&1 || {
        log_error "Failed to checkout pinned runtime tag ${PINNED_TAG}."
        exit 2
      }
    )
  fi

  (
    cd "${MANAGED_RELEASE_DIR}"
    uv sync --frozen --no-dev >/dev/null 2>&1 || {
      log_error "Failed to install runtime dependencies with uv sync."
      exit 2
    }
  )
}

resolve_runtime_root() {
  if [[ -n "${VIDEO_SOURCING_AGENT_ROOT:-}" ]]; then
    if [[ ! -d "${VIDEO_SOURCING_AGENT_ROOT}" ]]; then
      log_error "VIDEO_SOURCING_AGENT_ROOT does not point to a directory: ${VIDEO_SOURCING_AGENT_ROOT}"
      exit 2
    fi
    echo "${VIDEO_SOURCING_AGENT_ROOT}"
    return 0
  fi

  if [[ -f "${BOOTSTRAP_MARKER}" && ! -f "${MANAGED_RELEASE_DIR}/pyproject.toml" ]]; then
    log_error "Managed runtime is incomplete at ${MANAGED_RELEASE_DIR}; reinitializing."
    rm -f "${BOOTSTRAP_MARKER}" || true
  fi

  if [[ ! -f "${BOOTSTRAP_MARKER}" ]]; then
    acquire_lock
    if [[ ! -f "${BOOTSTRAP_MARKER}" ]]; then
      bootstrap_managed_runtime
      if ! : > "${BOOTSTRAP_MARKER}"; then
        log_error "Failed to create bootstrap marker at ${BOOTSTRAP_MARKER}"
        exit 2
      fi
    fi
  fi

  echo "${MANAGED_RELEASE_DIR}"
}

main() {
  require_binary uv
  require_env_key GOOGLE_API_KEY
  require_env_key YOUTUBE_API_KEY

  RUNTIME_ROOT="$(resolve_runtime_root)"
  cd "${RUNTIME_ROOT}"

  uv run python -m video_sourcing_agent.integrations.openclaw_runner "$@"
}

main "$@"
