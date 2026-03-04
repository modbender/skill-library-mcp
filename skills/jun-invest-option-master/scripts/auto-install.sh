#!/usr/bin/env bash
set -euo pipefail

# One-shot installer for jun-invest-option-master
# - Ensures the skill is up to date
# - Syncs assets into the isolated agent workspace
# - Registers the isolated agent (id: jun-invest-option-master)
# - Optionally restarts the gateway

WORKSPACE_DIR="/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master"
RESTART_GATEWAY="false"
SKILL_VERSION=""

usage() {
  cat <<'EOF'
Usage:
  bash scripts/auto-install.sh [--workspace <dir>] [--restart-gateway] [--skill-version <ver>]

Defaults:
  --workspace /Users/lijunsheng/.openclaw/workspace-jun-invest-option-master

What it does:
  1) clawhub update jun-invest-option-master (optional --skill-version)
  2) bash scripts/install.sh --workspace <workspace>
  3) openclaw agents add jun-invest-option-master --non-interactive --workspace <workspace>
  4) optionally: openclaw gateway restart
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE_DIR="$2"; shift 2;;
    --restart-gateway)
      RESTART_GATEWAY="true"; shift 1;;
    --skill-version)
      SKILL_VERSION="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage; exit 1;;
  esac
done

if command -v clawhub >/dev/null 2>&1; then
  if [[ -n "${SKILL_VERSION}" ]]; then
    clawhub update jun-invest-option-master --version "${SKILL_VERSION}" --force || true
  else
    clawhub update jun-invest-option-master --force || true
  fi
fi

bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install.sh" --workspace "${WORKSPACE_DIR}"

# Register agent (idempotent: if it already exists, this may error; treat as OK)
openclaw agents add jun-invest-option-master --non-interactive --workspace "${WORKSPACE_DIR}" --json >/dev/null 2>&1 || true

if [[ "${RESTART_GATEWAY}" == "true" ]]; then
  openclaw gateway restart
fi

echo "OK: jun-invest-option-master installed to ${WORKSPACE_DIR}"
