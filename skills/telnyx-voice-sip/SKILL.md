---
name: sip-voice-call-control
description: Voice interface using Telnyx Call Control API. Answer phone calls with AI, function calling, and natural conversation. Use for hands-free assistant access, phone-based reminders, or voice-controlled tools. Requires Node.js and Telnyx API key.
metadata: {"openclaw":{"emoji":"📞","requires":{"bins":["node","npm"],"env":["TELNYX_API_KEY"]},"primaryEnv":"TELNYX_API_KEY"}}
---

# SIP Voice Call Control

Voice interface for OpenClaw using Telnyx Call Control API. Call via SIP and have natural conversations with your AI assistant.

## How It Works

```
Your Phone (SIP) → Telnyx Call Control → Webhooks → This Server → Commands back
                         ↓                              ↓
                    STT/TTS/Media              LLM + Tool Execution
```

This is **not WebRTC** — it's server-side SIP call handling. Telnyx handles all audio; we just receive webhooks and send commands.

## Setup

### 1. Install Dependencies

```bash
cd skills/sip-voice-call-control
npm install
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env`:
```env
TELNYX_API_KEY=KEY_your_api_key_here
```

### 3. Start Server

```bash
npm run start
```

Console shows:
```
🎙️  Assistant Voice Server ready on port 3000
📞 Dial: sip:openclaw@yourconnection.sip.telnyx.com
```

## Agent Setup Flow

When setting up for a user, agents should:

### 1. Collect Configuration

Ask for:

1. **Telnyx API Key** (required)
   - Get from: https://portal.telnyx.com/#/app/auth/v2
   - Needs Voice API + Inference permissions

2. **TTS Voice** (optional)
   - `Telnyx.NaturalHD.astra` — Female, warm and clear **(default, recommended)**
   - `Telnyx.NaturalHD.atlas` — Male, deep and authoritative
   - `Polly.Amy-Neural` — British female
   - `Polly.Brian-Neural` — British male
   - `Polly.Joanna-Neural` — American female
   - `Polly.Matthew-Neural` — American male
   - `Azure.en-US-JennyNeural` — American female
   - `Azure.en-GB-RyanNeural` — British male
   - See `.env.example` for full list

3. **Voice Model** (optional)
   - `Qwen/Qwen3-235B-A22B` — Best for function calling (default)
   - `meta-llama/Meta-Llama-3.1-8B-Instruct` — Fastest
   - `meta-llama/Llama-3.3-70B-Instruct` — Balanced

Personalization (assistant name, user name, timezone) is pulled automatically from workspace files (`IDENTITY.md`, `USER.md`).

### 2. Write .env File

```bash
cat > .env << 'EOF'
TELNYX_API_KEY=<user_api_key>
VOICE_MODEL=Qwen/Qwen3-235B-A22B
TTS_VOICE=Telnyx.NaturalHD.astra
EOF
```

### 3. Start in Background (Persistent)

The server must run persistently to receive calls. Use `nohup` to keep it alive:

```bash
cd /path/to/sip-voice-call-control
nohup npm run start > sip-voice-call-control.log 2>&1 &
```

Or from an agent:

```typescript
// Use nohup to keep process alive after session ends
exec({ 
  command: "cd /path/to/sip-voice-call-control && nohup npm run start > sip-voice-call-control.log 2>&1 &",
  background: true 
})
```

**Important:** Without `nohup`, the process will die when the parent session ends. Always use `nohup` or a process manager for production.

To check if running:
```bash
ps aux | grep "tsx.*dev" | grep -v grep
```

To stop:
```bash
pkill -f "tsx.*dev.ts"
```

To view logs:
```bash
tail -f /path/to/sip-voice-call-control/sip-voice-call-control.log
```

### 4. Extract SIP Address

Poll the process logs and give the user the SIP dial-in:
```
📞 Dial: sip:openclaw@<connection>.sip.telnyx.com
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELNYX_API_KEY` | Yes | — | Telnyx API key |
| `VOICE_MODEL` | No | `Qwen/Qwen3-235B-A22B` | Model for inference |
| `TTS_VOICE` | No | `Polly.Amy-Neural` | Text-to-speech voice |
| `PORT` | No | `3000` | Server port |
| `ENABLE_TUNNEL` | No | `true` | Create Cloudflare tunnel |
| `WORKSPACE_DIR` | No | `~/clawd` | For memory search tool |

## Available Tools

| Tool | Trigger Phrases | What It Does |
|------|-----------------|--------------|
| `list_cron_jobs` | "what reminders", "my schedule", "cron jobs" | Lists scheduled tasks |
| `add_reminder` | "remind me", "set a reminder" | Creates new reminder |
| `remove_cron_job` | "delete", "cancel" + job name | Removes a scheduled task |
| `get_weather` | "weather", "temperature", "forecast" | Gets current weather |
| `search_memory` | "what have we been working on", "projects" | Searches workspace files |

## Features

- **Low-latency** — 500ms-1.5s response time with `enable_thinking: false`
- **Barge-in** — Interrupt the assistant anytime by speaking
- **Function calling** — Native tool support with Qwen
- **Auto-setup** — Cloudflare tunnel and Call Control app created automatically
- **Personalization** — Reads `IDENTITY.md` and `USER.md` for context

## Troubleshooting

**No response after speaking:**
- Check Telnyx API key has Voice API + Inference permissions
- Verify webhook URL is reachable (tunnel must be active)

**Slow responses (>3s):**
- Ensure using `function-calling` branch (not `main`)
- Check model availability on your Telnyx account

**Tool not executing:**
- Ensure `openclaw` CLI is in PATH
- Check `WORKSPACE_DIR` is set correctly

**Port already in use:**
- Kill existing server: `pkill -f "tsx.*dev.ts"`
- Or change `PORT` in .env

## Resources

- Telnyx Call Control: https://developers.telnyx.com/docs/voice/call-control
- Telnyx Inference: https://developers.telnyx.com/docs/inference
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
