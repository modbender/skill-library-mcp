#!/usr/bin/env bash
# Revert installer-managed changes where possible.
set -euo pipefail
IFS=$'\n\t'

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_SH="${SKILL_DIR}/lib/common.sh"
if [ -f "${COMMON_SH}" ]; then
  # shellcheck source=/dev/null
  source "${COMMON_SH}"
fi

OPENCLAW_DIR="${HOME}/.openclaw"
CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-${OPENCLAW_DIR}/openclaw.json}"
RESTART_GATEWAY="no" # yes|no
UNINSTALL_WATCHDOG="yes" # yes|no

usage() {
  cat <<'EOF'
Usage:
  uninstall.sh [options]

Options:
  --openclaw-config <path>  OpenClaw config path (default: ~/.openclaw/openclaw.json)
  --restart-gateway <mode>  yes | no (default: no)
  --uninstall-watchdog <m>  yes | no (default: yes)
  --help                    show help
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --openclaw-config) CONFIG_PATH="$2"; shift 2 ;;
    --restart-gateway) RESTART_GATEWAY="$2"; shift 2 ;;
    --uninstall-watchdog) UNINSTALL_WATCHDOG="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

case "$RESTART_GATEWAY" in yes|no) ;; *) echo "Invalid --restart-gateway"; exit 1 ;; esac
case "$UNINSTALL_WATCHDOG" in yes|no) ;; *) echo "Invalid --uninstall-watchdog"; exit 1 ;; esac

echo "Uninstalling ollama-memory-embeddings changes..."

if [ "$UNINSTALL_WATCHDOG" = "yes" ] && [ -x "${SKILL_DIR}/watchdog.sh" ]; then
  if [ "$(uname -s)" = "Darwin" ]; then
    "${SKILL_DIR}/watchdog.sh" --uninstall-launchd || true
  fi
fi

if [ -f "$CONFIG_PATH" ]; then
  latest_backup="$(ls -1t "${CONFIG_PATH}".bak.* 2>/dev/null | head -n1 || true)"
  if [ -n "$latest_backup" ]; then
    cp "$latest_backup" "$CONFIG_PATH"
    echo "Restored config from backup: $latest_backup"
  else
    echo "No config backup found. Leaving config as-is: $CONFIG_PATH"
  fi
else
  echo "Config not found: $CONFIG_PATH"
fi

if [ "$RESTART_GATEWAY" = "yes" ] && command -v openclaw >/dev/null 2>&1; then
  openclaw gateway restart || true
fi

echo "Done."
