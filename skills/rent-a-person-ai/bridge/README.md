# RentAPerson Webhook Bridge

A separate Node.js service that receives webhooks from RentAPerson, adds the API key to the message, and forwards to OpenClaw. This approach is **more secure** (API key never appears in OpenClaw session transcripts) and **more reliable** (doesn't depend on OpenClaw's transform system).

## Architecture

```
RentAPerson → Bridge Service (port 3001) → OpenClaw Gateway (port 18789)
                ↓
            Adds API key to message
            Logs requests (redacts keys)
            Handles errors gracefully
```

## Setup

### 1. Environment Variables

Set these environment variables:

```bash
export RENTAPERSON_API_KEY="rap_your_key"
export RENTAPERSON_AGENT_ID="agent_xxx"
export RENTAPERSON_AGENT_NAME="My Agent"
export OPENCLAW_URL="http://127.0.0.1:18789"
export OPENCLAW_TOKEN="your-openclaw-hooks-token"
export BRIDGE_PORT=3001  # optional, defaults to 3001
```

**Or** the bridge will auto-load from `../rentaperson-agent.json` if it exists.

### 2. Start the Bridge

```bash
cd bridge
node server.js
# or: npm start
```

The bridge will:
- Listen on port 3001 (or `BRIDGE_PORT`)
- Forward to `OPENCLAW_URL/hooks/agent` (or `/hooks/rentaperson` if mapped)
- Add API key injection to every webhook message (unless disabled, see below)

### 3. Point RentAPerson Webhook

In RentAPerson, set `webhookUrl` to your ngrok URL pointing at the bridge:

```bash
# If bridge runs on localhost:3001, expose with ngrok:
ngrok http 3001

# Then set webhookUrl in RentAPerson to:
# https://abc123.ngrok.io
```

### 4. Verify

Send a test webhook from RentAPerson. Check bridge logs:

```
[2026-02-09T12:00:00.000Z] POST /
Body: { "message": "...", "name": "..." }
```

The bridge will forward to OpenClaw with the API key injected.

## Benefits

- ✅ **Security**: API key never appears in OpenClaw session transcripts
- ✅ **Reliability**: Doesn't depend on OpenClaw transform system
- ✅ **Debugging**: Centralized logs (keys redacted)
- ✅ **Flexibility**: Can add retry logic, rate limiting, etc.
- ✅ **Simplicity**: Single Node.js file, no dependencies

## Running as a Service

### systemd (Linux)

Create `/etc/systemd/system/rentaperson-bridge.service`:

```ini
[Unit]
Description=RentAPerson Webhook Bridge
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/openclaw-skill/bridge
Environment="RENTAPERSON_API_KEY=rap_xxx"
Environment="OPENCLAW_URL=http://127.0.0.1:18789"
Environment="OPENCLAW_TOKEN=xxx"
ExecStart=/usr/bin/node server.js
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl enable rentaperson-bridge
sudo systemctl start rentaperson-bridge
```

### PM2

```bash
pm2 start server.js --name rentaperson-bridge
pm2 save
pm2 startup
```

## Troubleshooting

**Bridge not receiving webhooks:**
- Check ngrok is running and forwarding to port 3001
- Verify `webhookUrl` in RentAPerson points to ngrok URL
- Check bridge logs for incoming requests

**OpenClaw not receiving forwarded webhooks:**
- Verify `OPENCLAW_URL` is correct
- Check OpenClaw gateway is running
- Verify `OPENCLAW_TOKEN` is correct (if required)

**API key not injected:**
- Check `RENTAPERSON_API_KEY` env var or `rentaperson-agent.json`
- Verify credentials are loaded (check bridge startup logs)
- If you set `INJECT_API_KEY=false`, key injection is disabled (use this if main session has key in env)

**Disabling API key injection (if main session has key in env):**

If your main session has `RENTAPERSON_API_KEY` in env (set during setup in `openclaw.json`), you can disable key injection in the bridge:

```bash
export INJECT_API_KEY=false
```

Or in `rentaperson-agent.json`:
```json
{
  "injectApiKey": false
}
```

This is recommended if the main session already has the key in env—no need to include it in every webhook message.
