#!/bin/bash
# backup.sh - Snapshot and restore Qdrant collections
# Usage: backup.sh <command> [args...]

set -euo pipefail

QDRANT_HOST="${QDRANT_HOST:-localhost}"
QDRANT_PORT="${QDRANT_PORT:-6333}"
QDRANT_URL="http://${QDRANT_HOST}:${QDRANT_PORT}"

COMMAND="${1:-}"

if [[ -z "$COMMAND" ]]; then
    echo "Usage: backup.sh <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  snapshot <collection> [name]  - Create snapshot"
    echo "  restore <collection> <name>   - Restore from snapshot"
    echo "  list <collection>             - List snapshots"
    echo "  delete <collection> <name>    - Delete snapshot"
    echo "  download <collection> <name>  - Download snapshot file"
    exit 1
fi

case "$COMMAND" in
    snapshot)
        COLLECTION="${2:-}"
        SNAPSHOT_NAME="${3:-}"
        
        if [[ -z "$COLLECTION" ]]; then
            echo "Usage: backup.sh snapshot <collection> [snapshot_name]"
            exit 1
        fi
        
        if [[ -z "$SNAPSHOT_NAME" ]]; then
            SNAPSHOT_NAME="snapshot_$(date +%Y%m%d_%H%M%S)"
        fi
        
        echo "Creating snapshot '$SNAPSHOT_NAME' for collection '$COLLECTION'..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X POST \
            -H "Content-Type: application/json" \
            "${QDRANT_URL}/collections/${COLLECTION}/snapshots" \
            -d "{\"snapshot_name\": \"$SNAPSHOT_NAME\"")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')
        
        if [[ "$HTTP_CODE" == "200" || "$HTTP_CODE" == "201" ]]; then
            echo "✓ Snapshot created successfully"
            echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
        else
            echo "✗ Failed to create snapshot (HTTP $HTTP_CODE)"
            echo "$BODY"
            exit 1
        fi
        ;;
        
    restore)
        COLLECTION="${2:-}"
        SNAPSHOT_NAME="${3:-}"
        
        if [[ -z "$COLLECTION" || -z "$SNAPSHOT_NAME" ]]; then
            echo "Usage: backup.sh restore <collection> <snapshot_name>"
            exit 1
        fi
        
        read -p "This will overwrite collection '$COLLECTION'. Continue? (yes/no): " CONFIRM
        if [[ "$CONFIRM" != "yes" ]]; then
            echo "Cancelled"
            exit 0
        fi
        
        echo "Restoring collection '$COLLECTION' from snapshot '$SNAPSHOT_NAME'..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X PUT \
            "${QDRANT_URL}/collections/${COLLECTION}/snapshots/${SNAPSHOT_NAME}/restore")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "✓ Collection restored successfully"
        else
            BODY=$(echo "$RESPONSE" | sed '$d')
            echo "✗ Failed to restore (HTTP $HTTP_CODE)"
            echo "$BODY"
            exit 1
        fi
        ;;
        
    list)
        COLLECTION="${2:-}"
        
        if [[ -z "$COLLECTION" ]]; then
            echo "Usage: backup.sh list <collection>"
            exit 1
        fi
        
        echo "Listing snapshots for collection '$COLLECTION'..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            "${QDRANT_URL}/collections/${COLLECTION}/snapshots")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        BODY=$(echo "$RESPONSE" | sed '$d')
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "$BODY" | python3 -m json.tool
        else
            echo "Error: Failed to list snapshots (HTTP $HTTP_CODE)"
            echo "$BODY"
            exit 1
        fi
        ;;
        
    delete)
        COLLECTION="${2:-}"
        SNAPSHOT_NAME="${3:-}"
        
        if [[ -z "$COLLECTION" || -z "$SNAPSHOT_NAME" ]]; then
            echo "Usage: backup.sh delete <collection> <snapshot_name>"
            exit 1
        fi
        
        read -p "Delete snapshot '$SNAPSHOT_NAME'? (yes/no): " CONFIRM
        if [[ "$CONFIRM" != "yes" ]]; then
            echo "Cancelled"
            exit 0
        fi
        
        echo "Deleting snapshot '$SNAPSHOT_NAME'..."
        
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X DELETE \
            "${QDRANT_URL}/collections/${COLLECTION}/snapshots/${SNAPSHOT_NAME}")
        
        HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
        
        if [[ "$HTTP_CODE" == "200" ]]; then
            echo "✓ Snapshot deleted successfully"
        else
            BODY=$(echo "$RESPONSE" | sed '$d')
            echo "✗ Failed to delete (HTTP $HTTP_CODE)"
            echo "$BODY"
            exit 1
        fi
        ;;
        
    download)
        COLLECTION="${2:-}"
        SNAPSHOT_NAME="${3:-}"
        OUTPUT_PATH="${4:-./$SNAPSHOT_NAME}"
        
        if [[ -z "$COLLECTION" || -z "$SNAPSHOT_NAME" ]]; then
            echo "Usage: backup.sh download <collection> <snapshot_name> [output_path]"
            exit 1
        fi
        
        echo "Downloading snapshot '$SNAPSHOT_NAME' to '$OUTPUT_PATH'..."
        
        curl -L -o "$OUTPUT_PATH" \
            "${QDRANT_URL}/collections/${COLLECTION}/snapshots/${SNAPSHOT_NAME}"
        
        if [[ $? -eq 0 ]]; then
            echo "✓ Download complete: $OUTPUT_PATH"
        else
            echo "✗ Download failed"
            exit 1
        fi
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        echo "Use 'backup.sh' without arguments for help"
        exit 1
        ;;
esac
