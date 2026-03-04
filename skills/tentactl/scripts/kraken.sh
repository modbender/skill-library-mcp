#!/usr/bin/env bash
# Convenience wrapper. Loads .env and delegates to kraken.py.
# Usage: kraken.sh <tool_name> [json_arguments]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load env vars
ENV_FILE="${KRAKEN_ENV_FILE:-$HOME/.tentactl.env}"
[[ -f "$ENV_FILE" ]] && { set -a; source "$ENV_FILE"; set +a; }

# Find binary
export KRAKEN_MCP_BINARY="${KRAKEN_MCP_BINARY:-$(command -v tentactl 2>/dev/null || echo "")}"
[[ -z "$KRAKEN_MCP_BINARY" && -x "$HOME/.cargo/bin/tentactl" ]] && export KRAKEN_MCP_BINARY="$HOME/.cargo/bin/tentactl"
[[ -z "$KRAKEN_MCP_BINARY" ]] && { echo "Error: tentactl not found. Install: cargo install tentactl" >&2; exit 1; }

exec python3 "$SCRIPT_DIR/kraken.py" "$@"
