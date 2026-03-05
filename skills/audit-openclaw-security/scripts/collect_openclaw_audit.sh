#!/usr/bin/env bash
set -euo pipefail

# Collects defensive, mostly read-only diagnostics for an OpenClaw security audit.
# It does NOT run any --fix operations.
#
# Usage:
#   bash scripts/collect_openclaw_audit.sh --out ./openclaw-audit
#
# Safety notes:
# - Review outputs before sharing them externally. While the chosen OpenClaw commands are
#   intended to redact secrets, some files may still contain environment details or PII.
# - This script avoids copying credential files; it only runs status/audit/snapshot commands
#   plus basic host/network inspection.

OUT_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "${OUT_DIR}" ]]; then
  echo "Missing --out <dir>" >&2
  exit 2
fi

TS="$(date -u +"%Y%m%dT%H%M%SZ")"
ROOT="${OUT_DIR%/}/openclaw-audit-${TS}"
mkdir -p "${ROOT}"

log() { echo "[collect] $*"; }

run_cmd() {
  local name="$1"; shift
  local file="${ROOT}/${name}.txt"
  log "Running: $*"
  {
    echo "$ $*"
    "$@"
  } > "${file}" 2>&1 || {
    echo "[warn] command failed (continuing): $*" >> "${file}"
    return 0
  }
}

run_cmd_maybe_sudo() {
  local name="$1"; shift
  local file="${ROOT}/${name}.txt"
  if command -v sudo >/dev/null 2>&1; then
    log "Running (sudo -n): $*"
    {
      echo "$ sudo -n $*"
      sudo -n "$@"
    } > "${file}" 2>&1 || {
      echo "[info] sudo not available without password (skipped): $*" >> "${file}"
      return 0
    }
  else
    echo "[info] sudo not installed; skipped: $*" > "${file}"
  fi
}

# Basic host info
run_cmd "host_whoami" whoami
run_cmd "host_uname" uname -a

if command -v sw_vers >/dev/null 2>&1; then
  run_cmd "host_sw_vers" sw_vers
  # macOS firewall (read-only)
  if [[ -x /usr/libexec/ApplicationFirewall/socketfilterfw ]]; then
    run_cmd "macos_firewall_state" /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
    run_cmd "macos_firewall_stealth" /usr/libexec/ApplicationFirewall/socketfilterfw --getstealthmode
  fi
  run_cmd "macos_filevault" fdesetup status || true
fi
if [[ -f /etc/os-release ]]; then
  run_cmd "host_os_release" cat /etc/os-release
fi

# OpenClaw info
if ! command -v openclaw >/dev/null 2>&1; then
  echo "openclaw not found on PATH" > "${ROOT}/openclaw_missing.txt"
  log "openclaw missing; collected host info only"
  exit 0
fi

run_cmd "openclaw_version" openclaw --version
run_cmd "openclaw_status_all" openclaw status --all
run_cmd "openclaw_doctor" openclaw doctor
run_cmd "openclaw_gateway_status" openclaw gateway status
run_cmd "openclaw_health_json" openclaw health --json
run_cmd "openclaw_security_audit_json" openclaw security audit --json
run_cmd "openclaw_security_audit_deep_json" openclaw security audit --deep --json

# Supply-chain visibility (no secrets)
run_cmd "openclaw_skills_eligible_json" openclaw skills list --eligible --json
run_cmd "openclaw_plugins_list_json" openclaw plugins list --json

# Network listeners (best-effort)
if command -v lsof >/dev/null 2>&1; then
  run_cmd "net_lsof_listen" lsof -nP -iTCP -sTCP:LISTEN
elif command -v ss >/dev/null 2>&1; then
  run_cmd "net_ss_listen" ss -ltnp
elif command -v netstat >/dev/null 2>&1; then
  run_cmd "net_netstat_listen" netstat -anv | head -n 2000
fi

# Linux firewall snapshot (best-effort, non-interactive)
if [[ -f /etc/os-release ]]; then
  run_cmd_maybe_sudo "linux_ufw_status" ufw status verbose
  run_cmd_maybe_sudo "linux_nft_ruleset" nft list ruleset
  run_cmd_maybe_sudo "linux_iptables_rules" iptables -S
fi

# OpenClaw state dir perms (do not copy secrets; just record metadata)
STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
if [[ -d "${STATE_DIR}" ]]; then
  run_cmd "openclaw_state_ls" ls -la "${STATE_DIR}"
  if command -v stat >/dev/null 2>&1; then
    # config path may differ; best-effort
    run_cmd "openclaw_state_stat" stat "${STATE_DIR}" "${STATE_DIR}/openclaw.json" 2>/dev/null || true
  fi
fi

log "Done. Output: ${ROOT}"
