#!/usr/bin/env bash
# god logs - View activity logs
# Usage: god logs [options]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib"

# Source libraries
source "$LIB_DIR/output.sh"
source "$LIB_DIR/logging.sh"

# Show help
show_help() {
    cat << 'EOF'
Usage: god logs [options]

View god-mode activity logs.

Options:
  -n, --lines <N>    Show last N lines (default: 50)
  -f, --follow       Follow log output (like tail -f)
  --path             Show log file path
  --clear            Clear all logs
  -h, --help         Show this help

Examples:
  god logs                # Last 50 lines
  god logs -n 100         # Last 100 lines
  god logs -f             # Follow log output
  god logs --path         # Show log file location
EOF
}

# Parse arguments
LINES=50
FOLLOW=false
SHOW_PATH=false
CLEAR=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--lines)
            LINES="$2"
            shift 2
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        --path)
            SHOW_PATH=true
            shift
            ;;
        --clear)
            CLEAR=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

LOG_FILE=$(get_log_file)

# Handle options
if [[ "$SHOW_PATH" == "true" ]]; then
    echo "$LOG_FILE"
    exit 0
fi

if [[ "$CLEAR" == "true" ]]; then
    > "$LOG_FILE"
    success "Logs cleared"
    exit 0
fi

# Show logs
if [[ ! -f "$LOG_FILE" ]]; then
    warn "No logs yet"
    exit 0
fi

if [[ "$FOLLOW" == "true" ]]; then
    tail -f "$LOG_FILE"
else
    tail -n "$LINES" "$LOG_FILE"
fi
