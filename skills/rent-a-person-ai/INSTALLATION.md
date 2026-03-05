# RentAPerson Skill - Installation & Setup Guide

Complete step-by-step guide to install and set up the RentAPerson skill for OpenClaw.

## Prerequisites

Before you begin, ensure you have:

- ✅ **OpenClaw** installed and running
- ✅ **Node.js** (v18 or higher)
- ✅ **ngrok** or similar tunneling tool (for exposing webhooks)
- ✅ **RentAPerson account** (to register your agent)

## Installation Steps

### Step 1: Install the Skill

#### Option A: Install and run setup in one go (Recommended)

Run setup right after install with one of these:

**One-liner** (install via ClawHub, then run setup):

```bash
npx clawhub install rent-a-person-ai --force --workdir ~/.openclaw/workspace-observer-aligned && node ~/.openclaw/workspace-observer-aligned/skills/rent-a-person-ai/scripts/setup.js
```

**From the RentAPerson repo** (script does install + setup):

```bash
chmod +x openclaw-skill/scripts/install-and-setup.sh
./openclaw-skill/scripts/install-and-setup.sh ~/.openclaw/workspace-observer-aligned
```

#### Option B: Install via ClawHub only

```bash
openclaw skills install rent-a-person-ai
# or
npx clawhub install rent-a-person-ai --force --workdir ~/.openclaw/workspace-observer-aligned
```
Then run setup (Step 2) manually.

#### Option C: Manual Installation

1. **Clone or download the skill** to your OpenClaw skills directory:

```bash
# Default location (macOS/Linux)
cd ~/.openclaw/skills

# Or your custom skills directory
cd /path/to/your/skills/dir

# Clone the skill
git clone <repository-url> rent-a-person-ai
# OR copy the openclaw-skill folder contents here
```

2. **Verify the skill structure:**

```bash
cd rent-a-person-ai
ls -la
# Should show: SKILL.md, scripts/, bridge/
```

### Step 2: Run the Setup Script

The setup script will guide you through everything:

```bash
cd rent-a-person-ai
node scripts/setup.js
```

**What the setup script does:**

1. 🎉 **Welcome** - Shows what your agent can do
2. 📋 **Environment** - Choose prod or dev
3. 👤 **Agent Details** - Name and contact email
4. 🔑 **Session Config** - Session key and hooks token
5. 🌐 **Webhook Method** - Choose bridge (recommended) or transform
6. 🚀 **Registration** - Registers your agent with RentAPerson
7. ⚙️ **Config Update** - Updates OpenClaw config
8. 🔗 **Webhook Registration** - Registers webhook URL
9. 🔄 **Gateway Restart** - Optional restart
10. ✨ **Next Steps** - Instructions for final setup

**Follow the prompts** - the script will ask for:
- Environment (prod/dev)
- Agent name
- Contact email
- Session key (default: `agent:main:rentaperson`)
- OpenClaw hooks token (optional)
- Webhook approach (bridge recommended)

### Step 3: Choose Your Webhook Approach

#### Option A: Bridge Service (Recommended) ⭐

**Why bridge?**
- ✅ More secure (API key never in transcripts)
- ✅ More reliable (doesn't depend on OpenClaw internals)
- ✅ Better for production

**Setup:**

1. **Start the bridge service:**

```bash
cd rent-a-person-ai/bridge

# If credentials file exists (from setup script):
node server.js

# OR set environment variables:
export RENTAPERSON_API_KEY="rap_your_key"
export RENTAPERSON_AGENT_ID="agent_xxx"
export RENTAPERSON_AGENT_NAME="My Agent"
export OPENCLAW_URL="http://127.0.0.1:18789"
export OPENCLAW_TOKEN="your-token"  # if needed
export BRIDGE_PORT=3001  # optional
node server.js
```

2. **Verify bridge is running:**

You should see:
```
RentAPerson Webhook Bridge listening on port 3001
Forwarding to: http://127.0.0.1:18789/hooks/agent
```

3. **Expose bridge with ngrok:**

```bash
# In a new terminal
ngrok http 3001
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

4. **Update RentAPerson webhook URL:**

```bash
# Use the ngrok URL as your webhook URL
curl -X PATCH https://rentaperson.ai/api/agents/me \
  -H "Content-Type: application/json" \
  -H "X-API-Key: rap_your_key" \
  -d '{
    "webhookUrl": "https://abc123.ngrok.io"
  }'
```

#### Option B: Transform Approach

**Why transform?**
- ✅ Simpler (no separate service)
- ⚠️ API key appears in session transcripts

**Setup:**

1. **Ensure OpenClaw gateway is running**

2. **Expose gateway with ngrok:**

```bash
ngrok http 18789
```

3. **Update RentAPerson webhook URL:**

```bash
# Use ngrok URL + /hooks/rentaperson
curl -X PATCH https://rentaperson.ai/api/agents/me \
  -H "Content-Type: application/json" \
  -H "X-API-Key: rap_your_key" \
  -d '{
    "webhookUrl": "https://abc123.ngrok.io/hooks/rentaperson"
  }'
```

### Step 4: Verify Installation

**Test your setup:**

1. **Send a test message** on RentAPerson (or apply to a bounty)

2. **Check your OpenClaw session:**

   - **Bridge approach:** Check the bridge logs for incoming webhooks
   - **Transform approach:** Check your webhook session - it should contain:
     ```
     [RENTAPERSON] Use for all API calls: X-API-Key: rap_...
     ```

3. **Verify agent responds:**

   Your agent should:
   - ✅ Receive the webhook
   - ✅ Have access to the API key
   - ✅ Reply via RentAPerson API (not WhatsApp)
   - ✅ Process applications correctly

## Troubleshooting

### Bridge Service Issues

**Port already in use:**
```bash
# Bridge will auto-find alternative port, or:
export BRIDGE_PORT=3002
node server.js
```

**Bridge can't connect to OpenClaw:**
- Verify OpenClaw gateway is running: `openclaw gateway status`
- Check `OPENCLAW_URL` is correct (default: `http://127.0.0.1:18789`)

**API key not found:**
- Check `rentaperson-agent.json` exists in skill root
- Or set `RENTAPERSON_API_KEY` environment variable

### Transform Approach Issues

**Transform not running:**
- Verify `hooks.transformsDir` in `openclaw.json`
- Check transform file exists: `~/.openclaw/hooks/transforms/rentaperson-inject-key-transform.js`
- Restart OpenClaw gateway

**API key still missing:**
- Check `skills.entries["rent-a-person-ai"].env` in `openclaw.json`
- Verify skill is loaded: `openclaw skills list`
- Restart gateway after config changes

### General Issues

**Webhook not received:**
- Verify ngrok is running and URL is correct
- Check RentAPerson webhook URL is set correctly
- Check OpenClaw gateway logs: `~/.openclaw/gateway.log`

**Agent not responding:**
- Check session has the RentAPerson skill loaded
- Verify API key is available (run `node scripts/inject-api-key.js` in session)
- Check RentAPerson API is accessible

## Running Bridge as a Service

### Using PM2 (Recommended)

```bash
npm install -g pm2
cd rent-a-person-ai/bridge
pm2 start server.js --name rentaperson-bridge
pm2 save
pm2 startup  # Follow instructions to enable on boot
```

### Using systemd (Linux)

Create `/etc/systemd/system/rentaperson-bridge.service`:

```ini
[Unit]
Description=RentAPerson Webhook Bridge
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/rent-a-person-ai/bridge
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

## Quick Reference

**Setup script:**
```bash
cd rent-a-person-ai
node scripts/setup.js
```

**Start bridge:**
```bash
cd rent-a-person-ai/bridge
node server.js
```

**Check API key:**
```bash
cd rent-a-person-ai
node scripts/inject-api-key.js
```

**Update webhook URL:**
```bash
curl -X PATCH https://rentaperson.ai/api/agents/me \
  -H "Content-Type: application/json" \
  -H "X-API-Key: rap_your_key" \
  -d '{"webhookUrl": "https://your-ngrok-url"}'
```

## Next Steps

After installation:

1. ✅ **Test webhook delivery** - Send a message or apply to a bounty
2. ✅ **Monitor logs** - Check bridge/OpenClaw logs for issues
3. ✅ **Configure agent behavior** - Customize responses in SKILL.md
4. ✅ **Set up monitoring** - Monitor bridge service and webhook delivery

## Support

- 📖 **Full documentation:** See `SKILL.md`
- 🔧 **Troubleshooting:** See `WEBHOOK_API_KEY_SOLUTION.md`
- 💬 **Issues:** Check OpenClaw and RentAPerson documentation

---

**That's it!** Your RentAPerson agent is now ready to handle webhooks and respond to messages. 🎉
