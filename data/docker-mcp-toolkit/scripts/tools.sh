#!/usr/bin/env bash
set -euo pipefail

# List tools exposed by Docker MCP Toolkit.
# Note: requires Docker Desktop running + MCP Toolkit enabled.

docker mcp tools --format list ls
