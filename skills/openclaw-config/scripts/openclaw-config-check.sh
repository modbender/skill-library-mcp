#!/usr/bin/env bash
set -euo pipefail

resolve_config_path() {
  if [[ -n "${OPENCLAW_CONFIG_PATH:-}" ]]; then
    echo "${OPENCLAW_CONFIG_PATH}"
    return 0
  fi

  local state_dir
  state_dir="${OPENCLAW_STATE_DIR:-${CLAWDBOT_STATE_DIR:-$HOME/.openclaw}}"
  echo "${state_dir%/}/openclaw.json"
}

resolve_mode() {
  if [[ -n "${OPENCLAW_CONFIG_PATH:-}" ]]; then
    echo "OPENCLAW_CONFIG_PATH"
    return 0
  fi
  if [[ -n "${OPENCLAW_STATE_DIR:-}" || -n "${CLAWDBOT_STATE_DIR:-}" ]]; then
    echo "OPENCLAW_STATE_DIR"
    return 0
  fi
  echo "default"
}

CONFIG_PATH="$(resolve_config_path)"
MODE="$(resolve_mode)"

echo "Config path (${MODE}): ${CONFIG_PATH}"

if [[ -f "${CONFIG_PATH}" ]]; then
  echo
  echo "Config file:"
  ls -la "${CONFIG_PATH}"

  # Permissions check (macOS + Linux)
  perms=""
  if perms="$(stat -f '%A' "${CONFIG_PATH}" 2>/dev/null)"; then
    :
  elif perms="$(stat -c '%a' "${CONFIG_PATH}" 2>/dev/null)"; then
    :
  else
    perms=""
  fi
  if [[ -n "${perms}" ]]; then
    echo "Permissions: ${perms}"
    if [[ "${perms}" =~ ^[0-9]+$ ]] && (( perms > 600 )); then
      echo "WARNING: config perms are >600; consider: chmod 600 \"${CONFIG_PATH}\""
    fi
  fi
else
  echo "Config file does not exist."
fi

echo
if command -v openclaw >/dev/null 2>&1; then
  echo "Running: openclaw doctor"
  openclaw doctor
else
  echo "openclaw CLI not found in PATH; skipping: openclaw doctor"
fi

