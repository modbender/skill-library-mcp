#!/usr/bin/env bash
set -euo pipefail

# Agent workspace directory (recommended: /Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent)
WORKSPACE=""
TARGET_DIR_NAME=""

usage() {
  cat <<'EOF'
Usage:
  bash scripts/doctor.sh --workspace <OPENCLAW_WORKSPACE_PATH> [--target-name jun_invest_option_master]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE="$2"; shift 2;;
    --target-name)
      TARGET_DIR_NAME="$2"; shift 2;;
    -h|--help)
      usage; exit 0;;
    *)
      echo "Unknown arg: $1" >&2
      usage; exit 1;;
  esac
done

[[ -n "${WORKSPACE}" ]] || { echo "Missing --workspace" >&2; usage; exit 1; }

# If target-name is empty, doctor checks WORKSPACE directly.
if [[ -z "${TARGET_DIR_NAME}" ]]; then
  DST_DIR="${WORKSPACE}"
else
  DST_DIR="${WORKSPACE}/${TARGET_DIR_NAME}"
fi

echo "Workspace: ${WORKSPACE}"
[[ -d "${WORKSPACE}" ]] || { echo "FAIL: workspace not found"; exit 1; }

echo "Agent dir: ${DST_DIR}"
[[ -d "${DST_DIR}" ]] || { echo "FAIL: agent dir not found"; exit 1; }

req=(
  "config/policy.yaml"
  "config/agents.yaml"
  "prompts"
  "templates/approval_packet.md"
)

for r in "${req[@]}"; do
  [[ -e "${DST_DIR}/${r}" ]] || { echo "FAIL: missing ${r}"; exit 1; }
done

echo "OK: required files present"
