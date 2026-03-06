#!/bin/bash
# ingest.sh - Ingest documents with contextual chunking
# Usage: ingest.sh <file_path> <collection> [chunk_strategy] [metadata_json]

set -euo pipefail

QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

FILE_PATH="${1:-}"
COLLECTION="${2:-}"
CHUNK_STRATEGY="${3:-paragraph}"
METADATA_JSON="${4:-{}}"

if [[ -z "$FILE_PATH" || -z "$COLLECTION" ]]; then
    echo "Usage: ingest.sh <file_path> <collection> [chunk_strategy] [metadata_json]"
    echo ""
    echo "Chunk strategies: paragraph (default), sentence, fixed, semantic"
    echo ""
    echo "Examples:"
    echo '  ingest.sh article.md my_collection paragraph'
    echo '  ingest.sh doc.txt my_collection fixed \'{"category": "docs"}\''
    exit 1
fi

if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "Error: OPENAI_API_KEY environment variable not set"
    exit 1
fi

QDRANT_URL="http://${QDRANT_HOST}:${QDRANT_PORT}"

echo "Reading file: $FILE_PATH"

# Read and chunk the file
CHUNKS=$(python3 << EOF
import json
import re

def chunk_paragraphs(text, overlap=2):
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paragraphs

def chunk_sentences(text, overlap=1):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_fixed(text, size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def chunk_semantic(text):
    # Split on headers then paragraphs
    sections = re.split(r'\n#{1,6}\s', text)
    chunks = []
    for section in sections:
        if section.strip():
            paragraphs = chunk_paragraphs(section)
            chunks.extend(paragraphs)
    return chunks

with open('$FILE_PATH', 'r', encoding='utf-8') as f:
    content = f.read()

strategy = '$CHUNK_STRATEGY'
if strategy == 'paragraph':
    chunks = chunk_paragraphs(content)
elif strategy == 'sentence':
    chunks = chunk_sentences(content)
elif strategy == 'fixed':
    chunks = chunk_fixed(content)
elif strategy == 'semantic':
    chunks = chunk_semantic(content)
else:
    chunks = chunk_paragraphs(content)

print(json.dumps(chunks))
EOF
)

TOTAL_CHUNKS=$(echo "$CHUNKS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
echo "Created $TOTAL_CHUNKS chunks using '$CHUNK_STRATEGY' strategy"

# Process chunks in batches
BATCH_SIZE=100
UPLOADED=0
FAILED=0

process_batch() {
    local batch_data="$1"
    local batch_num="$2"
    
    # Generate embeddings for batch
    local embedding_response=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -H "Content-Type: application/json" \
        https://api.openai.com/v1/embeddings \
        -d "{
            \"input\": $batch_data,
            \"model\": \"text-embedding-3-small\"
        }")
    
    local http_code=$(echo "$embedding_response" | tail -n1)
    local body=$(echo "$embedding_response" | sed '$d')
    
    if [[ "$http_code" != "200" ]]; then
        echo "Error: Embedding generation failed (HTTP $http_code)"
        return 1
    fi
    
    # Build points payload
    local points_payload=$(echo "$body" | python3 << PYEOF
import json
import sys

data = json.load(sys.stdin)
chunks = json.loads('$batch_data')
embeddings = data['data']
metadata = json.loads('$METADATA_JSON')

points = []
for i, emb in enumerate(embeddings):
    point = {
        "id": f"chunk_{batch_num}_{i}",
        "vector": emb['embedding'],
        "payload": {
            "text": chunks[i],
            **metadata,
            "chunk_index": i,
            "source_file": "$FILE_PATH"
        }
    }
    points.append(point)

print(json.dumps({"points": points}))
PYEOF
)
    
    # Upload to Qdrant
    local upload_response=$(curl -s -w "\n%{http_code}" \
        -X PUT \
        -H "Content-Type: application/json" \
        "${QDRANT_URL}/collections/${COLLECTION}/points" \
        -d "$points_payload")
    
    local upload_code=$(echo "$upload_response" | tail -n1)
    
    if [[ "$upload_code" == "200" ]]; then
        return 0
    else
        return 1
    fi
}

# Process batches
echo "Uploading chunks..."

python3 << EOF | while read -r batch; do
import json
chunks = json.loads('$CHUNKS')
for i in range(0, len(chunks), $BATCH_SIZE):
    batch = chunks[i:i+$BATCH_SIZE]
    print(json.dumps(batch))
EOF
    BATCH_NUM=$((UPLOADED / BATCH_SIZE))
    if process_batch "$batch" "$BATCH_NUM"; then
        UPLOADED=$((UPLOADED + $(echo "$batch" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")))
        echo "  Progress: $UPLOADED/$TOTAL_CHUNKS chunks uploaded"
    else
        FAILED=$((FAILED + $(echo "$batch" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")))
        echo "  Error: Batch $BATCH_NUM failed"
    fi
done

echo ""
echo "Ingestion complete:"
echo "  Total chunks: $TOTAL_CHUNKS"
echo "  Uploaded: $UPLOADED"
echo "  Failed: $FAILED"
