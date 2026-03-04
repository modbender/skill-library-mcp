#!/bin/bash

# Test Backend API Endpoints
# Verifies that bp-api has the required endpoints for agent dashboard

echo "🧪 Testing Bloom Protocol Backend API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
API_BASE="${BLOOM_API_URL:-https://api.bloomprotocol.ai}"
TEST_AGENT_ID="123"

echo "📋 Configuration:"
echo "   API Base: $API_BASE"
echo "   Test Agent ID: $TEST_AGENT_ID"
echo ""

# Test 1: Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 TEST 1: Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Request: GET $API_BASE/health"
echo ""

HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE/health")
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)

if [ "$HEALTH_CODE" = "200" ]; then
  echo "✅ Health check passed"
  echo "Response: $HEALTH_BODY"
else
  echo "❌ Health check failed (HTTP $HEALTH_CODE)"
  echo "Response: $HEALTH_BODY"
fi
echo ""

# Test 2: Get Agent (should return 404 if not exists, but endpoint should exist)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 TEST 2: Get Agent Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Request: GET $API_BASE/x402/agent/$TEST_AGENT_ID"
echo ""

AGENT_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_BASE/x402/agent/$TEST_AGENT_ID")
AGENT_CODE=$(echo "$AGENT_RESPONSE" | tail -1)
AGENT_BODY=$(echo "$AGENT_RESPONSE" | head -n -1)

if [ "$AGENT_CODE" = "200" ]; then
  echo "✅ Endpoint exists and returned agent data"
  echo "Response: $AGENT_BODY" | jq . 2>/dev/null || echo "$AGENT_BODY"
elif [ "$AGENT_CODE" = "404" ]; then
  echo "✅ Endpoint exists (agent not found is expected for test ID)"
  echo "Response: $AGENT_BODY"
else
  echo "❌ Unexpected response (HTTP $AGENT_CODE)"
  echo "Response: $AGENT_BODY"
  echo ""
  echo "💡 This might mean:"
  echo "   - Endpoint doesn't exist yet"
  echo "   - API routing issue"
  echo "   - CORS issue"
fi
echo ""

# Test 3: Agent Claim Endpoint
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 TEST 3: Agent Claim Endpoint"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Request: POST $API_BASE/x402/agent-claim"
echo "(Will fail without valid signature, but we're just checking if endpoint exists)"
echo ""

CLAIM_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"test": true}' \
  "$API_BASE/x402/agent-claim")
CLAIM_CODE=$(echo "$CLAIM_RESPONSE" | tail -1)
CLAIM_BODY=$(echo "$CLAIM_RESPONSE" | head -n -1)

if [ "$CLAIM_CODE" = "400" ] || [ "$CLAIM_CODE" = "401" ]; then
  echo "✅ Endpoint exists (validation error is expected)"
  echo "Response: $CLAIM_BODY"
elif [ "$CLAIM_CODE" = "404" ]; then
  echo "❌ Endpoint not found"
  echo "Response: $CLAIM_BODY"
else
  echo "⚠️  Unexpected response (HTTP $CLAIM_CODE)"
  echo "Response: $CLAIM_BODY"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Backend API Status:"
echo "   Health: $([ "$HEALTH_CODE" = "200" ] && echo "✅ OK" || echo "❌ Failed")"
echo "   Get Agent: $([ "$AGENT_CODE" = "200" ] || [ "$AGENT_CODE" = "404" ] && echo "✅ OK" || echo "❌ Not Found")"
echo "   Agent Claim: $([ "$CLAIM_CODE" != "404" ] && echo "✅ OK" || echo "❌ Not Found")"
echo ""

if [ "$HEALTH_CODE" = "200" ] && [ "$AGENT_CODE" != "500" ] && [ "$CLAIM_CODE" != "404" ]; then
  echo "🎉 Backend API looks good!"
  echo ""
  echo "Next steps:"
  echo "   1. ✅ Backend ready"
  echo "   2. ⏳ Frontend needs to add /agents/[agentUserId] route"
  echo "   3. ⏳ Deploy frontend to Railway"
else
  echo "⚠️  Backend API needs attention:"
  echo ""
  if [ "$HEALTH_CODE" != "200" ]; then
    echo "   - Health endpoint not working"
  fi
  if [ "$AGENT_CODE" = "500" ]; then
    echo "   - Get Agent endpoint has errors"
  fi
  if [ "$CLAIM_CODE" = "404" ]; then
    echo "   - Agent Claim endpoint not found"
  fi
  echo ""
  echo "Please check backend logs and configuration."
fi
echo ""
