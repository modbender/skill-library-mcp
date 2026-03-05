#!/usr/bin/env bash
# proxybase-register.sh — Register with ProxyBase and store API key
# Usage: source proxybase-register.sh
#
# This script:
# 1. Checks if credentials already exist
# 2. If not, registers a new agent via POST /agents
# 3. Stores the API key in state/credentials.env
# 4. Exports PROXYBASE_API_KEY for the current shell
#
# MUST be sourced (not executed) so that exports persist in the calling shell.
#
# Fixed: captures both HTTP body and status code in one call,
#        handles 429 rate-limiting with retry, validates JSON responses.

set -euo pipefail

# Source shared library
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../lib/common.sh"

# Check if we already have credentials
if [[ -f "$CREDS_FILE" ]]; then
    source "$CREDS_FILE"
    if [[ -n "${PROXYBASE_API_KEY:-}" ]]; then
        # Validate the key still works — capture both body and code
        local_rc=0
        api_call_with_retry GET "/packages" || local_rc=$?
        if [[ $local_rc -eq 0 ]]; then
            echo "ProxyBase: Credentials loaded (key: ${PROXYBASE_API_KEY:0:8}...)"
            export PROXYBASE_API_KEY
            export PROXYBASE_API_URL
            return 0 2>/dev/null || exit 0
        else
            # Only invalidate the key on auth errors (401/403).
            # For 5xx / network errors, the key is likely still valid — just report API is down.
            if [[ "$API_HTTP_CODE" == "401" || "$API_HTTP_CODE" == "403" ]]; then
                echo "ProxyBase: Stored key is invalid (HTTP $API_HTTP_CODE) — re-registering..."
                unset PROXYBASE_API_KEY
            else
                echo "ProxyBase: API unreachable (HTTP $API_HTTP_CODE) — keeping existing key."
                echo "ProxyBase: The API may be temporarily down. Retry later." >&2
                export PROXYBASE_API_KEY
                export PROXYBASE_API_URL
                return 0 2>/dev/null || exit 0
            fi
        fi
    fi
fi

# Register new agent (with retry for 429/transient errors)
echo "ProxyBase: Registering new agent..."

local_rc=0
api_call_with_retry POST "/agents" -H "Content-Type: application/json" || local_rc=$?
if [[ $local_rc -ne 0 ]]; then
    echo "ProxyBase: ERROR — Registration failed (HTTP $API_HTTP_CODE)"
    if validate_json "$API_RESPONSE"; then
        echo "$API_RESPONSE" | jq .
    else
        echo "$API_RESPONSE"
    fi
    return 1 2>/dev/null || exit 1
fi

# Validate response contains api_key
if ! echo "$API_RESPONSE" | jq -e '.api_key' > /dev/null 2>&1; then
    echo "ProxyBase: ERROR — No api_key in registration response:"
    echo "$API_RESPONSE" | jq .
    return 1 2>/dev/null || exit 1
fi

API_KEY=$(echo "$API_RESPONSE" | jq -r '.api_key')
AGENT_ID=$(echo "$API_RESPONSE" | jq -r '.agent_id // .id // "unknown"')

if [[ -z "$API_KEY" || "$API_KEY" == "null" ]]; then
    echo "ProxyBase: ERROR — api_key field is empty/null"
    echo "$API_RESPONSE" | jq .
    return 1 2>/dev/null || exit 1
fi

# Store credentials
cat > "$CREDS_FILE" << EOF
# ProxyBase credentials — generated $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Agent ID: $AGENT_ID
export PROXYBASE_API_KEY="$API_KEY"
export PROXYBASE_API_URL="$PROXYBASE_API_URL"
EOF

chmod 600 "$CREDS_FILE"

# Export for current shell
export PROXYBASE_API_KEY="$API_KEY"
export PROXYBASE_API_URL

echo "ProxyBase: Registered successfully"
echo "  Agent ID: $AGENT_ID"
echo "  API Key:  ${API_KEY:0:8}..."
echo "  Stored:   $CREDS_FILE"
