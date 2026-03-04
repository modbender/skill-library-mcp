#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Agent-safe wrapper for environments where non-zero exit codes can hide output.
"$SCRIPT_DIR/openclaw_smoke.sh" --agent-safe
