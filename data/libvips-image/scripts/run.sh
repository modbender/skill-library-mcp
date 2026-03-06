#!/usr/bin/env bash
#
# Wrapper script to run libvips-image tools with proper library paths
# Usage: ./scripts/run.sh vips_tool.py <args>
#        ./scripts/run.sh vips_batch.py <args>
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Detect OS and set library paths
case "$(uname -s)" in
    Darwin*)
        # macOS: Set library path for libvips
        for lib_path in /opt/homebrew/lib /usr/local/lib; do
            if [ -f "$lib_path/libvips.dylib" ] || [ -f "$lib_path/libvips.42.dylib" ]; then
                export DYLD_LIBRARY_PATH="$lib_path:$DYLD_LIBRARY_PATH"
                break
            fi
        done
        ;;
    Linux*)
        # Linux: Usually handled by ldconfig, but add common paths just in case
        export LD_LIBRARY_PATH="/usr/local/lib:/usr/lib:$LD_LIBRARY_PATH"
        ;;
esac

# Determine which Python to use
PYTHON=""

# Check for project venv first
if [ -f "$SKILL_DIR/.venv/bin/python" ]; then
    PYTHON="$SKILL_DIR/.venv/bin/python"
# Check for uv
elif command -v uv &>/dev/null; then
    # Use uv run if pyproject.toml exists
    if [ -f "$SKILL_DIR/pyproject.toml" ]; then
        cd "$SKILL_DIR"
        exec uv run python "$SCRIPT_DIR/$@"
    fi
# Fallback to system python
elif command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "Error: Python not found" >&2
    exit 1
fi

# Run the script
exec "$PYTHON" "$SCRIPT_DIR/$@"
