#!/usr/bin/env bash
# Example: Full OpenClaw agent integration
# Place in ~/.openclaw/workspace/hooks/pre-send.sh

set -euo pipefail

ARC_SHIELD="${HOME}/.openclaw/workspace/skills/arc-shield/scripts/arc-shield.sh"

# Hook: Called before sending any external message
# Args: $1=channel, $2=message
pre_send_message() {
    local channel="$1"
    local message="$2"
    
    # Skip internal channels (agent-to-agent communication)
    if [[ "$channel" =~ ^(internal|agent|localhost) ]]; then
        return 0
    fi
    
    # Scan for secrets
    if ! echo "$message" | "$ARC_SHIELD" --strict 2>/dev/null; then
        echo "⚠️  [ARC-SHIELD] Message blocked: contains secrets" >&2
        echo "    Channel: $channel" >&2
        echo "    Run with --report to see details" >&2
        
        # Log the blocked attempt
        echo "[$(date)] BLOCKED message to $channel" >> ~/.openclaw/logs/arc-shield-blocks.log
        
        return 1
    fi
    
    return 0
}

# If sourced, export function for use in agent scripts
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    export -f pre_send_message
else
    # If executed directly, run as test
    if [[ $# -lt 2 ]]; then
        echo "Usage: $0 <channel> <message>" >&2
        exit 1
    fi
    
    pre_send_message "$1" "$2"
fi
