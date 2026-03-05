#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./scripts/run-codex-example.sh /path/to/repo "Implement X and add tests"

PROJECT_DIR="${1:-}"
TASK="${2:-}"

if [[ -z "$PROJECT_DIR" || -z "$TASK" ]]; then
  echo "Usage: $0 <project_dir> <task>"
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "Error: codex not found. Install with: npm i -g @openai/codex"
  exit 1
fi

cd "$PROJECT_DIR"
codex exec "$TASK"
