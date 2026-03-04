#!/usr/bin/env bash
set -euo pipefail

err() { echo "[preflight] $*" >&2; }

if ! command -v docker >/dev/null 2>&1; then
  err "docker CLI not found. Install Docker Desktop (macOS/Windows) or Docker Engine (Linux)."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  err "Docker daemon not reachable. Start Docker Desktop (macOS) and wait until it finishes starting."
  exit 1
fi

if ! docker mcp version >/dev/null 2>&1; then
  err "docker mcp not available. Ensure Docker Desktop is recent and MCP Toolkit is enabled (Settings → Beta features)."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  err "jq not found. Install jq (macOS: brew install jq). Required for call-tool.sh JSON parsing."
  exit 1
fi

echo "[preflight] OK: docker + docker mcp + jq available"
