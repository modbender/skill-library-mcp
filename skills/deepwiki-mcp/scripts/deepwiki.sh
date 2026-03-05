#!/usr/bin/env bash
# deepwiki.sh — Query DeepWiki MCP for any GitHub repo
# Usage:
#   deepwiki.sh ask    <owner/repo> "<question>"
#   deepwiki.sh topics <owner/repo>
#   deepwiki.sh docs   <owner/repo>
#
# No auth required. Defaults to openclaw/openclaw if repo is omitted.
# The MCP server returns SSE events; we extract the result text.

set -euo pipefail

DEEPWIKI_URL="https://mcp.deepwiki.com/mcp"
DEFAULT_REPO="openclaw/openclaw"

usage() {
  echo "Usage:"
  echo "  deepwiki.sh ask    [owner/repo] \"<question>\""
  echo "  deepwiki.sh topics [owner/repo]"
  echo "  deepwiki.sh docs   [owner/repo]"
  exit 1
}

call_mcp() {
  local tool="$1"
  local args_json="$2"
  curl -s -X POST "$DEEPWIKI_URL" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"$tool\",\"arguments\":$args_json}}" \
  | grep '^data:' \
  | grep '"id":1' \
  | sed 's/^data: //' \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'error' in data:
    print('ERROR:', data['error']['message'], file=sys.stderr)
    sys.exit(1)
result = data.get('result', {})
contents = result.get('content', [])
for c in contents:
    if c.get('type') == 'text':
        print(c['text'])
"
}

CMD="${1:-}"
[ -z "$CMD" ] && usage

case "$CMD" in
  ask)
    if [ $# -eq 3 ]; then
      REPO="$2"
      QUESTION="$3"
    elif [ $# -eq 2 ]; then
      REPO="$DEFAULT_REPO"
      QUESTION="$2"
    else
      usage
    fi
    ARGS=$(python3 -c "import json, sys; print(json.dumps({'repoName': sys.argv[1], 'question': sys.argv[2]}))" "$REPO" "$QUESTION")
    call_mcp "ask_question" "$ARGS"
    ;;
  topics)
    REPO="${2:-$DEFAULT_REPO}"
    ARGS=$(python3 -c "import json, sys; print(json.dumps({'repoName': sys.argv[1]}))" "$REPO")
    call_mcp "read_wiki_structure" "$ARGS"
    ;;
  docs)
    REPO="${2:-$DEFAULT_REPO}"
    ARGS=$(python3 -c "import json, sys; print(json.dumps({'repoName': sys.argv[1]}))" "$REPO")
    call_mcp "read_wiki_contents" "$ARGS"
    ;;
  *)
    usage
    ;;
esac
