#!/bin/bash
set -euo pipefail

# gotchi-equip: Show currently equipped wearables on an Aavegotchi
# Usage: show-equipped.sh <gotchi-id>
# Example: show-equipped.sh 9638

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Validate inputs
if [ $# -ne 1 ]; then
    echo "❌ Usage: show-equipped.sh <gotchi-id>"
    echo ""
    echo "Example:"
    echo "  show-equipped.sh 9638"
    exit 1
fi

GOTCHI_ID="$1"

echo "👻 Fetching Equipped Wearables for Gotchi #$GOTCHI_ID"
echo ""
echo "==================================================================="

# Query subgraph for equipped wearables
SUBGRAPH_URL="https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn"

QUERY=$(cat <<EOF
{
  "query": "{ aavegotchi(id: \"$GOTCHI_ID\") { id name equippedWearables } }"
}
EOF
)

RESPONSE=$(curl -s "$SUBGRAPH_URL" -H 'content-type: application/json' --data "$QUERY")

# Parse response
NAME=$(echo "$RESPONSE" | jq -r '.data.aavegotchi.name // "Unknown"')
EQUIPPED=$(echo "$RESPONSE" | jq -r '.data.aavegotchi.equippedWearables // []')

if [ "$NAME" = "Unknown" ] || [ "$NAME" = "null" ]; then
    echo "❌ Gotchi #$GOTCHI_ID not found"
    exit 1
fi

echo "Gotchi: #$GOTCHI_ID \"$NAME\""
echo ""
echo "🎭 Equipped Wearables:"
echo ""

# Parse equipped wearables array
SLOTS=("Body" "Face" "Eyes" "Head" "Left Hand" "Right Hand" "Pet" "Background")

for i in {0..7}; do
    WEARABLE_ID=$(echo "$EQUIPPED" | jq -r ".[$i] // 0")
    if [ "$WEARABLE_ID" != "0" ] && [ "$WEARABLE_ID" != "null" ]; then
        echo "   ${SLOTS[$i]}: Wearable ID $WEARABLE_ID"
    fi
done

echo ""
echo "==================================================================="
