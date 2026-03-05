#!/usr/bin/env bash

# Shared shell helpers for ollama-memory-embeddings scripts.

# Optional: LOG_FORMAT=json emits one JSON object per log line (ndjson) to stderr.
# Keys: ts (ISO8601), level (INFO|WARN|ERROR), msg. Enables deterministic parsing in CI/audit.
_log_json() {
  local level="$1"
  shift
  local msg="$*"
  local ts
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%S 2>/dev/null)"
  printf '{"ts":"%s","level":"%s","msg":"%s"}\n' "$ts" "$level" "${msg//\"/\\\"}" >&2
}

log_info() {
  local quiet="${QUIET:-0}"
  [ "$quiet" -eq 1 ] && return 0
  if [ "${LOG_FORMAT:-}" = "json" ]; then
    _log_json "INFO" "$@"
  else
    echo "[INFO] $*"
  fi
}

log_warn() {
  local quiet="${QUIET:-0}"
  [ "$quiet" -eq 1 ] && return 0
  if [ "${LOG_FORMAT:-}" = "json" ]; then
    _log_json "WARN" "$@"
  else
    echo "[WARN] $*"
  fi
}

log_err() {
  if [ "${LOG_FORMAT:-}" = "json" ]; then
    _log_json "ERROR" "$@"
  else
    echo "[ERROR] $*" >&2
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    log_err "'$1' not found in PATH."
    exit 1
  }
}

normalize_model() {
  local m="$1"
  if [[ "$m" != *:* ]]; then
    echo "${m}:latest"
  else
    echo "$m"
  fi
}

normalize_base_url() {
  local u="${1%/}"
  if [[ "$u" != */v1 ]]; then
    u="${u}/v1"
  fi
  echo "${u}/"
}
