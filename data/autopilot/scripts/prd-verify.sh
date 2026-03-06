#!/bin/bash
# prd-verify.sh — PRD verify entrypoint

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -f "${SCRIPT_DIR}/prd_verify_engine.py" ]; then
    echo "prd-verify: missing ${SCRIPT_DIR}/prd_verify_engine.py" >&2
    exit 3
fi

exec "$PYTHON_BIN" "${SCRIPT_DIR}/prd_verify_engine.py" --project-dir "$PROJECT_DIR" "$@"
