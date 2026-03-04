#!/bin/bash
# Vote on Aavegotchi Snapshot proposals via Bankr signature
# Usage: vote.sh <proposal-id> <choice>

set -e

if [ $# -lt 2 ]; then
  echo "Usage: $0 <proposal-id> <choice>"
  echo ""
  echo "Examples:"
  echo "  Single-choice: $0 0xabc123... 2"
  echo "  Weighted:      $0 0xabc123... '{\"2\": 2238}'"
  exit 1
fi

PROPOSAL_ID="$1"
CHOICE="$2"

# Load config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Config file not found: $CONFIG_FILE"
  exit 1
fi

WALLET=$(jq -r '.wallet' "$CONFIG_FILE")
SPACE=$(jq -r '.space' "$CONFIG_FILE")
SNAPSHOT_API=$(jq -r '.snapshotApiUrl' "$CONFIG_FILE")
SEQUENCER=$(jq -r '.snapshotSequencer' "$CONFIG_FILE")

# Get Bankr API key
BANKR_CONFIG="$HOME/.openclaw/skills/bankr/config.json"
if [ ! -f "$BANKR_CONFIG" ]; then
  echo "❌ Bankr config not found: $BANKR_CONFIG"
  exit 1
fi

API_KEY=$(jq -r '.apiKey' "$BANKR_CONFIG")

echo "🗳️  AAVEGOTCHI DAO VOTING"
echo "========================"
echo ""
echo "👤 Wallet: $WALLET"
echo "📋 Proposal: $PROPOSAL_ID"
echo "✅ Choice: $CHOICE"
echo ""

# Get proposal details
echo "🔍 Fetching proposal details..."
PROPOSAL_DATA=$(curl -s -X POST "$SNAPSHOT_API" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"query { proposal(id: \\\"$PROPOSAL_ID\\\") { id title type choices state } }\"
  }")

TITLE=$(echo "$PROPOSAL_DATA" | jq -r '.data.proposal.title')
TYPE=$(echo "$PROPOSAL_DATA" | jq -r '.data.proposal.type')
STATE=$(echo "$PROPOSAL_DATA" | jq -r '.data.proposal.state')
CHOICES=$(echo "$PROPOSAL_DATA" | jq -r '.data.proposal.choices[]')

echo "📝 Title: $TITLE"
echo "🎯 Type: $TYPE"
echo "⚡ State: $STATE"
echo ""

if [ "$STATE" != "active" ]; then
  echo "⚠️  Warning: Proposal is not active (state: $STATE)"
  echo "   Voting may not be accepted"
  echo ""
fi

echo "📊 Available choices:"
echo "$CHOICES" | nl
echo ""

# Check voting power
echo "💪 Checking voting power..."
VP_DATA=$(curl -s -X POST "$SNAPSHOT_API" \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"query { vp(voter: \\\"$WALLET\\\", space: \\\"$SPACE\\\", proposal: \\\"$PROPOSAL_ID\\\") { vp vp_by_strategy } }\"
  }")

VP=$(echo "$VP_DATA" | jq -r '.data.vp.vp')
VP_BY_STRATEGY=$(echo "$VP_DATA" | jq '.data.vp.vp_by_strategy')

echo "   Total VP: $VP"
echo "   Breakdown: $VP_BY_STRATEGY"
echo ""

if [ "$VP" = "0" ] || [ "$VP" = "null" ]; then
  echo "❌ You have 0 voting power on this proposal"
  echo "   Cannot vote"
  exit 1
fi

# Prepare choice based on voting type
CHOICE_VALUE="$CHOICE"

# If it's weighted voting and choice doesn't look like JSON, convert it
if [ "$TYPE" = "weighted" ]; then
  if [[ ! "$CHOICE" =~ ^\{.*\}$ ]]; then
    # Simple number provided, convert to weighted format
    CHOICE_VALUE="{\"$CHOICE\": ${VP%.*}}"
    echo "💡 Converted to weighted format: $CHOICE_VALUE"
    echo ""
  fi
fi

# Build typed data
TIMESTAMP=$(date +%s)

# Determine choice type based on voting type
if [ "$TYPE" = "weighted" ]; then
  CHOICE_TYPE="string"
else
  CHOICE_TYPE="uint32"
  # For single-choice, ensure it's a number
  if [[ "$CHOICE" =~ ^[0-9]+$ ]]; then
    CHOICE_VALUE=$CHOICE
  else
    echo "❌ Single-choice voting requires a number (1, 2, 3, etc.)"
    exit 1
  fi
fi

# Create typed data file
cat > /tmp/vote_typed_data.json <<EOF
{
  "types": {
    "Vote": [
      {"name": "from", "type": "address"},
      {"name": "space", "type": "string"},
      {"name": "timestamp", "type": "uint64"},
      {"name": "proposal", "type": "bytes32"},
      {"name": "choice", "type": "$CHOICE_TYPE"},
      {"name": "reason", "type": "string"},
      {"name": "app", "type": "string"},
      {"name": "metadata", "type": "string"}
    ]
  },
  "domain": {
    "name": "snapshot",
    "version": "0.1.4"
  },
  "primaryType": "Vote",
  "message": {
    "from": "$WALLET",
    "space": "$SPACE",
    "timestamp": $TIMESTAMP,
    "proposal": "$PROPOSAL_ID",
    "choice": $(if [ "$CHOICE_TYPE" = "string" ]; then echo "$CHOICE_VALUE" | jq -R .; else echo "$CHOICE_VALUE"; fi),
    "reason": "",
    "app": "openclaw",
    "metadata": "{}"
  }
}
EOF

echo "📝 Signing vote with Bankr..."

# Sign with Bankr
SIGN_RESPONSE=$(curl -s -X POST "https://api.bankr.bot/agent/sign" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"signatureType\": \"eth_signTypedData_v4\",
    \"typedData\": $(cat /tmp/vote_typed_data.json | jq -c .)
  }")

SIGNATURE=$(echo "$SIGN_RESPONSE" | jq -r '.signature')

if [ "$SIGNATURE" = "null" ] || [ -z "$SIGNATURE" ]; then
  echo "❌ Failed to get signature from Bankr"
  echo "$SIGN_RESPONSE" | jq .
  exit 1
fi

echo "✅ Signature obtained"
echo ""

# Submit to Snapshot
echo "📤 Submitting vote to Snapshot..."

cat > /tmp/vote_payload.json <<PAYLOAD
{
  "address": "$WALLET",
  "sig": "$SIGNATURE",
  "data": $(cat /tmp/vote_typed_data.json | jq -c .)
}
PAYLOAD

VOTE_RESPONSE=$(curl -s -X POST "$SEQUENCER" \
  -H "Content-Type: application/json" \
  -d @/tmp/vote_payload.json)

echo "📬 Response:"
echo "$VOTE_RESPONSE" | jq .
echo ""

# Check result
if echo "$VOTE_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
  VOTE_ID=$(echo "$VOTE_RESPONSE" | jq -r '.id')
  IPFS=$(echo "$VOTE_RESPONSE" | jq -r '.ipfs')
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ VOTE SUCCESSFUL!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📋 Vote ID: $VOTE_ID"
  echo "📦 IPFS: $IPFS"
  echo "🔗 View: https://snapshot.org/#/$SPACE/proposal/$PROPOSAL_ID"
  echo ""
  echo "✅ Your vote has been recorded on Snapshot!"
else
  ERROR=$(echo "$VOTE_RESPONSE" | jq -r '.error_description // .error // "Unknown error"')
  echo "❌ Vote failed: $ERROR"
  exit 1
fi

# Cleanup
rm -f /tmp/vote_typed_data.json /tmp/vote_payload.json
