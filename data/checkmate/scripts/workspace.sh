#!/usr/bin/env bash
# checkmate/scripts/workspace.sh
# Creates and initializes a checkmate workspace directory.
#
# Usage: workspace.sh <base_dir> [task_description]
#   base_dir: parent directory for the workspace (e.g. /tmp or ~/checkmate-runs)
#   task_description: optional task text to write to task.md
#
# Output: prints the workspace path to stdout

set -euo pipefail

BASE_DIR="${1:-/tmp}"
TASK="${2:-}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
WORKSPACE="${BASE_DIR}/checkmate-${TIMESTAMP}"

mkdir -p "${WORKSPACE}"

# Write initial state
cat > "${WORKSPACE}/state.json" <<EOF
{"iteration": 0, "status": "running", "createdAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF

# Write task if provided
if [ -n "${TASK}" ]; then
  echo "${TASK}" > "${WORKSPACE}/task.md"
fi

# Create feedback file (empty)
touch "${WORKSPACE}/feedback.md"

echo "${WORKSPACE}"
