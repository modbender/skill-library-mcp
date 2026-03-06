#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  run_with_secret.sh --secret <name> --env <ENV_NAME> -- <command> [args...]

Example:
  run_with_secret.sh --secret github/token --env GITHUB_TOKEN -- gh api user
EOF
}

secret_name=""
env_name=""
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
vault_script="${script_dir}/vault.sh"

while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --secret)
      secret_name="${2:-}"
      shift 2
      ;;
    --env)
      env_name="${2:-}"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [ -z "$secret_name" ] || [ -z "$env_name" ] || [ $# -eq 0 ]; then
  usage
  exit 1
fi

if [[ ! "$env_name" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
  echo "Invalid env var name: $env_name" >&2
  exit 1
fi

if [ ! -x "$vault_script" ]; then
  echo "Missing executable vault script: $vault_script" >&2
  exit 1
fi

if ! secret_value="$("$vault_script" get "$secret_name")"; then
  echo "Failed to read secret: $secret_name" >&2
  exit 1
fi

exec env "$env_name=$secret_value" "$@"
