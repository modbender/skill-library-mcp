#!/usr/bin/env bash
#
# Telnyx RAG - Trigger Embedding on Bucket
#
# This is now a thin wrapper around sync.py --embed functionality.
# The embedding logic has been moved to sync.py for better integration.
#
# Usage:
#   ./embed.sh                    # Trigger embedding on default bucket
#   ./embed.sh --status <task_id> # Check embedding task status
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_ok()   { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e "${RED}✗${NC} $1"; }

main() {
    case "${1:-}" in
        --status|-s)
            if [[ -z "${2:-}" ]]; then
                log_err "Usage: $0 --status <task_id>"
                echo ""
                echo "Check embedding task status using the task ID returned"
                echo "when you triggered embedding."
                exit 1
            fi
            
            log_info "Checking embedding status via sync.py..."
            exec python3 "$SCRIPT_DIR/sync.py" --embed-status "$2"
            ;;
        
        --help|-h)
            echo "Telnyx RAG - Embedding Trigger"
            echo ""
            echo "Usage: $0 [--status <task_id>] [--help]"
            echo ""
            echo "This script triggers embedding on your Telnyx Storage bucket."
            echo "Embedding processes your uploaded files into searchable vectors."
            echo ""
            echo "Options:"
            echo "  --status TASK_ID    Check embedding task status"
            echo "  --help              Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                  # Trigger embedding on default bucket"
            echo "  $0 --status abc123  # Check embedding task status"
            echo ""
            echo "Note: This is now a wrapper around 'sync.py --embed'."
            echo "You can also use the sync.py command directly:"
            echo "  ./sync.py --embed"
            echo "  ./sync.py --embed-status <task_id>"
            ;;
        
        --*)
            log_err "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
        
        *)
            # Default behavior: trigger embedding
            log_info "Triggering embedding via sync.py..."
            exec python3 "$SCRIPT_DIR/sync.py" --embed
            ;;
    esac
}

main "$@"