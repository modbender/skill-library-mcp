#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  dex-agent.sh doctor
  dex-agent.sh install
  dex-agent.sh balance [--json]
  dex-agent.sh order [order options...]
  dex-agent.sh backend <command> [options...]
  dex-agent.sh watch [--channel <name> | --channels <csv>] [--json]
  dex-agent.sh autotrade [autotrade options...]
  dex-agent.sh onboard [onboarding options...]
  dex-agent.sh help

Examples:
  dex-agent.sh balance
  dex-agent.sh order --market-id 1 --side buy --type market --margin 1000000
  dex-agent.sh backend positions --mine --limit 20
  dex-agent.sh watch --channel agent.signals
  dex-agent.sh autotrade --market-id 1 --margin 1000000 --min-confidence 0.75
  dex-agent.sh onboard --market-id 1 --margin 1000000
EOF
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[error] required command not found: $1" >&2
    exit 1
  fi
}

ensure_skill_dir() {
  if [ ! -d "${SKILL_DIR}" ]; then
    echo "[error] skill directory not found: ${SKILL_DIR}" >&2
    exit 1
  fi
}

install_deps() {
  ensure_skill_dir
  require_cmd npm
  if [ ! -d "${SKILL_DIR}/node_modules" ]; then
    echo "[info] installing npm dependencies in ${SKILL_DIR}"
    (cd "${SKILL_DIR}" && npm install)
  fi
}

run_local_script() {
  local script_rel="$1"
  shift || true
  ensure_skill_dir
  install_deps
  require_cmd node
  (
    cd "${SKILL_DIR}"
    node "${script_rel}" "$@"
  )
}

doctor() {
  echo "skill_dir=${SKILL_DIR}"
  for cmd in node npm solana; do
    if command -v "${cmd}" >/dev/null 2>&1; then
      echo "[ok] ${cmd}: $(command -v "${cmd}")"
    else
      echo "[warn] ${cmd}: missing"
    fi
  done

  local api_base="${EASYCLAW_API_BASE_URL:-${API_BASE_URL:-http://127.0.0.1:8080}}"
  local ws_url="${EASYCLAW_WS_URL:-${BACKEND_WS_URL:-}}"
  if [ -z "${ws_url}" ]; then
    ws_url="${api_base/http:\/\//ws://}"
    ws_url="${ws_url/https:\/\//wss://}"
    ws_url="${ws_url%/}/ws"
  fi
  echo "[info] api_base=${api_base}"
  echo "[info] ws_url=${ws_url}"
}

balance() {
  run_local_script "scripts/balance.js" "$@"
}

order_execute() {
  run_local_script "scripts/order-execute.js" "$@"
}

backend_api() {
  run_local_script "scripts/backend.js" "$@"
}

watch_stream() {
  run_local_script "scripts/ws-watch.js" "$@"
}

autotrade() {
  run_local_script "scripts/realtime-agent.js" "$@"
}

onboard() {
  run_local_script "scripts/onboard.js" "$@"
}

main() {
  local cmd="${1:-help}"
  shift || true

  case "${cmd}" in
    doctor)
      doctor
      ;;
    install)
      install_deps
      ;;
    balance)
      balance "$@"
      ;;
    order)
      order_execute "$@"
      ;;
    backend)
      backend_api "$@"
      ;;
    watch)
      watch_stream "$@"
      ;;
    autotrade)
      autotrade "$@"
      ;;
    onboard)
      onboard "$@"
      ;;
    help|-h|--help)
      usage
      ;;
    *)
      echo "[error] unknown command: ${cmd}" >&2
      usage
      exit 1
      ;;
  esac
}

main "$@"
