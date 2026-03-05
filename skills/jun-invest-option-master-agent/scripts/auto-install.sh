#!/usr/bin/env bash
set -euo pipefail

# One-shot installer for jun-invest-option-master-agent
# - Ensures THIS skill is up to date (latest)
# - Creates runtime workspace (first install)
# - Sets up runtime git + commit-triggered sync to artifact
# - Registers the isolated agent (id: jun-invest-option-master-agent)

WORKSPACE_DIR="/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent"
RESTART_GATEWAY="false"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/auto-install.sh [--workspace <dir>] [--restart-gateway]

Defaults:
  --workspace /Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent

What it does:
  1) clawhub update jun-invest-option-master-agent --force   (always latest)
  2) bash scripts/install.sh --workspace <workspace>
  3) bash scripts/setup-runtime-git.sh  (commit-triggered sync)
  4) openclaw agents add jun-invest-option-master-agent --non-interactive --workspace <workspace>
  5) optionally: openclaw gateway restart
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE_DIR="$2"; shift 2;;
    --restart-gateway)
      RESTART_GATEWAY="true"; shift 1;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage; exit 1;;
  esac
done

if command -v clawhub >/dev/null 2>&1; then
  clawhub update jun-invest-option-master-agent --force || true
fi

bash "$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)/install.sh" --workspace "${WORKSPACE_DIR}"

bash "$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)/setup-runtime-git.sh" || true

# Setup unattended daily publish (macOS launchd; best-effort)
if [[ "$(uname -s)" == "Darwin" ]]; then
  bash "$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)/setup-launchd.sh" || true
fi

openclaw agents add jun-invest-option-master-agent --non-interactive --workspace "${WORKSPACE_DIR}" --json >/dev/null 2>&1 || true

if [[ "${RESTART_GATEWAY}" == "true" ]]; then
  openclaw gateway restart
fi

echo "OK: jun-invest-option-master-agent installed to ${WORKSPACE_DIR}"
