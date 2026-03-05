#!/bin/bash
# Register this node on the Telnyx mesh registry
# Usage: register.sh --name <name> [--bucket <bucket>]

set -e

# Defaults
BUCKET="${TELNYX_MESH_BUCKET:-openclaw-mesh}"
NODE_NAME=""
METADATA=""

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
        --meta|-m)
            METADATA="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: register.sh --name <name> [--bucket <bucket>] [--meta <json>]"
            echo ""
            echo "Register this node on the Telnyx mesh registry."
            echo ""
            echo "Options:"
            echo "  --name, -n    Node name (required)"
            echo "  --bucket, -b  Registry bucket (default: openclaw-mesh)"
            echo "  --meta, -m    Additional metadata as JSON"
            echo ""
            echo "Environment:"
            echo "  TELNYX_MESH_BUCKET  Default bucket name"
            echo ""
            echo "Example:"
            echo "  register.sh --name home-server"
            echo "  register.sh --name laptop --meta '{\"owner\":\"john\"}'"
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
    echo "Usage: register.sh --name <name>"
    exit 1
fi

# Check telnyx CLI
if ! command -v telnyx &> /dev/null; then
    echo "❌ Telnyx CLI not found. Install with: npm install -g @telnyx/api-cli"
    exit 1
fi

# Get WireGuard interface IP
WG_IP=""
if command -v wg &> /dev/null; then
    # Try to get IP from telnyx0 interface
    # macOS uses ifconfig, Linux uses ip
    if command -v ip &> /dev/null; then
        WG_IP=$(ip -4 addr show telnyx0 2>/dev/null | grep -oE 'inet [0-9.]+' | awk '{print $2}')
    fi
    if [[ -z "$WG_IP" ]] && command -v ifconfig &> /dev/null; then
        WG_IP=$(ifconfig telnyx0 2>/dev/null | grep -oE 'inet [0-9.]+' | awk '{print $2}')
    fi
fi

if [[ -z "$WG_IP" ]]; then
    echo "⚠️  Could not detect WireGuard IP. Is the mesh running?"
    echo "   Run: scripts/join.sh --name $NODE_NAME --apply"
    exit 1
fi

# Build registration JSON
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HOSTNAME=$(hostname)

REG_JSON=$(cat <<EOF
{
  "name": "$NODE_NAME",
  "ip": "$WG_IP",
  "hostname": "$HOSTNAME",
  "registered_at": "$TIMESTAMP",
  "metadata": ${METADATA:-null}
}
EOF
)

echo "🔄 Registering node on mesh..."
echo "   Name: $NODE_NAME"
echo "   IP: $WG_IP"
echo "   Bucket: $BUCKET"

# Ensure bucket exists
if ! telnyx storage bucket list 2>/dev/null | grep -q "$BUCKET"; then
    echo "📦 Creating registry bucket: $BUCKET"
    telnyx storage bucket create "$BUCKET" > /dev/null
fi

# Write registration
TEMP_FILE=$(mktemp)
echo "$REG_JSON" > "$TEMP_FILE"
telnyx storage object put "$BUCKET" "$TEMP_FILE" -k "nodes/$NODE_NAME.json" > /dev/null
rm "$TEMP_FILE"

echo ""
echo "✅ Node registered!"
echo ""
echo "Other nodes can discover you with:"
echo "   scripts/discover.sh"
echo ""
echo "Registration:"
echo "$REG_JSON" | python3 -m json.tool 2>/dev/null || echo "$REG_JSON"
