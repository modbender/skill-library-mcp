#!/bin/bash
# Discover nodes registered on the Telnyx mesh
# Usage: discover.sh [--bucket <bucket>] [--json]

set -e

# Defaults
BUCKET="${TELNYX_MESH_BUCKET:-openclaw-mesh}"
OUTPUT_JSON=false

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --bucket|-b)
            BUCKET="$2"
            shift 2
            ;;
        --json|-j)
            OUTPUT_JSON=true
            shift
            ;;
        --help|-h)
            echo "Usage: discover.sh [--bucket <bucket>] [--json]"
            echo ""
            echo "Discover nodes registered on the Telnyx mesh."
            echo ""
            echo "Options:"
            echo "  --bucket, -b  Registry bucket (default: openclaw-mesh)"
            echo "  --json, -j    Output as JSON array"
            echo ""
            echo "Environment:"
            echo "  TELNYX_MESH_BUCKET  Default bucket name"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check telnyx CLI
if ! command -v telnyx &> /dev/null; then
    echo "❌ Telnyx CLI not found. Install with: npm install -g @telnyx/api-cli"
    exit 1
fi

# Check if bucket exists
if ! telnyx storage bucket list 2>/dev/null | grep -q "$BUCKET"; then
    if $OUTPUT_JSON; then
        echo "[]"
    else
        echo "⚠️  No mesh registry found (bucket: $BUCKET)"
        echo "   Register a node first: scripts/register.sh --name <name>"
    fi
    exit 0
fi

# List and fetch all node registrations
NODES=()
TEMP_DIR=$(mktemp -d)

# Get list of node files
NODE_FILES=$(telnyx storage object list "$BUCKET" --prefix "nodes/" 2>/dev/null | grep -oE 'nodes/[^[:space:]]+\.json' || echo "")

if [[ -z "$NODE_FILES" ]]; then
    if $OUTPUT_JSON; then
        echo "[]"
    else
        echo "📭 No nodes registered yet"
        echo "   Register with: scripts/register.sh --name <name>"
    fi
    rm -rf "$TEMP_DIR"
    exit 0
fi

if ! $OUTPUT_JSON; then
    echo "🔍 Discovering nodes on mesh ($BUCKET)..."
    echo ""
    printf "%-15s %-15s %-20s %s\n" "NAME" "IP" "HOSTNAME" "REGISTERED"
    printf "%-15s %-15s %-20s %s\n" "----" "--" "--------" "----------"
fi

JSON_ARRAY="["
FIRST=true

for NODE_FILE in $NODE_FILES; do
    NODE_NAME=$(basename "$NODE_FILE" .json)
    TEMP_FILE="$TEMP_DIR/$NODE_NAME.json"
    
    # Fetch node data
    if telnyx storage object get "$BUCKET" "$NODE_FILE" --output "$TEMP_FILE" 2>/dev/null; then
        if [[ -f "$TEMP_FILE" ]]; then
            NAME=$(python3 -c "import json; d=json.load(open('$TEMP_FILE')); print(d.get('name','unknown'))" 2>/dev/null)
            IP=$(python3 -c "import json; d=json.load(open('$TEMP_FILE')); print(d.get('ip','unknown'))" 2>/dev/null)
            HOSTNAME=$(python3 -c "import json; d=json.load(open('$TEMP_FILE')); print(d.get('hostname','unknown'))" 2>/dev/null)
            REGISTERED=$(python3 -c "import json; d=json.load(open('$TEMP_FILE')); print(d.get('registered_at','unknown'))" 2>/dev/null)
            
            if $OUTPUT_JSON; then
                if ! $FIRST; then
                    JSON_ARRAY+=","
                fi
                JSON_ARRAY+=$(cat "$TEMP_FILE")
                FIRST=false
            else
                # Check if node is reachable (quick ping)
                # Note: ICMP may be blocked in containers/cloud environments
                REACHABLE=""
                if [[ "$IP" != "unknown" ]] && command -v ping &>/dev/null; then
                    if ping -c 1 -W 1 "$IP" &>/dev/null 2>&1; then
                        REACHABLE=" ✅"
                    fi
                fi
                printf "%-15s %-15s %-20s %s%s\n" "$NAME" "$IP" "$HOSTNAME" "${REGISTERED:0:10}" "$REACHABLE"
            fi
        fi
    fi
done

if $OUTPUT_JSON; then
    JSON_ARRAY+="]"
    echo "$JSON_ARRAY" | python3 -m json.tool
else
    echo ""
    echo "💡 Tip: Use --json for machine-readable output"
fi

rm -rf "$TEMP_DIR"
