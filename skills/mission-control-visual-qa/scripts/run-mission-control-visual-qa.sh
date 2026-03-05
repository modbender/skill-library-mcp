#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 1 ]]; then
  echo "Usage: $0 <url1> [url2 ...]"
  exit 2
fi

SSH_TARGET="${SSH_TARGET:-neill@<YOUR_REMOTE_HOST>}"
REMOTE_RUN_DIR="${REMOTE_RUN_DIR:-~/.openclaw/workspace/mission-control-visual-qa-runner}"
OUTPUT_DIR="${OUTPUT_DIR:-~/.openclaw/workspace/output/visual-qa/}"
SCRIPT_NAME="mission-control-visual-qa.js"
LOCAL_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ssh "${SSH_TARGET}" "mkdir -p ${REMOTE_RUN_DIR} ${OUTPUT_DIR}"
scp "${LOCAL_SCRIPT_DIR}/${SCRIPT_NAME}" "${SSH_TARGET}:${REMOTE_RUN_DIR}/${SCRIPT_NAME}"

quoted_args=()
for arg in "$@"; do
  quoted_args+=("$(printf '%q' "$arg")")
done

# shellcheck disable=SC2029
ssh "${SSH_TARGET}" "cd ${REMOTE_RUN_DIR} && OUTPUT_DIR='${OUTPUT_DIR}' node ./${SCRIPT_NAME} ${quoted_args[*]}"
