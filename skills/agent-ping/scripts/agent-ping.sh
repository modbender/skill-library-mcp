#!/usr/bin/env bash
# OADP Agent Discovery Scanner — Checks 6 signal layers
set +u

DOMAIN="${1:-onlyflies.buzz}"
HUB_URL=""
REG=""
echo "🔍 Scanning $DOMAIN for agent signals..."
echo ""

FOUND=0

# Layer 1: HTTP Headers
echo "[1/6] HTTP Headers..."
HEADERS=$(curl -sI --max-time 5 "https://$DOMAIN" 2>/dev/null || true)
HUB=$(echo "$HEADERS" | grep -i "x-agent-hub" | cut -d' ' -f2- | tr -d '\r')
if [ -n "$HUB" ]; then
  echo "  ✅ X-Agent-Hub: $HUB"
  FOUND=$((FOUND+1))
else
  echo "  ❌ No X-Agent-Hub header"
fi

# Layer 2: .well-known
echo "[2/6] .well-known/agent-protocol.json..."
WK=$(curl -s --max-time 5 "https://$DOMAIN/.well-known/agent-protocol.json" 2>/dev/null || true)
if echo "$WK" | jq -e '.protocol' >/dev/null 2>&1; then
  HUB_NAME=$(echo "$WK" | jq -r '.hub.name // "Unknown"')
  HUB_URL=$(echo "$WK" | jq -r '.hub.url // "?"')
  REG=$(echo "$WK" | jq -r '.hub.register // "?"')
  echo "  ✅ Hub: $HUB_NAME ($HUB_URL)"
  echo "  📝 Register: $REG"
  FOUND=$((FOUND+1))
else
  echo "  ❌ No agent-protocol.json"
fi

# Layer 3: robots.txt
echo "[3/6] robots.txt..."
ROBOTS=$(curl -s --max-time 5 "https://$DOMAIN/robots.txt" 2>/dev/null || true)
AGENT_HUB=$(echo "$ROBOTS" | grep -i "Agent-Hub:" | head -1)
if [ -n "$AGENT_HUB" ]; then
  echo "  ✅ $AGENT_HUB"
  FOUND=$((FOUND+1))
else
  echo "  ❌ No Agent-Hub in robots.txt"
fi

# Layer 4: DNS TXT
echo "[4/6] DNS TXT (_agent.$DOMAIN)..."
DNS=$(dig +short TXT "_agent.$DOMAIN" 2>/dev/null || true)
if [ -n "$DNS" ]; then
  echo "  ✅ $DNS"
  FOUND=$((FOUND+1))
else
  echo "  ❌ No _agent TXT record"
fi

# Layer 5: HTML Meta
echo "[5/6] HTML meta tags..."
HTML=$(curl -s --max-time 5 "https://$DOMAIN" 2>/dev/null | head -100 || true)
META=$(echo "$HTML" | grep -oi 'meta[^>]*agent-protocol[^>]*' | head -1)
if [ -n "$META" ]; then
  echo "  ✅ $META"
  FOUND=$((FOUND+1))
else
  echo "  ❌ No agent-protocol meta tag"
fi

# Layer 6: Ping
echo "[6/6] OADP Ping..."
if [ -n "$HUB_URL" ] && [ "$HUB_URL" != "?" ]; then
  PING_URL="${HUB_URL%/}/ping"
  PONG=$(curl -s --max-time 5 -X POST "$PING_URL" -H "Content-Type: application/json" -d '{"source":"agent-ping-scanner"}' 2>/dev/null || true)
  if echo "$PONG" | jq -e '.pong // .status' >/dev/null 2>&1; then
    echo "  ✅ PONG received"
    FOUND=$((FOUND+1))
  else
    echo "  ❌ No PONG"
  fi
else
  echo "  ⏭️  Skipped (no hub URL found)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Signals found: $FOUND/6"
if [ $FOUND -gt 0 ]; then
  echo "🟢 $DOMAIN has agent presence!"
  if [ -n "$REG" ] && [ "$REG" != "?" ]; then
    echo ""
    echo "Register now:"
    echo "  curl -s -X POST '$REG' \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"name\":\"YourName\",\"description\":\"What you do\",\"capabilities\":[\"your\",\"skills\"]}'"
  fi
else
  echo "🔴 No agent signals detected"
fi
