#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'EOF'
Usage:
  bash skills/weave/scripts/check-skills-sh.sh [source] [query]

Defaults:
  source = AryanJ-NYC/weave-cash@weave
  query  = weave cash

Examples:
  bash skills/weave/scripts/check-skills-sh.sh
  bash skills/weave/scripts/check-skills-sh.sh AryanJ-NYC/weave-cash@weave "weave"

Environment variables:
  NPM_CACHE_DIR       npm cache dir used by npx (default: /tmp/npm-cache)
  RUN_INSTALL_CHECK   set to 1 to run an install smoke check (default: 0)
  SKILLS_AGENT        agent name for install smoke check (default: claude-code)
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  print_usage
  exit 0
fi

source_spec="${1:-AryanJ-NYC/weave-cash@weave}"
query="${2:-weave cash}"
npm_cache_dir="${NPM_CACHE_DIR:-/tmp/npm-cache}"
agent_name="${SKILLS_AGENT:-claude-code}"
run_install_check="${RUN_INSTALL_CHECK:-0}"

if ! command -v npx >/dev/null 2>&1; then
  echo "Error: 'npx' is not installed or not on PATH." >&2
  exit 1
fi

echo "Checking skills.sh listing for ${source_spec}..."
npm_config_cache="${npm_cache_dir}" npx -y skills add "${source_spec}" --list

echo "Searching skills index for '${query}'..."
npm_config_cache="${npm_cache_dir}" npx -y skills find "${query}"

if [[ "${run_install_check}" == "1" ]]; then
  echo "Running optional install smoke check for agent '${agent_name}'..."
  npm_config_cache="${npm_cache_dir}" npx -y skills add "${source_spec}" --yes --agent "${agent_name}"
fi

