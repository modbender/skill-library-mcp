#!/bin/bash
# Test script for /functions/v1/submit-ratings
# Run after deploying the Edge Function

set -e

ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
BASE_URL="https://ccyuxrtrklgpkzcryzpj.supabase.co"
CHAT_ID=87

echo "=== OneMind Batch Rating Endpoint Test ==="
echo ""

# Step 1: Anonymous Auth
echo "Step 1: Authenticating..."
AUTH_RESP=$(curl -s -X POST "$BASE_URL/auth/v1/signup" \
  -H "apikey: $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{}')
ACCESS_TOKEN=$(echo "$AUTH_RESP" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
USER_ID=$(echo "$AUTH_RESP" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✓ Got token and user_id"

# Step 2: Join Chat
echo "Step 2: Joining chat..."
JOIN_RESP=$(curl -s -X POST "$BASE_URL/rest/v1/participants" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": $CHAT_ID, \"user_id\": \"$USER_ID\", \"display_name\": \"Test Agent\"}")
echo "✓ Joined chat"

# Step 3: Get Participant ID
echo "Step 3: Getting participant_id..."
PART_RESP=$(curl -s "$BASE_URL/rest/v1/participants?user_id=eq.$USER_ID&chat_id=eq.$CHAT_ID&select=id" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
PARTICIPANT_ID=$(echo "$PART_RESP" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "✓ Got participant_id: $PARTICIPANT_ID"

# Step 4: Get Round Info
echo "Step 4: Finding rating phase round..."
ROUND_RESP=$(curl -s "$BASE_URL/rest/v1/rounds?phase=eq.rating&select=id&limit=1" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
ROUND_ID=$(echo "$ROUND_RESP" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo "✓ Found round: $ROUND_ID"

# Step 5: Get Propositions to Rate
echo "Step 5: Fetching propositions..."
PROP_RESP=$(curl -s "$BASE_URL/rest/v1/propositions?round_id=eq.$ROUND_ID&participant_id=neq.$PARTICIPANT_ID&select=id&limit=3" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
PROP_IDS=($(echo "$PROP_RESP" | grep -o '"id":[0-9]*' | cut -d: -f2))
echo "✓ Found ${#PROP_IDS[@]} propositions"

# Step 6: Submit Batch Ratings (THE NEW ENDPOINT)
echo "Step 6: Testing POST /functions/v1/submit-ratings..."
RATING_RESULT=$(curl -s -X POST "$BASE_URL/functions/v1/submit-ratings" \
  -H "apikey: $ANON_KEY" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"round_id\": $ROUND_ID,
    \"participant_id\": $PARTICIPANT_ID,
    \"ratings\": [
      {\"proposition_id\": ${PROP_IDS[0]}, \"grid_position\": 100},
      {\"proposition_id\": ${PROP_IDS[1]}, \"grid_position\": 0},
      {\"proposition_id\": ${PROP_IDS[2]}, \"grid_position\": 50}
    ]
  }" -w "\nHTTP_CODE:%{http_code}")

echo ""
echo "Response:"
echo "$RATING_RESULT"
echo ""

# Verify success
if echo "$RATING_RESULT" | grep -q '"success":true'; then
  echo "✅ TEST PASSED: Batch rating endpoint working"
else
  echo "❌ TEST FAILED: Check response above"
  exit 1
fi

echo ""
echo "All tests complete!"
