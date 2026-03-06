#!/bin/bash
# Bailian Search - Real-time web search via Alibaba Cloud DashScope MCP
# Usage: export DASHSCOPE_API_KEY="your-key" && ./search.sh "search query"

set -e

DASHSCOPE_API_KEY="${DASHSCOPE_API_KEY}"
QUERY="$1"

# Validate API key
if [ -z "$DASHSCOPE_API_KEY" ]; then
  echo "Error: DASHSCOPE_API_KEY environment variable is not set." >&2
  echo "" >&2
  echo "Please set your DashScope API key:" >&2
  echo "  export DASHSCOPE_API_KEY='your-api-key'" >&2
  echo "" >&2
  echo "Get your API key from: https://bailian.console.aliyun.com" >&2
  exit 1
fi

# Validate query
if [ -z "$QUERY" ]; then
  echo "Usage: DASHSCOPE_API_KEY='your-key' ./search.sh <search query>" >&2
  echo "Example: DASHSCOPE_API_KEY='sk-xxx' ./search.sh 'latest AI news'" >&2
  exit 1
fi

# URL encode the query
ENCODED_QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$QUERY'''))" 2>/dev/null || echo "$QUERY")

# Call Bailian MCP SSE service
curl -s -N \
  --connect-timeout 10 \
  --max-time 60 \
  -H "Authorization: Bearer ${DASHSCOPE_API_KEY}" \
  -H "Accept: text/event-stream" \
  -H "Connection: keep-alive" \
  "https://dashscope.aliyuncs.com/api/v1/mcps/WebSearch/sse?query=${ENCODED_QUERY}" | \
  grep -E "^data:" | \
  head -10 | \
  sed 's/^data: //' | \
  python3 -c "
import json
import sys

results = []
for line in sys.stdin:
    line = line.strip()
    if line:
        try:
            data = json.loads(line)
            if 'content' in data:
                results.append(data['content'])
        except json.JSONDecodeError:
            # Handle non-JSON lines
            if line and line not in ['[DONE]', '']:
                results.append(line)
        except Exception as e:
            # Skip problematic lines
            continue

if results:
    print('\n'.join(results))
else:
    print('No results found or search failed.', file=sys.stderr)
    sys.exit(1)
" || {
  echo "Error: Search failed or no results found." >&2
  echo "Please check your API key and network connection." >&2
  exit 1
}