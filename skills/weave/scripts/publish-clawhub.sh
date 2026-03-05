#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'EOF'
Usage:
  bash skills/weave/scripts/publish-clawhub.sh <version> [changelog]

Examples:
  bash skills/weave/scripts/publish-clawhub.sh 0.1.0
  bash skills/weave/scripts/publish-clawhub.sh 0.1.1 "Docs-only update for skills.sh listing notes"

Environment variables:
  SKILL_PATH_REL   Repo-relative skill path (default: skills/weave)
  CLAWHUB_CMD      Optional command override, e.g. "npx -y clawhub"
  NPM_CONFIG_CACHE npm cache path used with npx fallback (default: /tmp/npm-cache)
EOF
}

resolve_clawhub_cmd() {
  if [[ -n "${CLAWHUB_CMD:-}" ]]; then
    # shellcheck disable=SC2206
    clawhub_cmd=(${CLAWHUB_CMD})
    return 0
  fi

  if command -v clawhub >/dev/null 2>&1; then
    clawhub_cmd=(clawhub)
    return 0
  fi

  if command -v npx >/dev/null 2>&1; then
    export NPM_CONFIG_CACHE="${NPM_CONFIG_CACHE:-/tmp/npm-cache}"
    clawhub_cmd=(npx -y clawhub)
    return 0
  fi

  echo "Error: neither 'clawhub' nor 'npx' is available on PATH." >&2
  exit 1
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  print_usage
  exit 0
fi

if [[ $# -lt 1 ]]; then
  print_usage
  exit 1
fi

version="$1"
default_changelog="Publish weave skill ${version}: full lifecycle flow docs and runtime-safe token guidance."
changelog="${2:-$default_changelog}"
clawhub_cmd=()
resolve_clawhub_cmd

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/../../.." && pwd)"
skill_path_rel="${SKILL_PATH_REL:-skills/weave}"

(
  cd "${repo_root}"
  echo "Publishing '${skill_path_rel}' with version '${version}' via: ${clawhub_cmd[*]}"
  "${clawhub_cmd[@]}" publish "${skill_path_rel}" --version "${version}" --changelog "${changelog}"
)
