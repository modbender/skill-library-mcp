#!/bin/bash
# migrate.sh - Migrate between collections or upgrade embedding models
# Usage: migrate.sh <source_collection> <target_collection> [options]

set -euo pipefail

QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

QDRANT_URL="http://${QDRANT_HOST}:${QDRANT_PORT}"

SOURCE="${1:-}"
TARGET="${2:-}"

if [[ -z "$SOURCE" || -z "$TARGET" ]]; then
    echo "Usage: migrate.sh <source_collection> <target_collection> [options]"
    echo ""
    echo "Options:"
    echo "  --upgrade-model      Re-embed with new model (requires OPENAI_API_KEY)"
    echo "  --filter '<json>'    Migrate only matching points"
    echo "  --batch-size N       Points per batch (default: 100)"
    echo "  --target-dim N       Target collection dimensions"
    echo "  --target-dist DIST   Target distance metric (cosine, euclid, dot)"
    echo ""
    echo "Examples:"
    echo "  migrate.sh old_collection new_collection"
    echo "  migrate.sh old_collection new_collection --upgrade-model"
    echo "  migrate.sh old_collection new_collection --filter '{\"must\": [{\"key\": \"category\", \"match\": {\"value\": \"public\"}}]}'"
    exit 1
fi

UPGRADE_MODEL=false
FILTER_JSON=""
BATCH_SIZE=100
TARGET_DIM=""
TARGET_DIST="cosine"

shift 2
while [[ $# -gt 0 ]]; do
    case "$1" in
        --upgrade-model)
            UPGRADE_MODEL=true
            shift
            ;;
        --filter)
            FILTER_JSON="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --target-dim)
            TARGET_DIM="$2"
            shift 2
            ;;
        --target-dist)
            TARGET_DIST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Migration Plan:"
echo "  Source: $SOURCE"
echo "  Target: $TARGET"
echo "  Upgrade model: $UPGRADE_MODEL"
echo "  Batch size: $BATCH_SIZE"
if [[ -n "$FILTER_JSON" ]]; then
    echo "  Filter: $FILTER_JSON"
fi
echo ""

# Check if source exists
echo "Checking source collection..."
SOURCE_INFO=$(curl -s -w "\n%{http_code}" "${QDRANT_URL}/collections/${SOURCE}")
SOURCE_CODE=$(echo "$SOURCE_INFO" | tail -n1)

if [[ "$SOURCE_CODE" != "200" ]]; then
    echo "Error: Source collection '$SOURCE' not found"
    exit 1
fi

SOURCE_DIM=$(echo "$SOURCE_INFO" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('result', {}).get('config', {}).get('params', {}).get('vectors', {}).get('size', 0))")
SOURCE_POINTS=$(echo "$SOURCE_INFO" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('result', {}).get('points_count', 0))")

echo "  Source dimensions: $SOURCE_DIM"
echo "  Source points: $SOURCE_POINTS"

# Determine target dimensions
if [[ -z "$TARGET_DIM" ]]; then
    if [[ "$UPGRADE_MODEL" == true ]]; then
        TARGET_DIM=1536  # text-embedding-3-small default
    else
        TARGET_DIM=$SOURCE_DIM
    fi
fi
echo "  Target dimensions: $TARGET_DIM"

# Check/create target collection
echo ""
echo "Checking target collection..."
TARGET_INFO=$(curl -s -w "\n%{http_code}" "${QDRANT_URL}/collections/${TARGET}")
TARGET_CODE=$(echo "$TARGET_INFO" | tail -n1)

if [[ "$TARGET_CODE" == "200" ]]; then
    echo "  Target exists"
    read -p "Target collection exists. Overwrite? (yes/no): " CONFIRM
    if [[ "$CONFIRM" != "yes" ]]; then
        echo "Cancelled"
        exit 0
    fi
else
    echo "  Creating target collection (${TARGET_DIM}d, $TARGET_DIST)..."
    CREATE_RESP=$(curl -s -w "\n%{http_code}" \
        -X PUT \
        -H "Content-Type: application/json" \
        "${QDRANT_URL}/collections/${TARGET}" \
        -d "{\"vectors\": {\"size\": $TARGET_DIM, \"distance\": \"$TARGET_DIST\"}}")
    
    CREATE_CODE=$(echo "$CREATE_RESP" | tail -n1)
    if [[ "$CREATE_CODE" != "200" ]]; then
        echo "Error: Failed to create target collection"
        exit 1
    fi
    echo "  Target created"
fi

# Migration function
migrate_batch() {
    local offset="$1"
    local limit="$2"
    
    # Scroll points from source
    local scroll_payload="{\"limit\": $limit, \"offset\": $offset, \"with_payload\": true, \"with_vector\": true}"
    
    if [[ -n "$FILTER_JSON" ]]; then
        scroll_payload=$(echo "$scroll_payload" | python3 -c "
import json
import sys
data = json.load(sys.stdin)
data['filter'] = json.loads('$FILTER_JSON')
print(json.dumps(data))
")
    fi
    
    local scroll_resp=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        "${QDRANT_URL}/collections/${SOURCE}/points/scroll" \
        -d "$scroll_payload")
    
    local points=$(echo "$scroll_resp" | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin).get('result', {}).get('points', [])))")
    local point_count=$(echo "$points" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
    
    if [[ "$point_count" -eq 0 ]]; then
        echo "0"
        return
    fi
    
    # Process points
    if [[ "$UPGRADE_MODEL" == true ]]; then
        if [[ -z "$OPENAI_API_KEY" ]]; then
            echo "Error: OPENAI_API_KEY required for model upgrade"
            exit 1
        fi
        
        # Extract texts and re-embed
        local texts=$(echo "$points" | python3 -c "import json,sys; pts=json.load(sys.stdin); print(json.dumps([p.get('payload', {}).get('text', '') for p in pts]))")
        
        local emb_resp=$(curl -s -X POST \
            -H "Authorization: Bearer $OPENAI_API_KEY" \
            -H "Content-Type: application/json" \
            https://api.openai.com/v1/embeddings \
            -d "{\"input\": $texts, \"model\": \"text-embedding-3-small\"}")
        
        local embeddings=$(echo "$emb_resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps([e['embedding'] for e in d.get('data', [])]))")
        
        # Build new points
        points=$(python3 << EOF
import json
points = json.loads('$points')
embeddings = json.loads('$embeddings')
for i, p in enumerate(points):
    p['vector'] = embeddings[i] if i < len(embeddings) else p.get('vector')
print(json.dumps(points))
EOF
)
    fi
    
    # Prepare for upload
    local upload_points=$(echo "$points" | python3 -c "
import json
import sys
points = json.load(sys.stdin)
formatted = []
for p in points:
    formatted.append({
        'id': p['id'],
        'vector': p['vector'],
        'payload': p.get('payload', {})
    })
print(json.dumps({'points': formatted}))
")
    
    # Upload to target
    local upload_resp=$(curl -s -w "\n%{http_code}" \
        -X PUT \
        -H "Content-Type: application/json" \
        "${QDRANT_URL}/collections/${TARGET}/points" \
        -d "$upload_points")
    
    local upload_code=$(echo "$upload_resp" | tail -n1)
    
    if [[ "$upload_code" == "200" ]]; then
        echo "$point_count"
    else
        echo "Error uploading batch" >&2
        echo "0"
    fi
}

# Run migration
echo ""
echo "Starting migration..."
MIGRATED=0
OFFSET=0

while true; do
    COUNT=$(migrate_batch "$OFFSET" "$BATCH_SIZE")
    if [[ "$COUNT" == "Error"* ]] || [[ "$COUNT" == "0" ]]; then
        break
    fi
    MIGRATED=$((MIGRATED + COUNT))
    OFFSET=$((OFFSET + BATCH_SIZE))
    echo "  Migrated: $MIGRATED / $SOURCE_POINTS points"
done

echo ""
echo "Migration complete!"
echo "  Total migrated: $MIGRATED points"
echo "  Target collection: $TARGET"
