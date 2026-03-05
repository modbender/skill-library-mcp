#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  vault.sh put <secret-name>      # read secret from stdin and store
  vault.sh get <secret-name>      # print secret to stdout
  vault.sh ls                     # list secret names
  vault.sh exists <secret-name>   # exit 0 if exists
  vault.sh rm <secret-name>       # remove secret
EOF
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

validate_secret_name() {
  local value="$1"
  if [ -z "$value" ]; then
    echo "Secret name is required" >&2
    exit 1
  fi
  if [[ "$value" == -* ]]; then
    echo "Secret name must not start with '-'" >&2
    exit 1
  fi
  if [[ ! "$value" =~ ^[A-Za-z0-9._/-]+$ ]]; then
    echo "Secret name contains invalid characters" >&2
    exit 1
  fi
  if [[ "$value" == *".."* ]] || [[ "$value" == *"//"* ]]; then
    echo "Secret name contains invalid path traversal pattern" >&2
    exit 1
  fi
  if [[ "$value" == /* ]] || [[ "$value" == */ ]]; then
    echo "Secret name must not start or end with '/'" >&2
    exit 1
  fi
}

if [ "${1:-}" = "" ]; then
  usage
  exit 1
fi

cmd="$1"
name="${2:-}"

if [ "$cmd" = "-h" ] || [ "$cmd" = "--help" ]; then
  usage
  exit 0
fi

require_cmd pass

if [ "$cmd" != "ls" ] && [ -z "$name" ]; then
  usage
  exit 1
fi

if [ "$cmd" != "ls" ]; then
  validate_secret_name "$name"
fi

case "$cmd" in
  put)
    # Read exactly from stdin and write as multiline secret.
    pass insert -m -f -- "$name" >/dev/null
    ;;
  get)
    pass show -- "$name"
    ;;
  ls)
    pass ls
    ;;
  exists)
    pass show -- "$name" >/dev/null 2>&1
    ;;
  rm)
    pass rm -f -- "$name" >/dev/null
    ;;
  *)
    usage
    exit 1
    ;;
esac
