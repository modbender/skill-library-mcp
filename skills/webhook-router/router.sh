#!/bin/bash
#
# Webhook Router for OpenClaw
# Routes incoming webhooks to appropriate handlers based on source
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDLERS_DIR="${SCRIPT_DIR}/handlers"
LOG_FILE="${WEBHOOK_LOG_PATH:-/Users/gregborden/.openclaw/workspace/memory/webhooks.jsonl}"
DEFAULT_HANDLER="${HANDLERS_DIR}/generic.sh"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Parse arguments
SOURCE=""
EVENT_TYPE=""
PAYLOAD_FILE=""
HEADERS_FILE=""

show_help() {
    cat << 'EOF'
Usage: router.sh [OPTIONS] [PAYLOAD_FILE]

Webhook router for OpenClaw - routes webhooks to appropriate handlers.

Options:
  --source SOURCE       Webhook source identifier (e.g., github-myrepo)
  --event EVENT_TYPE    Event type (e.g., push, pull_request)
  --headers FILE        File containing HTTP headers
  -h, --help           Show this help message

Arguments:
  PAYLOAD_FILE         JSON payload file (default: stdin)

Examples:
  # Route from stdin with explicit source
  echo '{"test": "data"}' | ./router.sh --source github-myapp --event push

  # Route from file with headers
  ./router.sh --source stripe --event payment.success --headers headers.txt payload.json

  # Auto-detect source from payload
  cat webhook.json | ./router.sh

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE="$2"
            shift 2
            ;;
        --event)
            EVENT_TYPE="$2"
            shift 2
            ;;
        --headers)
            HEADERS_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            show_help
            exit 1
            ;;
        *)
            PAYLOAD_FILE="$1"
            shift
            ;;
    esac
done

# Read payload from file or stdin
if [[ -n "$PAYLOAD_FILE" && -f "$PAYLOAD_FILE" ]]; then
    PAYLOAD=$(cat "$PAYLOAD_FILE")
else
    PAYLOAD=$(cat)
fi

# Validate payload is valid JSON
if ! echo "$PAYLOAD" | jq -e . >/dev/null 2>&1; then
    echo '{"error": "Invalid JSON payload"}' >&2
    
    # Log error
    LOG_ENTRY=$(jq -n \
        --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        --arg source "${SOURCE:-unknown}" \
        --arg event "${EVENT_TYPE:-unknown}" \
        --arg error "Invalid JSON payload" \
        '{
            timestamp: $ts,
            source: $source,
            event_type: $event,
            error: $error,
            processed: false
        }')
    echo "$LOG_ENTRY" >> "$LOG_FILE"
    exit 1
fi

# Auto-detect source if not provided
if [[ -z "$SOURCE" ]]; then
    # Check query parameter style (from header or env)
    if [[ -n "${WEBHOOK_SOURCE:-}" ]]; then
        SOURCE="$WEBHOOK_SOURCE"
    # Check for GitHub signature/header
    elif [[ -n "${HTTP_X_GITHUB_EVENT:-}" ]] || [[ -n "${HTTP_X_HUB_SIGNATURE:-}" ]]; then
        REPO=$(echo "$PAYLOAD" | jq -r '.repository.full_name // .repository.name // "unknown"' 2>/dev/null || echo "unknown")
        SOURCE="github-${REPO//\//-}"
    # Check for GitLab
    elif [[ -n "${HTTP_X_GITLAB_EVENT:-}" ]]; then
        PROJECT=$(echo "$PAYLOAD" | jq -r '.project.path_with_namespace // "unknown"' 2>/dev/null || echo "unknown")
        SOURCE="gitlab-${PROJECT//\//-}"
    # Check for Stripe
    elif [[ -n "${HTTP_STRIPE_SIGNATURE:-}" ]]; then
        SOURCE="stripe-webhook"
    # Check payload structure for hints
    else
        # Try to detect from payload structure
        if echo "$PAYLOAD" | jq -e '.repository.full_name' >/dev/null 2>&1; then
            REPO=$(echo "$PAYLOAD" | jq -r '.repository.full_name')
            SOURCE="github-${REPO//\//-}"
        elif echo "$PAYLOAD" | jq -e '.object_kind' >/dev/null 2>&1; then
            KIND=$(echo "$PAYLOAD" | jq -r '.object_kind')
            PROJECT=$(echo "$PAYLOAD" | jq -r '.project.path_with_namespace // "unknown"')
            SOURCE="gitlab-${PROJECT//\//-}-${KIND}"
        else
            SOURCE="generic-unknown"
        fi
    fi
fi

# Auto-detect event type if not provided
if [[ -z "$EVENT_TYPE" ]]; then
    if [[ -n "${HTTP_X_GITHUB_EVENT:-}" ]]; then
        EVENT_TYPE="$HTTP_X_GITHUB_EVENT"
    elif [[ -n "${HTTP_X_GITLAB_EVENT:-}" ]]; then
        EVENT_TYPE="$HTTP_X_GITLAB_EVENT"
    elif [[ -n "${HTTP_X_EVENT_TYPE:-}" ]]; then
        EVENT_TYPE="$HTTP_X_EVENT_TYPE"
    else
        # Try to extract from payload
        EVENT_TYPE=$(echo "$PAYLOAD" | jq -r '.
            | if .action then .action
            elif .event then .event
            elif .type then .type
            elif .object_kind then .object_kind
            else "unknown"
            end')
    fi
fi

# Normalize event type
EVENT_TYPE=$(echo "$EVENT_TYPE" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')

# Extract additional metadata
REPOSITORY="$(echo "$PAYLOAD" | jq -r '.repository.full_name // .repository.name // .project.path_with_namespace // "unknown"' 2>/dev/null || echo "unknown")"
SENDER="$(echo "$PAYLOAD" | jq -r '.sender.login // .user.username // .pusher.name // "unknown"' 2>/dev/null || echo "unknown")"

# Calculate payload hash for deduplication
if command -v sha256sum &> /dev/null; then
    PAYLOAD_HASH=$(echo "$PAYLOAD" | sha256sum | cut -d' ' -f1 | head -c 16)
else
    # macOS fallback
    PAYLOAD_HASH=$(echo "$PAYLOAD" | shasum -a 256 | cut -d' ' -f1 | head -c 16)
fi

# Determine handler
HANDLER=""
SOURCE_TYPE="${SOURCE%%-*}"

# Look for specific handler
if [[ -x "${HANDLERS_DIR}/${SOURCE}.sh" ]]; then
    HANDLER="${HANDLERS_DIR}/${SOURCE}.sh"
elif [[ -x "${HANDLERS_DIR}/${SOURCE_TYPE}.sh" ]]; then
    HANDLER="${HANDLERS_DIR}/${SOURCE_TYPE}.sh"
elif [[ -x "${HANDLERS_DIR}/generic.sh" ]]; then
    HANDLER="${HANDLERS_DIR}/generic.sh"
else
    echo '{"error": "No handler found"}' >&2
    exit 1
fi

# Log the webhook
LOG_ENTRY=$(jq -n \
    --arg ts "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg source "$SOURCE" \
    --arg event "$EVENT_TYPE" \
    --arg repo "$REPOSITORY" \
    --arg sender "$SENDER" \
    --arg hash "$PAYLOAD_HASH" \
    --arg handler "$HANDLER" \
    '{
        timestamp: $ts,
        source: $source,
        event_type: $event,
        repository: $repo,
        sender: $sender,
        payload_hash: $hash,
        handler: $handler,
        processed: true
    }')

echo "$LOG_ENTRY" >> "$LOG_FILE"

# Route to handler
RESULT=$("$HANDLER" "$PAYLOAD" "$SOURCE" "$EVENT_TYPE" 2>&1)
EXIT_CODE=$?

# Return response
if [[ $EXIT_CODE -eq 0 ]]; then
    RESPONSE=$(jq -n \
        --arg source "$SOURCE" \
        --arg event "$EVENT_TYPE" \
        --arg handler "$HANDLER" \
        --arg result "$RESULT" \
        '{
            status: "success",
            source: $source,
            event_type: $event,
            handler: $handler,
            message: $result
        }')
    echo "$RESPONSE"
    exit 0
else
    RESPONSE=$(jq -n \
        --arg source "$SOURCE" \
        --arg event "$EVENT_TYPE" \
        --arg handler "$HANDLER" \
        --arg error "$RESULT" \
        '{
            status: "error",
            source: $source,
            event_type: $event,
            handler: $handler,
            error: $error
        }')
    echo "$RESPONSE"
    exit 1
fi
