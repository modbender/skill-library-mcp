#!/usr/bin/env bash
set -euo pipefail

# Wrapper to run the Node Tavily search CLI.
# Usage:
#   TAVILY_API_KEY=... ./tavily_search.sh --query "..." --max_results 5

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec node "$DIR/tavily_search.js" "$@"
