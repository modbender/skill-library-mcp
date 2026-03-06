#!/bin/bash
# Unregister this node from the Telnyx mesh registry
# Usage: unregister.sh --name <name> [--bucket <bucket>]

set -e

# Defaults
BUCKET="${TELNYX_MESH_BUCKET:-openclaw-mesh}"
NODE_NAME=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --name|-n)
            NODE_NAME="$2"
            shift 2
            ;;
        --bucket|-b)
            BUCKET="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: unregister.sh --name <name> [--bucket <bucket>]"
            echo ""
            echo "Remove a node from the Telnyx mesh registry."
            echo ""
            echo "Options:"
            echo "  --name, -n    Node name (required)"
            echo "  --bucket, -b  Registry bucket (default: openclaw-mesh)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$NODE_NAME" ]]; then
    echo "❌ --name is required"
    echo "Usage: unregister.sh --name <name>"
    exit 1
fi

# Check telnyx CLI
if ! command -v telnyx &> /dev/null; then
    echo "❌ Telnyx CLI not found. Install with: npm install -g @telnyx/api-cli"
    exit 1
fi

echo "🔄 Unregistering node: $NODE_NAME"

# Delete registration (--force skips confirmation prompt)
if telnyx storage object delete "$BUCKET" "nodes/$NODE_NAME.json" --force 2>/dev/null; then
    echo "✅ Node unregistered"
else
    echo "⚠️  Node not found or already unregistered"
fi
