#!/bin/bash
# MCP tool call helper
# Usage: mcp-call.sh <endpoint-url> <tool-name> '<json-arguments>'
# Example: mcp-call.sh https://aispecialistshub.com/api/v1/mcp/user/key list_specialists '{}'

set -euo pipefail

URL="${1:?Usage: mcp-call.sh <endpoint-url> <tool-name> '<json-arguments>'}"
TOOL="${2:?Missing tool name}"
ARGS="${3:-\{\}}"

# Build payload via python to avoid shell escaping issues
PAYLOAD=$(python3 -c "
import json, sys
print(json.dumps({
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'tools/call',
    'params': {
        'name': sys.argv[1],
        'arguments': json.loads(sys.argv[2])
    }
}))
" "$TOOL" "$ARGS")

RESPONSE=$(curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d "$PAYLOAD")

# Parse SSE response
echo "$RESPONSE" | python3 -c "
import sys, json
raw = sys.stdin.read()
try:
    data = raw.split('data: ')[1]
    result = json.loads(data)
    if 'error' in result:
        print(json.dumps(result['error'], indent=2))
        sys.exit(1)
    for content in result['result']['content']:
        print(content['text'])
except (IndexError, json.JSONDecodeError, KeyError) as e:
    print(f'Parse error: {e}', file=sys.stderr)
    print(raw, file=sys.stderr)
    sys.exit(1)
"
