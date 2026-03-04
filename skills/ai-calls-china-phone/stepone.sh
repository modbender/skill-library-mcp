#!/bin/bash
# stepone.sh - Low-level Stepone AI API wrapper
# Usage: ./stepone.sh <command> [options]
#
# Commands:
#   call       - Make a call (raw JSON body)
#   callinfo   - Get call info/transcript
#   balance    - Check account balance

set -e

# JSON转义函数
json_escape() {
    local str="$1"
    str="${str//\\/\\\\}"
    str="${str//\"/\\\"}"
    str="${str//$'\n'/\\n}"
    str="${str//$'\r'/}"
    str="${str//$'\t'/\\t}"
    echo "$str"
}

# 验证手机号
validate_phone() {
    local phone="$1"
    if [[ ! "$phone" =~ ^1[3-9][0-9]{9}$ ]]; then
        echo "Error: Invalid phone number format (must be 11 digits starting with 1)"
        return 1
    fi
    return 0
}

# 验证call_id
validate_call_id() {
    local call_id="$1"
    if [[ ! "$call_id" =~ ^[a-zA-Z0-9^_-]+$ ]]; then
        echo "Error: Invalid call_id format"
        return 1
    fi
    return 0
}

# 加载API key
load_api_key() {
    if [[ -z "$STEPONEAI_API_KEY" ]]; then
        if [[ -f ~/.clawd/secrets.json ]]; then
            STEPONEAI_API_KEY=$(grep -o '"steponeai_api_key"[[:space:]]*:[[:space:]]*"[^"]*"' ~/.clawd/secrets.json | sed 's/.*"\([^"]*\)"$/\1/')
        fi
    fi
    
    if [[ -z "$STEPONEAI_API_KEY" ]]; then
        echo "Error: STEPONEAI_API_KEY not set"
        echo "Set it in your environment or in ~/.clawd/secrets.json"
        exit 1
    fi
}

COMMAND="${1:-help}"

case "$COMMAND" in
    help|--help|-h)
        echo "Stepone AI API Wrapper"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  call '<json>'     Make a call with JSON body"
        echo "  callinfo <id>     Get call info by call_id"
        echo "  balance           Check account balance"
        echo "  help              Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 call '{\"phones\": \"13800138000\", \"user_requirement\": \"Hello\"}'"
        echo "  $0 callinfo abc123def456"
        ;;
        
    call)
        load_api_key
        if [[ -z "$2" ]]; then
            echo "Usage: $0 call '<json_body>'"
            exit 1
        fi
        
        RESPONSE=$(curl -s -X POST "https://open-skill-api.steponeai.com/api/v1/callinfo/initiate_call" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $STEPONEAI_API_KEY" \
            -d "$2")
        echo "$RESPONSE"
        ;;
        
    callinfo)
        load_api_key
        if [[ -z "$2" ]]; then
            echo "Usage: $0 callinfo <call_id>"
            exit 1
        fi
        
        if ! validate_call_id "$2"; then
            exit 1
        fi
        
        RESPONSE=$(curl -s -X POST "https://open-skill-api.steponeai.com/api/v1/callinfo/search_callinfo" \
            -H "Content-Type: application/json" \
            -H "X-API-Key: $STEPONEAI_API_KEY" \
            -d "{\"call_id\": \"$2\"}")
        echo "$RESPONSE"
        ;;
        
    balance)
        echo "Check your balance at: https://open-skill.steponeai.com"
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac
