#!/usr/bin/env bash
set -euo pipefail

# Sync from RUNTIME (source of truth) -> ARTIFACT (ClawHub publish workdir)

RUNTIME_DIR="${RUNTIME_DIR:-/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent}"
ARTIFACT_AGENT_DIR="${ARTIFACT_AGENT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/agent}"

if [[ ! -d "${RUNTIME_DIR}" ]]; then
  echo "FAIL: runtime workspace not found: ${RUNTIME_DIR}" >&2
  exit 1
fi

mkdir -p "${ARTIFACT_AGENT_DIR}"

echo "Sync runtime -> artifact"
echo "  runtime:  ${RUNTIME_DIR}"
echo "  artifact: ${ARTIFACT_AGENT_DIR}"

rsync -a --delete \
  --exclude '.openclaw/' \
  --exclude '.git/' \
  --exclude '**/.venv/' \
  --exclude '**/__pycache__/' \
  --exclude '**/*.pyc' \
  --exclude '**/*.pyo' \
  --exclude '**/.DS_Store' \
  --exclude 'logs/' \
  --exclude 'tmp/' \
  "${RUNTIME_DIR}/" \
  "${ARTIFACT_AGENT_DIR}/"

echo "OK: synced."
