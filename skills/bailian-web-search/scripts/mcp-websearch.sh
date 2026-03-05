#!/bin/bash

# MCP WebSearch Tool Script (Streamable HTTP)
# Usage: ./mcp-websearch.sh <query> [count]
# Example: ./mcp-websearch.sh "上海天气" 5

# Check if DASHSCOPE_API_KEY is set
if [ -z "$DASHSCOPE_API_KEY" ]; then
  echo "Error: DASHSCOPE_API_KEY environment variable is not set"
  exit 1
fi

# Parse command line arguments
QUERY="${1:-上海天气}"  # Default query if not provided
COUNT="${2:-5}"         # Default count if not provided

# Validate count is a number
if ! [[ "$COUNT" =~ ^[0-9]+$ ]]; then
  echo "Error: count must be a number"
  echo "Usage: $0 <query> [count]"
  exit 1
fi

echo "Search query: $QUERY"
echo "Result count: $COUNT"
echo ""

# Streamable HTTP endpoint
MCP_URL="https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/mcp"

echo "=== MCP WebSearch Searching (Streamable HTTP) ==="
echo ""

# Function to send JSON-RPC request and get response via streamable HTTP
send_request() {
  local req_json="$1"
  
  # Send POST request to streamable HTTP endpoint
  local response
  response=$(curl -s --connect-timeout 60 -X POST "$MCP_URL" \
    -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$req_json")
  
  # Check if response is valid JSON
  if echo "$response" | jq -e . >/dev/null 2>&1; then
    echo "$response" | jq .
  else
    echo "Error: Invalid response received"
    echo "$response"
    return 1
  fi
}

echo "Step 1: Sending initialize request..."
INIT_REQ='{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "curl-client", "version": "1.0.0"}
  }
}'

send_request "$INIT_REQ"
echo ""

echo "Step 2: Sending initialized notification..."
# Send notifications/initialized (no response expected)
curl -s -o /dev/null -X POST "$MCP_URL" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "notifications/initialized"
  }'
echo "  Notification sent"
echo ""

echo "Step 3: Listing available tools..."
LIST_TOOLS_REQ='{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}'

send_request "$LIST_TOOLS_REQ"
echo ""

echo "Step 4: Calling web search tool..."
# Build tool request with user-provided query and count
TOOL_REQ=$(jq -n \
  --arg query "$QUERY" \
  --argjson count "$COUNT" \
  '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "bailian_web_search",
      "arguments": {
        "query": $query,
        "count": $count
      }
    }
  }')

send_request "$TOOL_REQ"
echo ""

echo "=== Search Complete ==="
