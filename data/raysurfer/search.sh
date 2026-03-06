#!/usr/bin/env bash
# Search Raysurfer cache. Usage: bash search.sh "task description"
TASK="${1:-Parse a CSV file and generate a bar chart}"
curl -s -X POST https://api.raysurfer.com/api/retrieve/search \
  -H "Authorization: Bearer $RAYSURFER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"task\": \"$TASK\", \"top_k\": 5, \"min_verdict_score\": 0.3}" | python3 -m json.tool 2>/dev/null
