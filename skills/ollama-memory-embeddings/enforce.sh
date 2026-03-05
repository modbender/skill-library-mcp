#!/usr/bin/env bash
# Enforce OpenClaw memorySearch to use Ollama embeddings settings.
# Idempotent: safe to run repeatedly.
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_SH="${SCRIPT_DIR}/lib/common.sh"
CONFIG_CLI="${SCRIPT_DIR}/lib/config.js"
if [ ! -f "${COMMON_SH}" ]; then
  echo "[ERROR] Missing shared helper: ${COMMON_SH}" >&2
  exit 1
fi
if [ ! -f "${CONFIG_CLI}" ]; then
  echo "[ERROR] Missing config helper: ${CONFIG_CLI}" >&2
  exit 1
fi
source "${COMMON_SH}"

MODEL=""
BASE_URL="http://127.0.0.1:11434/v1/"
CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-${HOME}/.openclaw/openclaw.json}"
CHECK_ONLY=0
QUIET=0
RESTART_ON_CHANGE=0
API_KEY_VALUE="ollama"
LOCK_TIMEOUT_SEC="${OPENCLAW_LOCK_TIMEOUT_SEC:-30}"
LOCK_STALE_SEC="${OPENCLAW_LOCK_STALE_SEC:-600}"
LOCK_DIR=""
LOCK_HELD=0

usage() {
  cat <<'EOF'
Usage:
  enforce.sh [options]

Options:
  --model <id>              embedding model id (required unless already in config)
  --base-url <url>          Ollama OpenAI-compatible base URL (default: http://127.0.0.1:11434/v1/)
  --openclaw-config <path>  OpenClaw config path (default: ~/.openclaw/openclaw.json)
  --api-key-value <value>   apiKey to set if missing (default: ollama)
  --check-only              exit non-zero if drift is detected, do not modify config
  --restart-on-change       restart gateway if config was changed
  --quiet                   suppress non-error output
  --help                    show help

Exit codes:
  0  success (no drift or drift healed)
  10 drift detected in --check-only mode
  1  error
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --openclaw-config) CONFIG_PATH="$2"; shift 2 ;;
    --api-key-value) API_KEY_VALUE="$2"; shift 2 ;;
    --check-only) CHECK_ONLY=1; shift ;;
    --restart-on-change) RESTART_ON_CHANGE=1; shift ;;
    --quiet) QUIET=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

restart_gateway() {
  if ! command -v openclaw >/dev/null 2>&1; then
    log_info "openclaw CLI not found; skip restart."
    return 0
  fi
  if openclaw gateway restart 2>/dev/null; then
    log_info "Gateway restarted."
    return 0
  fi
  log_warn "openclaw gateway restart failed; restart manually."
  return 1
}

require_cmd node

mkdir -p "$(dirname "$CONFIG_PATH")"
[ -f "$CONFIG_PATH" ] || echo "{}" > "$CONFIG_PATH"

BASE_URL_NORM="$(normalize_base_url "$BASE_URL")"

release_lock() {
  if [ "${LOCK_HELD}" -eq 1 ] && [ -n "${LOCK_DIR}" ] && [ -d "${LOCK_DIR}" ]; then
    rm -rf "${LOCK_DIR}" || true
  fi
  LOCK_HELD=0
}
trap release_lock EXIT INT TERM

acquire_lock() {
  LOCK_DIR="${CONFIG_PATH}.lock"
  local start_epoch now_epoch waited lock_started lock_pid lock_age
  start_epoch="$(date +%s)"
  while ! mkdir "${LOCK_DIR}" 2>/dev/null; do
    now_epoch="$(date +%s)"
    waited=$((now_epoch - start_epoch))
    if [ "${waited}" -ge "${LOCK_TIMEOUT_SEC}" ]; then
      log_err "Timed out waiting for lock: ${LOCK_DIR} (waited ${LOCK_TIMEOUT_SEC}s)"
      return 1
    fi

    lock_started=""
    lock_pid=""
    if [ -f "${LOCK_DIR}/meta" ]; then
      lock_started="$(awk -F= '/^started_epoch=/{print $2}' "${LOCK_DIR}/meta" 2>/dev/null || true)"
      lock_pid="$(awk -F= '/^pid=/{print $2}' "${LOCK_DIR}/meta" 2>/dev/null || true)"
    fi
    lock_age=0
    if [ -n "${lock_started}" ] 2>/dev/null; then
      lock_age=$((now_epoch - lock_started))
    fi

    # Stale lock recovery: timed out lock or dead PID.
    if [ "${lock_age}" -ge "${LOCK_STALE_SEC}" ] || { [ -n "${lock_pid}" ] && ! kill -0 "${lock_pid}" 2>/dev/null; }; then
      log_warn "Recovering stale lock at ${LOCK_DIR}"
      rm -rf "${LOCK_DIR}" || true
      continue
    fi
    sleep 1
  done

  {
    printf 'pid=%s\n' "$$"
    printf 'started_epoch=%s\n' "$(date +%s)"
    printf 'started_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'host=%s\n' "$(hostname 2>/dev/null || echo unknown)"
  } > "${LOCK_DIR}/meta"
  LOCK_HELD=1
}

# If model omitted, try current config model; otherwise enforce requires explicit model.
if [ -z "$MODEL" ]; then
  MODEL="$(node "${CONFIG_CLI}" resolve-model "$CONFIG_PATH")"
fi

if [ -z "$MODEL" ]; then
  echo "ERROR: no model provided and no existing memorySearch.model in config."
  exit 1
fi
MODEL_NORM="$(normalize_model "$MODEL")"
if [ -z "$API_KEY_VALUE" ]; then
  echo "ERROR: --api-key-value must be non-empty."
  exit 1
fi

export CONFIG_PATH MODEL_NORM BASE_URL_NORM API_KEY_VALUE
if [ "$CHECK_ONLY" -eq 1 ]; then
  set +e
  node "${CONFIG_CLI}" check-drift "${CONFIG_PATH}" "${MODEL_NORM}" "${BASE_URL_NORM}"
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    log_info "No drift detected."
    exit 0
  elif [ "$status" -eq 10 ]; then
    log_info "Drift detected."
    exit 10
  else
    log_err "drift check failed."
    exit 1
  fi
fi

if ! acquire_lock; then
  exit 1
fi

set +e
PLAN_OUT="$(node "${CONFIG_CLI}" plan-enforce "${CONFIG_PATH}" "${MODEL_NORM}" "${BASE_URL_NORM}" "${API_KEY_VALUE}")"
status=$?
set -e

if [ "$status" -ne 0 ]; then
  log_err "failed to plan memorySearch enforcement."
  exit 1
fi

CHANGED="$(printf "%s\n" "$PLAN_OUT" | sed -n '1p')"
PROVIDER_NOW="$(printf "%s\n" "$PLAN_OUT" | sed -n '2p')"
MODEL_NOW="$(printf "%s\n" "$PLAN_OUT" | sed -n '3p')"
BASE_NOW="$(printf "%s\n" "$PLAN_OUT" | sed -n '4p')"
APIKEY_NOW="$(printf "%s\n" "$PLAN_OUT" | sed -n '5p')"
ACTIVE_PATH="$(printf "%s\n" "$PLAN_OUT" | sed -n '6p')"
MIRRORING_LEGACY="$(printf "%s\n" "$PLAN_OUT" | sed -n '7p')"

if [ "$CHANGED" = "changed" ]; then
  BACKUP_PATH="${CONFIG_PATH}.bak.$(date -u +%Y-%m-%dT%H-%M-%SZ)"
  cp "$CONFIG_PATH" "$BACKUP_PATH"
  node "${CONFIG_CLI}" apply-enforce "${CONFIG_PATH}" "${MODEL_NORM}" "${BASE_URL_NORM}" "${API_KEY_VALUE}"
fi

log_info "Config: ${CONFIG_PATH}"
if [ "$CHANGED" = "changed" ]; then
  log_info "Backup: ${BACKUP_PATH}"
fi
log_info "provider=${PROVIDER_NOW}"
log_info "model=${MODEL_NOW}"
log_info "baseUrl=${BASE_NOW}"
log_info "apiKey=${APIKEY_NOW}"
if [ -n "$ACTIVE_PATH" ] && [ "$ACTIVE_PATH" != "agents.defaults.memorySearch" ]; then
  log_info "legacyPathDetected=${ACTIVE_PATH}"
fi
if [ "$MIRRORING_LEGACY" = "yes" ]; then
  log_info "legacyMirrored=yes"
fi

if [ "$CHANGED" = "changed" ]; then
  log_info "Drift healed: memorySearch settings updated."
  if [ "$RESTART_ON_CHANGE" -eq 1 ]; then
    restart_gateway || true
  fi
else
  log_info "No changes required."
fi
