#!/usr/bin/env bash
# Drift watchdog for OpenClaw memorySearch embeddings config.
set -euo pipefail
IFS=$'\n\t'

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_SH="${SKILL_DIR}/lib/common.sh"
CONFIG_CLI="${SKILL_DIR}/lib/config.js"
if [ ! -f "${COMMON_SH}" ]; then
  echo "[ERROR] Missing shared helper: ${COMMON_SH}" >&2
  exit 1
fi
if [ ! -f "${CONFIG_CLI}" ]; then
  echo "[ERROR] Missing config helper: ${CONFIG_CLI}" >&2
  exit 1
fi
source "${COMMON_SH}"
ENFORCE_SH="${SKILL_DIR}/enforce.sh"
CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-${HOME}/.openclaw/openclaw.json}"
MODEL=""
BASE_URL="http://127.0.0.1:11434/v1/"
INTERVAL_SEC=60
ONCE=0
RESTART_ON_HEAL=0
INSTALL_LAUNCHD=0
UNINSTALL_LAUNCHD=0
QUIET=0

PLIST_NAME="bot.molt.openclaw.embedding-guard"
PLIST_PATH="${HOME}/Library/LaunchAgents/${PLIST_NAME}.plist"
LOG_DIR="${HOME}/.openclaw/logs"
STDOUT_LOG="${LOG_DIR}/embedding-guard.out.log"
STDERR_LOG="${LOG_DIR}/embedding-guard.err.log"

usage() {
  cat <<'EOF'
Usage:
  watchdog.sh [options]

Modes:
  --once                  run one check/heal cycle, then exit
  (default)               run continuously and check every --interval-sec
  --install-launchd       install + load launchd job (macOS)
  --uninstall-launchd     unload + remove launchd job (macOS)

Other OS guidance:
  Linux: run --once via cron/systemd timer
  Windows: not supported (bash script)

Linux cron example (every 5 min):
  */5 * * * * /bin/bash ~/.openclaw/skills/ollama-memory-embeddings/watchdog.sh --once --model embeddinggemma >/dev/null 2>&1

Options:
  --model <id>              model to enforce (required for new installs)
  --base-url <url>          base URL to enforce (default: http://127.0.0.1:11434/v1/)
  --openclaw-config <path>  config path (default: ~/.openclaw/openclaw.json)
  --interval-sec <n>        check interval (default: 60)
  --restart-on-heal         restart gateway after drift heal
  --quiet                   suppress non-error output
  --help                    show help
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --openclaw-config) CONFIG_PATH="$2"; shift 2 ;;
    --interval-sec) INTERVAL_SEC="$2"; shift 2 ;;
    --once) ONCE=1; shift ;;
    --restart-on-heal) RESTART_ON_HEAL=1; shift ;;
    --install-launchd) INSTALL_LAUNCHD=1; shift ;;
    --uninstall-launchd) UNINSTALL_LAUNCHD=1; shift ;;
    --quiet) QUIET=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

resolve_model_if_missing() {
  if [ -n "$MODEL" ]; then
    return 0
  fi
  MODEL="$(node "${CONFIG_CLI}" resolve-model "$CONFIG_PATH")"
  if [ -z "$MODEL" ]; then
    log_err "--model is required (or set memorySearch.model first)."
    exit 1
  fi
}

xml_escape() {
  local s="$1"
  s="${s//&/&amp;}"
  s="${s//</&lt;}"
  s="${s//>/&gt;}"
  s="${s//\"/&quot;}"
  s="${s//\'/&apos;}"
  printf '%s' "$s"
}

reject_newlines() {
  local name="$1"
  local value="$2"
  if [[ "$value" == *$'\n'* ]] || [[ "$value" == *$'\r'* ]]; then
    log_err "$name must not contain newline characters."
    exit 1
  fi
}

run_cycle() {
  set +e
  "$ENFORCE_SH" \
    --check-only \
    --model "$MODEL" \
    --base-url "$BASE_URL" \
    --openclaw-config "$CONFIG_PATH" \
    --quiet
  status=$?
  set -e

  if [ "$status" -eq 0 ]; then
    log_info "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] OK: no drift"
    return 0
  fi
  if [ "$status" -ne 10 ]; then
    log_err "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] drift check failed (status $status)"
    return 1
  fi

  log_warn "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] DRIFT: healing..."
  if [ "$RESTART_ON_HEAL" -eq 1 ]; then
    "$ENFORCE_SH" --model "$MODEL" --base-url "$BASE_URL" --openclaw-config "$CONFIG_PATH" --restart-on-change --quiet
  else
    "$ENFORCE_SH" --model "$MODEL" --base-url "$BASE_URL" --openclaw-config "$CONFIG_PATH" --quiet
  fi
  log_info "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] HEALED"
}

install_launchd() {
  if [ "$(uname)" != "Darwin" ]; then
    log_err "--install-launchd is macOS only."
    echo "Linux recommendation:"
    echo "  Use cron or a systemd timer to run:"
    echo "  /bin/bash ${SKILL_DIR}/watchdog.sh --once --model <model>"
    echo "Windows: not supported (bash script)."
    exit 1
  fi
  require_cmd launchctl
  require_cmd plutil
  require_cmd node
  resolve_model_if_missing
  mkdir -p "$(dirname "$PLIST_PATH")" "$LOG_DIR"
  local shell_bin
  shell_bin="$(command -v bash)"
  reject_newlines "MODEL" "${MODEL}"
  reject_newlines "BASE_URL" "${BASE_URL}"
  reject_newlines "CONFIG_PATH" "${CONFIG_PATH}"
  reject_newlines "STDOUT_LOG" "${STDOUT_LOG}"
  reject_newlines "STDERR_LOG" "${STDERR_LOG}"
  reject_newlines "PLIST_NAME" "${PLIST_NAME}"
  reject_newlines "SKILL_DIR" "${SKILL_DIR}"
  reject_newlines "shell_bin" "${shell_bin}"
  local esc_plist_name esc_shell_bin esc_skill_dir esc_model esc_base_url esc_config_path esc_stdout_log esc_stderr_log
  esc_plist_name="$(xml_escape "${PLIST_NAME}")"
  esc_shell_bin="$(xml_escape "${shell_bin}")"
  esc_skill_dir="$(xml_escape "${SKILL_DIR}")"
  esc_model="$(xml_escape "${MODEL}")"
  esc_base_url="$(xml_escape "${BASE_URL}")"
  esc_config_path="$(xml_escape "${CONFIG_PATH}")"
  esc_stdout_log="$(xml_escape "${STDOUT_LOG}")"
  esc_stderr_log="$(xml_escape "${STDERR_LOG}")"
  local restart_flag_xml=""
  if [ "$RESTART_ON_HEAL" -eq 1 ]; then
    restart_flag_xml="    <string>--restart-on-heal</string>"
  fi
  cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${esc_plist_name}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${esc_shell_bin}</string>
    <string>${esc_skill_dir}/watchdog.sh</string>
    <string>--once</string>
    <string>--model</string>
    <string>${esc_model}</string>
    <string>--base-url</string>
    <string>${esc_base_url}</string>
    <string>--openclaw-config</string>
    <string>${esc_config_path}</string>
${restart_flag_xml}
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>${INTERVAL_SEC}</integer>
  <key>StandardOutPath</key>
  <string>${esc_stdout_log}</string>
  <key>StandardErrorPath</key>
  <string>${esc_stderr_log}</string>
</dict>
</plist>
EOF

  if ! plutil -lint "$PLIST_PATH" >/dev/null 2>&1; then
    log_err "Generated launchd plist is invalid: ${PLIST_PATH}"
    rm -f "$PLIST_PATH"
    exit 1
  fi

  launchctl bootout "gui/$(id -u)/${PLIST_NAME}" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
  launchctl kickstart -k "gui/$(id -u)/${PLIST_NAME}"
  log_info "Installed launchd watchdog: ${PLIST_PATH}"
}

uninstall_launchd() {
  if [ "$(uname)" != "Darwin" ]; then
    log_err "--uninstall-launchd is macOS only."
    echo "Windows: not supported (bash script)."
    exit 1
  fi
  require_cmd launchctl
  launchctl bootout "gui/$(id -u)/${PLIST_NAME}" >/dev/null 2>&1 || true
  rm -f "$PLIST_PATH"
  log_info "Removed launchd watchdog: ${PLIST_PATH}"
}

if [ "$INSTALL_LAUNCHD" -eq 1 ] && [ "$UNINSTALL_LAUNCHD" -eq 1 ]; then
  log_err "choose only one of --install-launchd or --uninstall-launchd."
  exit 1
fi

if [ "$INSTALL_LAUNCHD" -eq 1 ]; then
  install_launchd
  exit 0
fi

if [ "$UNINSTALL_LAUNCHD" -eq 1 ]; then
  uninstall_launchd
  exit 0
fi

require_cmd node
resolve_model_if_missing

if [ "$ONCE" -eq 1 ]; then
  run_cycle
  exit 0
fi

while true; do
  run_cycle || true
  sleep "$INTERVAL_SEC"
done
