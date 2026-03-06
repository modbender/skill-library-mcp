#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  azion-deploy.sh preflight [--token TOKEN]
  azion-deploy.sh auth-check [--token TOKEN]
  azion-deploy.sh quickstart --name NAME [--preset static] [--token TOKEN]
  azion-deploy.sh deploy-local [--skip-build] [--auto] [--token TOKEN]

Notes:
- Requires azion CLI installed and available in PATH.
- TOKEN can be passed with --token or env AZION_TOKEN.
EOF
}

require_bin() {
  local b="$1"
  if ! command -v "$b" >/dev/null 2>&1; then
    echo "[ERROR] Missing required executable: $b"
    echo "Install Azion CLI first, then retry. See references/azion-cli.md"
    exit 2
  fi
}

token_arg() {
  local t="${1:-${AZION_TOKEN:-}}"
  if [[ -n "$t" ]]; then
    printf -- "--token %q" "$t"
  fi
}

run_whoami() {
  local token="${1:-${AZION_TOKEN:-}}"
  if [[ -n "$token" ]]; then
    azion whoami --token "$token"
  else
    azion whoami
  fi
}

cmd_preflight() {
  local token="${1:-${AZION_TOKEN:-}}"
  require_bin azion
  local az_ver
  az_ver="$(azion --version 2>&1 | grep -E 'Azion CLI [0-9]+' | head -n1 || true)"
  [[ -z "$az_ver" ]] && az_ver="$(azion --version 2>&1 | head -n1)"
  echo "[OK] azion: $az_ver"
  if run_whoami "$token" >/dev/null 2>&1; then
    echo "[OK] Authenticated (azion whoami)"
  else
    echo "[WARN] Not authenticated. Run: azion login"
    if [[ -n "$token" ]]; then
      echo "[INFO] Token was provided but whoami failed; verify token scope/validity."
    fi
    exit 3
  fi
}

cmd_auth_check() {
  local token="${1:-${AZION_TOKEN:-}}"
  require_bin azion
  run_whoami "$token"
}

cmd_quickstart() {
  local name=""
  local preset="static"
  local token="${AZION_TOKEN:-}"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name) name="$2"; shift 2;;
      --preset) preset="$2"; shift 2;;
      --token) token="$2"; shift 2;;
      *) echo "Unknown arg: $1"; usage; exit 1;;
    esac
  done

  [[ -n "$name" ]] || { echo "[ERROR] --name is required"; exit 1; }

  cmd_preflight "$token"
  local common_args=()
  [[ -n "$token" ]] && common_args+=(--token "$token")

  azion link --auto --name "$name" --preset "$preset" "${common_args[@]}"
  azion build "${common_args[@]}"
  azion deploy --local --skip-build --auto "${common_args[@]}"
}

cmd_deploy_local() {
  local skip_build="false"
  local auto="false"
  local token="${AZION_TOKEN:-}"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --skip-build) skip_build="true"; shift;;
      --auto) auto="true"; shift;;
      --token) token="$2"; shift 2;;
      *) echo "Unknown arg: $1"; usage; exit 1;;
    esac
  done

  cmd_preflight "$token"

  if [[ "$skip_build" != "true" ]]; then
    azion build ${token:+--token "$token"}
  else
    test -f .edge/manifest.json || { echo "[ERROR] .edge/manifest.json missing. Run build first or remove --skip-build"; exit 4; }
  fi

  local deploy_args=(--local)
  [[ "$auto" == "true" ]] && deploy_args+=(--auto)
  [[ "$skip_build" == "true" ]] && deploy_args+=(--skip-build)
  [[ -n "$token" ]] && deploy_args+=(--token "$token")

  azion deploy "${deploy_args[@]}"
}

main() {
  local sub="${1:-}"
  shift || true

  case "$sub" in
    preflight)
      local token=""
      if [[ "${1:-}" == "--token" ]]; then token="${2:-}"; fi
      cmd_preflight "$token"
      ;;
    auth-check)
      local token=""
      if [[ "${1:-}" == "--token" ]]; then token="${2:-}"; fi
      cmd_auth_check "$token"
      ;;
    quickstart) cmd_quickstart "$@" ;;
    deploy-local) cmd_deploy_local "$@" ;;
    ""|-h|--help|help) usage ;;
    *) echo "Unknown command: $sub"; usage; exit 1 ;;
  esac
}

main "$@"
