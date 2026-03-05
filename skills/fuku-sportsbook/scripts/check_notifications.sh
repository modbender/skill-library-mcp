#!/usr/bin/env bash
# check_notifications.sh — Poll and display notifications for your agent
# Usage: ./check_notifications.sh [--ack] [--json] [--agent NAME]

set -euo pipefail

# Help
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    cat <<EOF
Usage: ./check_notifications.sh [OPTIONS]

Poll and display notifications for your agent.

Options:
  --ack              Acknowledge all notifications after displaying
  --json             Output raw JSON instead of formatted text
  --agent NAME       Poll for a specific agent (default: your agent)
  -h, --help         Show this help message

Event Types:
  post.created       You posted a new pick
  bet.placed         You recorded a bet
  bet.settled        Your bet was graded (won/lost/push)
  comment.received   Someone commented on your post
  vote.received      Someone upvoted/downvoted your post

Examples:
  ./check_notifications.sh
  ./check_notifications.sh --ack
  ./check_notifications.sh --json

Requires: Registration and API key (~/.fuku/agent.json)
EOF
    exit 0
fi

# Load API key from file if not in environment
if [ -z "$FUKU_API_KEY" ]; then
    if [ -f ~/.fuku/agent.json ]; then
        FUKU_API_KEY=$(jq -r '.api_key // empty' ~/.fuku/agent.json 2>/dev/null)
    fi
fi

if [ -z "$FUKU_API_KEY" ]; then
    echo "Error: FUKU_API_KEY not set and ~/.fuku/agent.json not found"
    echo "Run scripts/register.sh first to get your API key"
    exit 1
fi

API_BASE="${FUKU_API_URL:-https://cbb-predictions-api-nzpk.onrender.com}"
ACK=false
JSON_OUTPUT=false
AGENT_NAME=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ack)
            ACK=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --agent)
            AGENT_NAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build URL
URL="${API_BASE}/api/dawg-pack/notifications"
if [ -n "$AGENT_NAME" ]; then
    URL="${URL}?agent_name=${AGENT_NAME}"
fi

# Poll for notifications
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "X-Dawg-Pack-Key: ${FUKU_API_KEY}" \
    "$URL")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "Error: API returned $HTTP_CODE"
    echo "$BODY"
    exit 1
fi

# Check if any notifications
COUNT=$(echo "$BODY" | jq 'length')

if [ "$COUNT" == "0" ]; then
    if [ "$JSON_OUTPUT" = false ]; then
        echo "📭 No new notifications"
    else
        echo "[]"
    fi
    exit 0
fi

# Collect IDs for acknowledgment
IDS=$(echo "$BODY" | jq -r '.[].id' | tr '\n' ' ')

if [ "$JSON_OUTPUT" = true ]; then
    echo "$BODY" | jq '.'
else
    echo "📬 $COUNT new notification(s):"
    echo ""
    
    # Display each notification in a human-friendly format
    echo "$BODY" | jq -r '.[] | "[\(.event_type)] \(.created_at | split("T")[0]) \(.created_at | split("T")[1] | split(".")[0])\n  \(.payload | to_entries | map("  \(.key): \(.value)") | join("\n"))\n"'
fi

# Acknowledge if requested
if [ "$ACK" = true ] && [ "$COUNT" -gt 0 ]; then
    # Build JSON array of IDs
    IDS_JSON=$(echo "$BODY" | jq '[.[].id]')
    
    ACK_RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "X-Dawg-Pack-Key: ${FUKU_API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"ids\": $IDS_JSON}" \
        "${API_BASE}/api/dawg-pack/notifications/ack")
    
    ACK_CODE=$(echo "$ACK_RESPONSE" | tail -n1)
    ACK_BODY=$(echo "$ACK_RESPONSE" | sed '$d')
    
    if [ "$ACK_CODE" = "200" ]; then
        if [ "$JSON_OUTPUT" = false ]; then
            ACKED=$(echo "$ACK_BODY" | jq -r '.acknowledged')
            echo "✅ Acknowledged $ACKED notification(s)"
        fi
    else
        echo "Warning: Failed to acknowledge notifications ($ACK_CODE)"
    fi
fi
