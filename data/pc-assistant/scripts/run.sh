#!/bin/bash
#
# PC Healthcheck - Convenience Wrapper
# Auto-detects OS and runs the appropriate script
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$(uname -s)" in
    Linux*)
        if [ -f "$SCRIPT_DIR/healthcheck.sh" ]; then
            exec "$SCRIPT_DIR/healthcheck.sh" "$@"
        else
            echo "Error: healthcheck.sh not found" >&2
            exit 1
        fi
        ;;
    Darwin*)
        if [ -f "$SCRIPT_DIR/healthcheck.command" ]; then
            exec "$SCRIPT_DIR/healthcheck.command" "$@"
        else
            echo "Error: healthcheck.command not found" >&2
            exit 1
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        if [ -f "$SCRIPT_DIR/healthcheck.ps1" ]; then
            powershell.exe -ExecutionPolicy Bypass -File "$SCRIPT_DIR/healthcheck.ps1" "$@"
        else
            echo "Error: healthcheck.ps1 not found" >&2
            exit 1
        fi
        ;;
    *)
        echo "Error: Unsupported OS: $(uname -s)" >&2
        exit 1
        ;;
esac