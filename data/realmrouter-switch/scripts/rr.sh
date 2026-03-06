#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/realm_manager.py"

cmd="${1:-help}"
shift || true

case "$cmd" in
  init)
    model="${1:-qwen3-max}"
    python3 "$PY" install --default-model "$model" --restart-gateway
    ;;
  key|k)
    key="${1:-}"
    if [[ -z "$key" ]]; then
      echo "Usage: rr key <api-key>" >&2
      exit 1
    fi
    python3 "$PY" set-key --api-key "$key" --restart-gateway
    ;;
  use|m)
    model="${1:-}"
    if [[ -z "$model" ]]; then
      echo "Usage: rr use <model-id|alias|index>" >&2
      exit 1
    fi
    python3 "$PY" set-model --model "$model" --restart-gateway
    ;;
  pick)
    python3 "$PY" models
    ;;
  test)
    python3 "$PY" test "$@"
    ;;
  show)
    python3 "$PY" show
    ;;
  list)
    python3 "$PY" list-models
    ;;
  rollback|rb)
    if [[ $# -gt 0 ]]; then
      python3 "$PY" rollback --backup "$1" --restart-gateway
    else
      python3 "$PY" rollback --restart-gateway
    fi
    ;;
  help|--help|-h|*)
    cat <<'EOF'
rr - short wrapper for realmrouter-switch

Commands:
  rr init [model]
  rr key|k <api-key>
  rr use|m <model>
  rr pick
  rr test
  rr show
  rr list
  rr rollback|rb [file]
EOF
    ;;
esac
