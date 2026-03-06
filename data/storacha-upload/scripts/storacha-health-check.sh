#!/usr/bin/env bash
set -euo pipefail

OK="✅"
WARN="⚠️"
FAIL="❌"

cli_status="$FAIL"
node_status="$FAIL"
auth_status="$FAIL"
spaces_status="$FAIL"
active_space_status="$FAIL"
provider_status="$FAIL"
usage_status="$WARN"

echo "========================================="
echo "  Storacha Health Check"
echo "========================================="
echo ""

# CLI installed
if command -v storacha &>/dev/null; then
    cli_version=$(storacha --version 2>/dev/null || echo "unknown")
    echo "$OK CLI installed: storacha $cli_version"
    cli_status="$OK"
else
    echo "$FAIL CLI not found. Install with: npm install -g @storacha/cli"
fi

# Node.js version
if command -v node &>/dev/null; then
    node_ver=$(node -v 2>/dev/null)
    node_major=${node_ver#v}
    node_major=${node_major%%.*}
    if [[ "$node_major" -ge 18 ]]; then
        echo "$OK Node.js $node_ver (meets v18+ requirement)"
        node_status="$OK"
    else
        echo "$WARN Node.js $node_ver is below v18. Upgrade at https://nodejs.org"
        node_status="$WARN"
    fi
else
    echo "$FAIL Node.js not found. Install from https://nodejs.org"
fi

# Authentication
if [[ "$cli_status" == "$OK" ]]; then
    whoami_output=$(storacha whoami 2>&1 || true)
    if echo "$whoami_output" | grep -q "did:key:"; then
        agent_did=$(echo "$whoami_output" | grep -o "did:key:[^ ]*")
        echo "$OK Authenticated as $agent_did"
        auth_status="$OK"
    else
        echo "$FAIL Not authenticated. Run: storacha login your@email.com"
    fi
fi

# Spaces
if [[ "$auth_status" == "$OK" ]]; then
    space_list=$(storacha space ls 2>&1 || true)
    if [[ -n "$space_list" ]] && ! echo "$space_list" | grep -qi "no spaces"; then
        space_count=$(echo "$space_list" | grep -c "did:key:" || echo "0")
        echo "$OK Found $space_count space(s)"
        spaces_status="$OK"

        if echo "$space_list" | grep -q "^\*"; then
            active_line=$(echo "$space_list" | grep "^\*")
            echo "$OK Active space: $active_line"
            active_space_status="$OK"
        else
            echo "$WARN No active space. Run: storacha space use \"SpaceName\""
            active_space_status="$WARN"
        fi
    else
        echo "$FAIL No spaces found. Run: storacha space create \"MyFiles\""
    fi
fi

# Provider registration
if [[ "$active_space_status" == "$OK" ]]; then
    space_info=$(storacha space info 2>&1 || true)
    if echo "$space_info" | grep -q "did:web:"; then
        echo "$OK Provider registered"
        provider_status="$OK"
    else
        echo "$WARN No provider found. Register space at https://console.storacha.network"
        provider_status="$WARN"
    fi
fi

# Storage usage
bytes_to_human() {
    local bytes=$1
    if [[ $bytes -ge 1073741824 ]]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1073741824}") GB"
    elif [[ $bytes -ge 1048576 ]]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1048576}") MB"
    elif [[ $bytes -ge 1024 ]]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1024}") KB"
    else
        echo "$bytes bytes"
    fi
}

if [[ "$active_space_status" == "$OK" ]]; then
    usage_output=$(storacha usage report 2>&1 || true)
    if echo "$usage_output" | grep -qi "error\|permission"; then
        echo "$WARN Could not fetch usage (permission issue). Uploads may still work."
    else
        size_bytes=$(echo "$usage_output" | grep -oP 'Size:\s*\K[0-9]+' || echo "")
        if [[ -n "$size_bytes" ]]; then
            human_size=$(bytes_to_human "$size_bytes")
            echo "$OK Storage used: $human_size ($size_bytes bytes)"
            usage_status="$OK"
        else
            echo "$WARN Could not parse storage usage."
        fi
    fi
fi

echo ""
echo "========================================="
echo "  Summary"
echo "========================================="
echo "  CLI installed:      $cli_status"
echo "  Node.js v18+:       $node_status"
echo "  Authenticated:      $auth_status"
echo "  Spaces exist:       $spaces_status"
echo "  Active space set:   $active_space_status"
echo "  Provider registered:$provider_status"
echo "  Storage usage:      $usage_status"
echo "========================================="
echo ""

if [[ "$cli_status" == "$OK" && "$auth_status" == "$OK" && "$active_space_status" == "$OK" && "$provider_status" == "$OK" ]]; then
    echo "🚀 Ready to upload!"
else
    echo "🔧 Setup incomplete. Fix the items marked $FAIL or $WARN above."
    if [[ "$cli_status" != "$OK" ]]; then
        echo "  → Install CLI: npm install -g @storacha/cli"
    fi
    if [[ "$auth_status" != "$OK" ]]; then
        echo "  → Authenticate: storacha login your@email.com"
    fi
    if [[ "$spaces_status" != "$OK" ]]; then
        echo "  → Create space: storacha space create \"MyFiles\""
    fi
    if [[ "$active_space_status" != "$OK" && "$spaces_status" == "$OK" ]]; then
        echo "  → Set active space: storacha space use \"SpaceName\""
    fi
fi
