# Verify Webhook Setup

## Quick Verification Steps

### 1. Check if ngrok is running
```bash
# Check ngrok web interface
open http://127.0.0.1:4040
# Or visit in browser: http://127.0.0.1:4040
```

### 2. Check which port ngrok is forwarding to
In the ngrok web interface, you should see:
- **Forwarding**: `https://velia-regardable-reed.ngrok-free.dev -> http://localhost:XXXX`
- Note the port number (should be 3001 for bridge or 18789 for gateway)

### 3. Verify bridge/gateway is running

**If using Bridge:**
```bash
# Check if bridge is running
ps aux | grep "bridge/server.js"
# Or check port 3001
lsof -i :3001
```

**If using Transform (OpenClaw gateway):**
```bash
# Check if OpenClaw gateway is running
openclaw gateway status
# Or check port 18789
lsof -i :18789
```

### 4. Test webhook manually

**Option A: Using curl**
```bash
curl -X POST https://velia-regardable-reed.ngrok-free.dev \
  -H "Content-Type: application/json" \
  -d '{
    "event": "message.received",
    "conversationId": "test_123",
    "humanId": "test_user",
    "contentPreview": "Test message"
  }'
```

**Option B: Using the test script**
```bash
cd openclaw-skill/scripts
node test-webhook.js https://velia-regardable-reed.ngrok-free.dev
```

### 5. Check OpenClaw session

After sending the test webhook:
1. Open your OpenClaw session (the one you configured: `agent:main:rentaperson` or your main session)
2. Look for the test message
3. Verify it contains: `[RENTAPERSON] Use for all API calls: X-API-Key: ...`

### 6. Common Issues

**ngrok-free.dev requires browser verification:**
- Visit `https://velia-regardable-reed.ngrok-free.dev` in your browser first
- Click through the ngrok warning page
- Then webhooks will work

**401 Unauthorized:**
- Check your `webhookBearerToken` matches OpenClaw's hooks token
- Verify token is set in RentAPerson agent config

**404 Not Found:**
- Bridge: Should be root `/` (no path)
- Transform: Should be `/hooks/rentaperson`

**Connection refused:**
- Bridge/gateway not running
- Wrong port in ngrok forwarding

## Expected Flow

1. ✅ ngrok receives webhook → forwards to local port
2. ✅ Bridge/gateway receives webhook → processes it
3. ✅ API key injected → message enhanced
4. ✅ OpenClaw session receives → agent can see key
5. ✅ Agent responds → via RentAPerson API
