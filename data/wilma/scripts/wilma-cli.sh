#!/usr/bin/env bash
set -euo pipefail

# Wrapper for wilma CLI that prefers non-interactive JSON output.
# Usage: wilma-cli.sh <args>

if command -v wilma >/dev/null 2>&1; then
  wilma "$@"
elif command -v wilmai >/dev/null 2>&1; then
  wilmai "$@"
else
  # fallback to local repo build
  node "$(pwd)/packages/wilma-cli/dist/index.js" "$@"
fi
