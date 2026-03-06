#!/usr/bin/env bash
# Upload code to Raysurfer cache. Usage: bash upload.sh "task description" path/to/file.py
TASK="${1:?Usage: upload.sh <task> <file>}"
FILE="${2:?Usage: upload.sh <task> <file>}"
CONTENT=$(cat "$FILE" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
curl -s -X POST https://api.raysurfer.com/api/store/execution-result \
  -H "Authorization: Bearer $RAYSURFER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"$TASK\", \"file_written\": {\"path\": \"$(basename "$FILE")\", \"content\": $CONTENT}, \"succeeded\": true, \"auto_vote\": true}" | python3 -m json.tool 2>/dev/null
