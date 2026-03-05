#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXAMPLES_DIR="$ROOT_DIR/examples"
WORKSPACE_DIR="$EXAMPLES_DIR/workspace"

# Remove generated line-delimited logs and lock files.
find "$ROOT_DIR" -type f \( -name '*.jsonl' -o -name '*.lock' \) -exec unlink {} \;

# Remove generated workspace tree if present.
if [[ -d "$WORKSPACE_DIR" ]]; then
  find "$WORKSPACE_DIR" -type f -exec unlink {} \;
  find "$WORKSPACE_DIR" -type l -exec unlink {} \;
  find "$WORKSPACE_DIR" -depth -type d -exec rmdir {} \; 2>/dev/null || true
fi

echo "clean_complete root=$ROOT_DIR"
