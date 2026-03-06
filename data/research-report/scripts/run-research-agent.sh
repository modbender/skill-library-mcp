#!/usr/bin/env bash
# run-research-agent.sh — Invoke the full research workflow via OpenClaw agent
# This script is called by the agent to execute the research process
set -euo pipefail

# Usage: run-research-agent.sh --topic <name> --mode <lite|full> --iterations <n> --workspace <dir>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Source the main script with agent-friendly defaults
exec "$SCRIPT_DIR/research-report.sh" "$@"
