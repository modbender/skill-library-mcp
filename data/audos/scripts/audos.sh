#!/usr/bin/env bash
# Audos Workspace Builder API client
# Usage: ./audos.sh <command> [args...]

set -e

BASE_URL="${AUDOS_BASE_URL:-https://audos.com/api/agent/onboard}"

usage() {
    cat <<EOF
Audos Workspace Builder CLI

Commands:
  docs                                  Get full API documentation
  start <email> <idea> [name] [target]  Start onboarding (sends OTP)
  verify <sessionToken> <otpCode>       Verify OTP and get authToken
  status <workspaceId> <authToken>      Check build progress
  chat <workspaceId> <authToken> <msg>  Chat with Otto
  rebuild <workspaceId> <authToken>     Rebuild failed workspace

Environment:
  AUDOS_BASE_URL  API base URL (optional)

Examples:
  ./audos.sh docs
  ./audos.sh start user@example.com "Dog walking app" "PawWalker"
  ./audos.sh verify aos_abc123 7294
  ./audos.sh status ws_xyz aud_live_xxx
  ./audos.sh chat ws_xyz aud_live_xxx "What should I focus on?"
  ./audos.sh rebuild ws_xyz aud_live_xxx
EOF
    exit 1
}

cmd_docs() {
    curl -s "$BASE_URL" | jq .
}

cmd_start() {
    local email="$1"
    local idea="$2"
    local name="${3:-}"
    local target="${4:-}"
    
    [[ -z "$email" || -z "$idea" ]] && { echo "Error: email and idea required"; usage; }
    
    local payload="{\"email\":\"$email\",\"businessIdea\":\"$idea\""
    [[ -n "$name" ]] && payload="$payload,\"businessName\":\"$name\""
    [[ -n "$target" ]] && payload="$payload,\"targetCustomer\":\"$target\""
    payload="$payload}"
    
    curl -s -X POST "$BASE_URL/start" \
        -H "Content-Type: application/json" \
        -d "$payload"
}

cmd_verify() {
    local token="$1"
    local code="$2"
    
    [[ -z "$token" || -z "$code" ]] && { echo "Error: sessionToken and otpCode required"; usage; }
    
    curl -s -X POST "$BASE_URL/verify" \
        -H "Content-Type: application/json" \
        -d "{\"sessionToken\":\"$token\",\"otpCode\":\"$code\"}"
}

cmd_status() {
    local workspace_id="$1"
    local auth_token="$2"
    
    [[ -z "$workspace_id" || -z "$auth_token" ]] && { echo "Error: workspaceId and authToken required"; usage; }
    
    curl -s -X GET "$BASE_URL/status/$workspace_id" \
        -H "Authorization: Bearer $auth_token"
}

cmd_chat() {
    local workspace_id="$1"
    local auth_token="$2"
    local message="$3"
    
    [[ -z "$workspace_id" || -z "$auth_token" || -z "$message" ]] && { echo "Error: workspaceId, authToken, and message required"; usage; }
    
    curl -s -X POST "$BASE_URL/chat/$workspace_id" \
        -H "Content-Type: application/json" \
        -d "{\"authToken\":\"$auth_token\",\"message\":\"$message\"}"
}

cmd_rebuild() {
    local workspace_id="$1"
    local auth_token="$2"
    
    [[ -z "$workspace_id" || -z "$auth_token" ]] && { echo "Error: workspaceId and authToken required"; usage; }
    
    curl -s -X POST "$BASE_URL/rebuild/$workspace_id" \
        -H "Authorization: Bearer $auth_token"
}

# Main
[[ $# -lt 1 ]] && usage

case "$1" in
    docs)    cmd_docs ;;
    start)   shift; cmd_start "$@" ;;
    verify)  shift; cmd_verify "$@" ;;
    status)  shift; cmd_status "$@" ;;
    chat)    shift; cmd_chat "$@" ;;
    rebuild) shift; cmd_rebuild "$@" ;;
    *)       usage ;;
esac
