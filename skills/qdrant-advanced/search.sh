#!/bin/bash
# search.sh - Semantic search across Qdrant collections
# Usage: search.sh <query> <collection> [limit] [filter_json] [min_score]

set -euo pipefail

QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

QUERY="${1:-}"
COLLECTION="${2:-}"
LIMIT="${3:-10}"
FILTER_JSON="${4:-}"
MIN_SCORE="${5:-0.0}"

if [[ -z "$QUERY" || -z "$COLLECTION" ]]; then
    echo "Usage: search.sh <query> <collection> [limit] [filter_json] [min_score]"
    echo ""
    echo "Examples:"
    echo '  search.sh "machine learning" my_docs 10'
    echo '  search.sh "deployment" my_docs 5 \'{"must": [{"key": "category", "match": {"value": "devops"}}]}\''
    exit 1
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "Error: OPENAI_API_KEY environment variable not set"
    exit 1
fi

QDRANT_URL="http://${QDRANT_HOST}:${QDRANT_PORT}"

echo "Generating embedding for query..."

# Generate embedding using OpenAI API
EMBEDDING_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-Type: application/json" \
    https://api.openai.com/v1/embeddings \
    -d "{
        \"input\": \"$QUERY\",
        \"model\": \"text-embedding-3-small\"
    }")

HTTP_CODE=$(echo "$EMBEDDING_RESPONSE" | tail -n1)
EMBEDDING_BODY=$(echo "$EMBEDDING_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" != "200" ]]; then
    echo "Error: Failed to generate embedding (HTTP $HTTP_CODE)"
    echo "$EMBEDDING_BODY"
    exit 1
fi

# Extract embedding vector
VECTOR=$(echo "$EMBEDDING_BODY" | python3 -c "
import json
import sys
data = json.load(sys.stdin)
embedding = data['data'][0]['embedding']
print(json.dumps(embedding))
")

echo "Searching collection '$COLLECTION'..."

# Build search request
if [[ -n "$FILTER_JSON" && "$FILTER_JSON" != "{}" ]]; then
    SEARCH_PAYLOAD="{
        \"vector\": $VECTOR,
        \"limit\": $LIMIT,
        \"score_threshold\": $MIN_SCORE,
        \"with_payload\": true,
        \"filter\": $FILTER_JSON
    }"
else
    SEARCH_PAYLOAD="{
        \"vector\": $VECTOR,
        \"limit\": $LIMIT,
        \"score_threshold\": $MIN_SCORE,
        \"with_payload\": true
    }"
fi

# Perform search
SEARCH_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    "${QDRANT_URL}/collections/${COLLECTION}/points/search" \
    -d "$SEARCH_PAYLOAD")

HTTP_CODE=$(echo "$SEARCH_RESPONSE" | tail -n1)
SEARCH_BODY=$(echo "$SEARCH_RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" != "200" ]]; then
    echo "Error: Search failed (HTTP $HTTP_CODE)"
    echo "$SEARCH_BODY" | python3 -m json.tool 2>/dev/null || echo "$SEARCH_BODY"
    exit 1
fi

# Format and output results
echo "$SEARCH_BODY" | python3 -c "
import json
import sys

data = json.load(sys.stdin)
results = data.get('result', [])

if not results:
    print(json.dumps({'results': [], 'query': '$QUERY', 'count': 0}))
    sys.exit(0)

formatted = []
for r in results:
    formatted.append({
        'id': r.get('id'),
        'score': round(r.get('score', 0), 4),
        'text': r.get('payload', {}).get('text', ''),
        'metadata': {k: v for k, v in r.get('payload', {}).items() if k != 'text'}
    })

output = {
    'results': formatted,
    'query': '$QUERY',
    'collection': '$COLLECTION',
    'count': len(formatted)
}
print(json.dumps(output, indent=2))
"
