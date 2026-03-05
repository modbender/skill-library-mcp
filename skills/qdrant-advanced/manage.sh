#!/bin/bash
# manage.sh - Qdrant collection management
# Usage: manage.sh <command> [args...]

set -euo pipefail

QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_URL="http://${QDRANT_HOST}:${QDRANT_PORT}"

COMMAND="${1:-}"

if [[ -z "$COMMAND" ]]; then
    echo "Usage: manage.sh <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  list                    - List all collections"
    echo "  create <name> <dim> <distance> - Create collection (dim: 768, 1536, etc)"
    echo "  delete <name>           - Delete collection"
    echo "  info <name>             - Get collection info"
    echo "  optimize <name>         - Optimize collection"
    exit 1
fi

case "$COMMAND" in
    list)
        echo "Fetching collections..."
        RESPONSE=$(curl -s -w "\n%{http_code}" "${QDRANT_URL}/collections")
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "$BODY" | python3 -c "
import json
import sys
data = json.load(sys.stdin)
collections = data.get('result', {}).get('collections', [])

if not collections:
    print('No collections found')
else:
    print(f\"{'Name':<30} {'Points':<10}\")
    print('-' * 40)
    for c in collections:
        name = c.get('name', 'N/A')
        print(f'{name:<30} (fetching...)')
"
            # Get point counts
            echo ""
            echo "Collection details:"
            for name in $(echo "$BODY" | python3 -c "import json,sys; [print(c['name']) for c in json.load(sys.stdin)['result']['collections']]"); do
                INFO=$(curl -s "${QDRANT_URL}/collections/${name}")
                POINTS=$(echo "$INFO" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('result', {}).get('points_count', 0))")
                VECTORS=$(echo "$INFO" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('result', {}).get('config', {}).get('params', {}).get('vectors', {}).get('size', 'N/A'))")
                DISTANCE=$(echo "$INFO" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('result', {}).get('config', {}).get('params', {}).get('vectors', {}).get('distance', 'N/A'))")
                echo "  $name: $POINTS points, ${VECTORS}d, $DISTANCE"
            done
        else
            echo "Error: Failed to list collections (HTTP $HTTP_CODE)"
            echo "$BODY"
            exit 1
        fi
        ;;
        
    create)
        COLLECTION_NAME="${2:-}"
        DIMENSION="${3:-}"
        DISTANCE="${4:-cosine}"
        
        if [[ -z "$COLLECTION_NAME" || -z "$DIMENSION" ]]; then
            echo "Usage: manage.sh create <name> <dimension> [distance]"
            echo ""
            echo "Distances: cosine (default), euclid, dot"
            echo ""
            echo "Examples:"
            echo "  manage.sh create my_collection 1536"
            echo "  manage.sh create my_collection 768 euclid"
            exit 1
        fi
        
        echo "Creating collection '$COLLECTION_NAME' (${DIMENSION}d, $DISTANCE)..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X PUT \
            -H "Content-Type: application/json" \
            "${QDRANT_URL}/collections/${COLLECTION_NAME}" \
            -d "{
                \"vectors\": {
                    \"size\": $DIMENSION,
                    \"distance\": \"$DISTANCE\"
                }
            }")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "✓ Collection created successfully"
            echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
        else
            echo "✗ Failed to create collection (HTTP $HTTP_CODE)"
            echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
            exit 1
        fi
        ;;
        
    delete)
        COLLECTION_NAME="${2:-}"
        
        if [[ -z "$COLLECTION_NAME" ]]; then
            echo "Usage: manage.sh delete <collection_name>"
            exit 1
        fi
        
        read -p "Are you sure you want to delete '$COLLECTION_NAME'? (yes/no): " CONFIRM
        if [[ "$CONFIRM" != "yes" ]]; then
            echo "Cancelled"
            exit 0
        fi
        
        echo "Deleting collection '$COLLECTION_NAME'..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X DELETE \
            "${QDRANT_URL}/collections/${COLLECTION_NAME}")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "✓ Collection deleted successfully"
        else
            BODY=$(echo "$RESPONSE" | sed '$d')
            echo "✗ Failed to delete collection (HTTP $HTTP_CODE)"
            echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
            exit 1
        fi
        ;;
        
    info)
        COLLECTION_NAME="${2:-}"
        
        if [[ -z "$COLLECTION_NAME" ]]; then
            echo "Usage: manage.sh info <collection_name>"
            exit 1
        fi
        
        echo "Fetching collection info for '$COLLECTION_NAME'..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            "${QDRANT_URL}/collections/${COLLECTION_NAME}")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "$BODY" | python3 -m json.tool
        else
            echo "Error: Failed to fetch info (HTTP $HTTP_CODE)"
            echo "$BODY"
            exit 1
        fi
        ;;
        
    optimize)
        COLLECTION_NAME="${2:-}"
        
        if [[ -z "$COLLECTION_NAME" ]]; then
            echo "Usage: manage.sh optimize <collection_name>"
            exit 1
        fi
        
        echo "Optimizing collection '$COLLECTION_NAME'..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X POST \
            "${QDRANT_URL}/collections/${COLLECTION_NAME}/optimizer"")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "✓ Collection optimization triggered"
        else
            BODY=$(echo "$RESPONSE" | sed '$d')
            echo "✗ Failed to optimize (HTTP $HTTP_CODE)"
            echo "$BODY"
            exit 1
        fi
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        echo "Use 'manage.sh' without arguments for help"
        exit 1
        ;;
esac
