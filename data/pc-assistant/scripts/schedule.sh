#!/bin/bash
# PC Assistant Scheduler - Run healthcheck on schedule and save to configured location
# Part of pc-assistant skill

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Default config location
CONFIG_FILE="${PC_ASSISTANT_CONFIG:-$HOME/.config/pc-assistant.conf}"

# Load config if exists
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        # shellcheck disable=SC1090
        source "$CONFIG_FILE"
    fi
    
    # Defaults
    OUTPUT_DIR="${PC_ASSISTANT_OUTPUT_DIR:-/tmp/pc-healthcheck-reports}"
    REPORT_PREFIX="${PC_ASSISTANT_REPORT_PREFIX:-HealthCheck}"
    NOTIFY="${PC_ASSISTANT_NOTIFY:-false}"
    KEEP_DAYS="${PC_ASSISTANT_KEEP_DAYS:-30}"
    CLEANUP="${PC_ASSISTANT_CLEANUP:-false}"
}

# Create output directory
setup_output() {
    mkdir -p "$OUTPUT_DIR"
}

# Get timestamp
get_timestamp() {
    date +%Y%m%d_%H%M%S
}

# Run healthcheck based on OS
run_healthcheck() {
    local timestamp
    timestamp=$(get_timestamp)
    
    echo "[PC Assistant] Running healthcheck at $(date)"
    echo "[PC Assistant] Output: $OUTPUT_DIR"
    
    # Detect OS and run appropriate script
    case "$(uname -s)" in
        Linux*)
            if [[ -f "$SCRIPT_DIR/healthcheck.sh" ]]; then
                TEMP_DIR="/tmp/pc-healthcheck-temp" bash "$SCRIPT_DIR/healthcheck.sh" "$OUTPUT_DIR"
            else
                echo "Error: healthcheck.sh not found" >&2
                exit 1
            fi
            ;;
        Darwin*)
            if [[ -f "$SCRIPT_DIR/healthcheck.command" ]]; then
                bash "$SCRIPT_DIR/healthcheck.command" "$OUTPUT_DIR"
            else
                echo "Error: healthcheck.command not found" >&2
                exit 1
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*|Windows_NT*)
            if [[ -f "$SCRIPT_DIR/healthcheck.ps1" ]]; then
                echo "Error: Windows scheduler requires PowerShell runner" >&2
                exit 1
            fi
            ;;
        *)
            echo "Error: Unknown OS: $(uname -s)" >&2
            exit 1
            ;;
    esac
    
    # Rename files to use configured prefix (case-insensitive check)
    # Also extract recommendations to a separate file and remove JSON
    local latest_txt latest_json
    latest_txt=$(ls -t "$OUTPUT_DIR"/healthcheck_*.txt 2>/dev/null | head -1)
    latest_json=$(ls -t "$OUTPUT_DIR"/healthcheck_*.json 2>/dev/null | head -1)
    
    # Rename TXT
    if [[ -n "$latest_txt" ]]; then
        local new_name="$OUTPUT_DIR/${REPORT_PREFIX}_${timestamp}.txt"
        if [[ "$latest_txt" != "$new_name" ]]; then
            mv "$latest_txt" "$new_name" 2>/dev/null || true
            latest_txt="$new_name"
        fi
        
        # Extract recommendations to separate file (from Summary onwards)
        if grep -q "Quick Health Score\|Recommendations" "$latest_txt" 2>/dev/null; then
            local rec_line
            rec_line=$(grep -n "Quick Health Score\|SUMMARY" "$latest_txt" | head -1 | cut -d: -f1)
            if [[ -n "$rec_line" ]]; then
                tail -n +"$rec_line" "$latest_txt" > "$OUTPUT_DIR/${REPORT_PREFIX}_${timestamp}_recommendations.txt"
                echo "[PC Assistant] Recommendations saved: ${REPORT_PREFIX}_${timestamp}_recommendations.txt"
            fi
        fi
    fi
    
    # Remove JSON file (not needed)
    if [[ -n "$latest_json" ]]; then
        rm -f "$latest_json"
    fi
    
    echo "[PC Assistant] Report saved to: $OUTPUT_DIR"
}

# Cleanup old reports (keep last N days)
cleanup_old_reports() {
    if [[ "$CLEANUP" == "true" ]]; then
        echo "[PC Assistant] Cleaning up reports older than $KEEP_DAYS days..."
        # Clean up report files (not recommendations)
        find "$OUTPUT_DIR" -maxdepth 1 -name "${REPORT_PREFIX}_*.txt" ! -name "*_recommendations*" -type f -mtime "+$KEEP_DAYS" -delete 2>/dev/null || true
        find "$OUTPUT_DIR" -maxdepth 1 -name "${REPORT_PREFIX}_*_recommendations*.txt" -type f -mtime "+$KEEP_DAYS" -delete 2>/dev/null || true
        echo "[PC Assistant] Cleanup complete"
    fi
}

# Show usage
usage() {
    cat << EOF
PC Assistant Scheduler
Usage: $(basename "$0") [OPTIONS]

Options:
    -c, --config FILE    Config file location (default: ~/.config/pc-assistant.conf)
    -o, --output DIR     Output directory for reports
    -p, --prefix PREFIX  Report filename prefix (default: HealthCheck)
    -k, --keep-days N    Keep reports for N days (default: 30)
    --cleanup            Enable cleanup of old reports
    -h, --help           Show this help

Environment variables:
    PC_ASSISTANT_CONFIG         Config file path
    PC_ASSISTANT_OUTPUT_DIR     Output directory
    PC_ASSISTANT_REPORT_PREFIX  Report filename prefix
    PC_ASSISTANT_KEEP_DAYS      Days to keep reports
    PC_ASSISTANT_CLEANUP        Enable cleanup (true/false)
    PC_ASSISTANT_NOTIFY         Enable notification (true/false)

Examples:
    # Use defaults (reports to /tmp/pc-healthcheck-reports)
    $(basename "$0")

    # Custom output folder
    PC_ASSISTANT_OUTPUT_DIR="\$HOME/Downloads/pc-reports" $(basename "$0")

    # With config file
    $(basename "$0") -c /path/to/config.conf

    # Enable cleanup (auto-delete reports older than 30 days)
    PC_ASSISTANT_CLEANUP=true $(basename "$0")
EOF
}

# Main
main() {
    # Parse args
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -p|--prefix)
                REPORT_PREFIX="$2"
                shift 2
                ;;
            -k|--keep-days)
                KEEP_DAYS="$2"
                shift 2
                ;;
            --cleanup)
                CLEANUP="true"
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    load_config
    setup_output
    run_healthcheck
    cleanup_old_reports
    
    echo "[PC Assistant] Done at $(date)"
}

main "$@"