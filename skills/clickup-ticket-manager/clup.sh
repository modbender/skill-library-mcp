#!/bin/bash

# ClickUp Ticket Manager (clup)
# Creates tasks in ClickUp with minimum quality standards

set -eo pipefail  # Exit on error, catch pipeline failures (removed -u for better compatibility)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PRIORITY=""  # No default - only set if explicitly provided
STATUS="${CLICKUP_DEFAULT_STATUS:-BACKLOG}"  # Use ENV or default to BACKLOG
TAGS="${CLICKUP_DEFAULT_TAG:-KI}"  # Use ENV or default to 'automated' (comma-separated)

# Print usage
usage() {
    cat << EOF
ClickUp Ticket Manager (clup)
Usage: clup --title "..." --description "..." [OPTIONS]

Create a ClickUp task with smart defaults.

Required:
  --title TITLE           Task title (short and clear)
  --description DESC      Task description (2-3 sentences minimum)

Optional:
  --priority LEVEL        Priority: urgent, high, normal, low (if not set, ClickUp default)
  --status STATUS         Status (overrides default)
  --tags TAG1,TAG2,...    Tags (comma-separated, overrides default)
  --help                  Show this help

Environment Variables:
  CLICKUP_API_KEY              ClickUp API token (required)
  CLICKUP_DEFAULT_LIST_ID      Target list ID (required)
  CLICKUP_DEFAULT_STATUS       Default status for new tasks (default: "BACKLOG")
  CLICKUP_DEFAULT_TAG          Default tags, comma-separated (default: "automated")

Examples:
  clup --title "Open firewall port" \\
       --description "Open port 443 from web-01 to db-prod for API communication..."

  clup --title "Fix login bug" \\
       --description "Login page returns 500 error since deployment..." \\
       --priority high --tags "bug,urgent,backend"

EOF
    exit 0
}

# Parse arguments
TITLE=""
DESCRIPTION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --title)
            TITLE="$2"
            shift 2
            ;;
        --description|--desc)
            DESCRIPTION="$2"
            shift 2
            ;;
        --priority)
            case "$2" in
                urgent) PRIORITY=1 ;;
                high) PRIORITY=2 ;;
                normal) PRIORITY=3 ;;
                low) PRIORITY=4 ;;
                *) echo -e "${RED}Error: Invalid priority. Use: urgent, high, normal, low${NC}" >&2; exit 1 ;;
            esac
            shift 2
            ;;
        --status)
            STATUS="$2"
            shift 2
            ;;
        --tags)
            TAGS="$2"
            shift 2
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}" >&2
            usage
            ;;
    esac
done

# Validate required env vars
if [[ -z "${CLICKUP_API_KEY:-}" ]]; then
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}" >&2
    echo -e "${RED}║ Error: CLICKUP_API_KEY environment variable not set           ║${NC}" >&2
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}" >&2
    echo "" >&2
    echo -e "${YELLOW}Please set your ClickUp API key:${NC}" >&2
    echo -e "  ${GREEN}export CLICKUP_API_KEY=\"pk_your_api_key_here\"${NC}" >&2
    echo "" >&2
    echo "To make it permanent, add to ~/.zshrc or ~/.bashrc:" >&2
    echo -e "  ${GREEN}echo 'export CLICKUP_API_KEY=\"pk_xxx\"' >> ~/.zshrc${NC}" >&2
    echo "" >&2
    echo "Get your API key: ClickUp Settings → Apps → Generate API Token" >&2
    exit 1
fi

if [[ -z "${CLICKUP_DEFAULT_LIST_ID:-}" ]]; then
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}" >&2
    echo -e "${RED}║ Error: CLICKUP_DEFAULT_LIST_ID environment variable not set   ║${NC}" >&2
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}" >&2
    echo "" >&2
    echo -e "${YELLOW}Please set your ClickUp List ID:${NC}" >&2
    echo -e "  ${GREEN}export CLICKUP_DEFAULT_LIST_ID=\"123456789\"${NC}" >&2
    echo "" >&2
    echo "To make it permanent, add to ~/.zshrc or ~/.bashrc:" >&2
    echo -e "  ${GREEN}echo 'export CLICKUP_DEFAULT_LIST_ID=\"xxx\"' >> ~/.zshrc${NC}" >&2
    echo "" >&2
    echo "Find your List ID in the ClickUp URL:" >&2
    echo "  https://app.clickup.com/123456/v/li/901234567" >&2
    echo "                                      ^^^^^^^^^^^" >&2
    echo "                                      This is your List ID" >&2
    exit 1
fi

# Validate required arguments
if [[ -z "$TITLE" ]]; then
    echo -e "${RED}Error: --title is required${NC}" >&2
    usage
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo -e "${RED}Error: --description is required${NC}" >&2
    usage
fi

# Build tags array for JSON
# Convert comma-separated string to JSON array: "tag1,tag2" -> ["tag1","tag2"]
if [[ -n "$TAGS" ]]; then
    IFS=',' read -ra TAG_ARRAY <<< "$TAGS"
    TAGS_JSON=$(printf ',"%s"' "${TAG_ARRAY[@]}")
    TAGS_JSON="[${TAGS_JSON:1}]"  # Remove leading comma and wrap in brackets
else
    TAGS_JSON="[]"
fi

# Build JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "name": "$TITLE",
  "description": "$DESCRIPTION",
  "status": "$STATUS",
  "tags": $TAGS_JSON
}
EOF
)

# Add priority only if set
if [[ -n "$PRIORITY" ]]; then
    JSON_PAYLOAD=$(echo "$JSON_PAYLOAD" | sed 's/}$/,\n  "priority": '"$PRIORITY"'\n}/')
fi

# Make API request
response=$(curl -s -w "\n%{http_code}" -X POST \
    "https://api.clickup.com/api/v2/list/${CLICKUP_DEFAULT_LIST_ID}/task" \
    -H "Authorization: ${CLICKUP_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

# Extract HTTP status code (last line)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [[ "$http_code" == "200" ]]; then
    task_id=$(echo "$body" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    task_url=$(echo "$body" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    # Output clean JSON
    cat <<EOF
{"status":"ok","ticket_id":"${task_id}","url":"${task_url}"}
EOF
else
    # Output error JSON
    cat <<EOF >&2
{"status":"error","http_code":${http_code},"message":"Failed to create ticket"}
EOF
    exit 1
fi
