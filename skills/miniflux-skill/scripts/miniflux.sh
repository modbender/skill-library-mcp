#!/bin/bash
# Miniflux CLI Wrapper
# Manage Miniflux - Modern minimalist feed reader

# Check required environment variables
if [ -z "$MINIFLUX_URL" ]; then
    echo "Error: MINIFLUX_URL environment variable must be set."
    echo "Example: export MINIFLUX_URL=\"https://your-miniflux-instance.com\""
    exit 1
fi

if [ -z "$MINIFLUX_TOKEN" ]; then
    echo "Error: MINIFLUX_TOKEN environment variable must be set."
    echo "Get your token from Settings > API Keys in Miniflux UI"
    exit 1
fi

# Export variables for Python script
export MINIFLUX_URL
export MINIFLUX_TOKEN

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if miniflux package is installed
if ! python3 -c "import miniflux" 2>/dev/null; then
    echo "Error: miniflux Python package not installed."
    echo "Please install it manually:"
    echo "  uv pip install miniflux"
    echo ""
    echo "Or with pip:"
    echo "  pip install miniflux"
    exit 1
fi

# Run Python script
python3 "$SCRIPT_DIR/miniflux-cli.py" "$@"
