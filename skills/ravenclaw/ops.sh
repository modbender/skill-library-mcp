#!/bin/bash
# Ravenclaw Operations Helper Script
# Common operations for Ravenclaw Email Bridge

# Configuration
RAVENCLAW_URL="${RAVENCLAW_URL:-http://localhost:5002}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function for API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "$RAVENCLAW_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" | python3 -m json.tool 2>/dev/null || \
        curl -s -X "$method" "$RAVENCLAW_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "$RAVENCLAW_URL$endpoint" \
            -H "Content-Type: application/json" | python3 -m json.tool 2>/dev/null || \
        curl -s -X "$method" "$RAVENCLAW_URL$endpoint" \
            -H "Content-Type: application/json"
    fi
}

# Print status with color
status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

info() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Show help
help() {
    echo "Ravenclaw Operations Helper"
    echo ""
    echo "Usage: ./ops.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  status          Check Ravenclaw health"
    echo "  inbox          List all emails"
    echo "  unread         List unread emails"
    echo "  check          Trigger manual inbox check"
    echo "  stats          Show statistics"
    echo "  send <to> <sub> <body>  Send immediate email"
    echo "  schedule <to> <sub> <body> <time>  Schedule email"
    echo "  scheduled      List scheduled emails"
    echo "  cancel <id>    Cancel scheduled email"
    echo "  help           Show this help"
    echo ""
    echo "Examples:"
    echo "  ./ops.sh status"
    echo "  ./ops.sh send 'boss@company.com' 'Hi' 'Hello!'"
    echo "  ./ops.sh schedule 'hr@company.com' 'Leave' 'Request' '2026-02-20T09:00:00'"
    echo ""
}

# Main commands
case "${1:-help}" in
    status)
        echo "Checking Ravenclaw status..."
        api_call "GET" "/health"
        ;;
    inbox)
        echo "Fetching inbox..."
        api_call "GET" "/inbox"
        ;;
    unread)
        echo "Fetching unread emails..."
        api_call "GET" "/unread"
        ;;
    check)
        echo "Triggering inbox check..."
        api_call "POST" "/check"
        status "Inbox check triggered"
        ;;
    stats)
        echo "Fetching statistics..."
        api_call "GET" "/stats"
        ;;
    scheduled)
        echo "Listing scheduled emails..."
        api_call "GET" "/schedule/list"
        ;;
    send)
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
            error "Usage: ./ops.sh send <to> <subject> <body>"
            exit 1
        fi
        DATA="{\"to\":\"$2\",\"subject\":\"$3\",\"body\":\"$4\"}"
        echo "Sending email to $2..."
        api_call "POST" "/send" "$DATA"
        status "Email sent"
        ;;
    schedule)
        if [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ]; then
            error "Usage: ./ops.sh schedule <to> <subject> <body> <time>"
            error "Time format: YYYY-MM-DDTHH:MM:SS"
            exit 1
        fi
        DATA="{\"to\":\"$2\",\"subject\":\"$3\",\"body\":\"$4\",\"target_time\":\"$5\"}"
        echo "Scheduling email to $2 at $5..."
        api_call "POST" "/schedule" "$DATA"
        status "Email scheduled"
        ;;
    cancel)
        if [ -z "$2" ]; then
            error "Usage: ./ops.sh cancel <id>"
            exit 1
        fi
        echo "Cancelling scheduled email $2..."
        api_call "POST" "/schedule/cancel/$2"
        status "Cancellation requested"
        ;;
    help|--help|-h)
        help
        ;;
    *)
        error "Unknown command: $1"
        help
        exit 1
        ;;
esac
