# elevenlabs-twilio-memory-bridge

A lightweight production bridge that adds **persistent caller memory** and **dynamic context injection** to ElevenLabs Conversational AI agents connected via Twilio phone numbers.

## Architecture

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   Caller     │──────▶│     Twilio        │──────▶│   ElevenLabs     │
│  (Phone)     │◀──────│  (Phone Number)   │◀──────│  Conversational  │
└──────────────┘       └──────────────────┘       │       AI         │
                              │                    │                  │
                              │ Native integration │   STT → LLM → TTS│
                              │ (no code needed)   │                  │
                              └────────────────────┤                  │
                                                   │                  │
                         ┌─────────────────────────│──────────────────┘
                         │ Personalization webhook  │
                         ▼                          │
                  ┌──────────────────┐              │
                  │  THIS SERVICE    │              │
                  │  (Memory Bridge) │              │
                  │                  │    ┌─────────▼─────────┐
                  │  /webhook/       │    │   OpenClaw / LLM   │
                  │   personalize    │    │  (your instance)   │
                  │                  │    └───────────────────┘
                  │  Sessions │ Memory│
                  │  Notes    │ Soul  │
                  └──────────────────┘
                         │
                    ./data/ (JSON)
```

**Key insight:** ElevenLabs handles ALL real-time audio streaming directly with Twilio via their native integration. This service only runs the personalization webhook — it never touches audio data. This keeps the bridge tiny, fast, and cheap to host.

### How it works

1. A caller dials your Twilio number
2. Twilio routes the call to ElevenLabs via their native integration
3. ElevenLabs calls **your webhook** (`/webhook/personalize`) with caller metadata
4. Your webhook looks up the caller's memory, session history, and daily notes
5. It returns personalized context (system prompt override + dynamic variables)
6. ElevenLabs starts the conversation with full caller context injected
7. The LLM backend is your **OpenClaw** instance (or any OpenAI-compatible endpoint)

## Prerequisites

- **Python 3.10+**
- **Twilio account** with a purchased phone number
- **ElevenLabs account** with a Conversational AI agent configured
- **OpenClaw instance** (or any OpenAI-compatible LLM gateway) reachable via HTTPS
- **Public URL** for this service (Cloudflare Tunnel, ngrok, Railway, etc.)

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/britrik/elevenlabs-twilio-memory-bridge.git
cd elevenlabs-twilio-memory-bridge
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Configure your ElevenLabs agent

1. Go to the [ElevenLabs Agents dashboard](https://elevenlabs.io/app/agents)
2. Create or select an agent
3. Under **Agent → LLM**, select **Custom LLM** and point it to your OpenClaw instance:
   - URL: `https://your-openclaw-instance.example.com/v1/chat/completions`
   - Add your OpenClaw API key as a secret
4. Under **Security → Overrides**, enable:
   - ✅ System prompt
   - ✅ First message
5. Under **Settings → Webhooks**, add your personalization webhook:
   - URL: `https://your-bridge.example.com/webhook/personalize`
   - Add your `WEBHOOK_SECRET` as a header secret if desired

### 4. Import your Twilio number into ElevenLabs

1. In ElevenLabs, go to **Phone Numbers**
2. Add your Twilio number with your Account SID and Auth Token
3. Assign it to your configured agent
4. ElevenLabs automatically configures Twilio webhooks — no manual TwiML setup needed

### 5. Run the service

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 6. Expose publicly

**Cloudflare Tunnel (recommended for production):**
```bash
cloudflared tunnel --url http://localhost:8000
```

**ngrok (for testing):**
```bash
ngrok http 8000
```

Update `PUBLIC_BASE_URL` in your `.env` to match the tunnel URL.

### 7. Test it

1. Call your Twilio number
2. The agent should answer with personalized context
3. Hang up, call again — the agent remembers your previous interaction
4. Add a memory via the API:
   ```bash
   curl -X POST http://localhost:8000/api/memory/PHONE_HASH \
     -H "Content-Type: application/json" \
     -d '{"fact": "Prefers to be called Mike"}'
   ```
5. Call again — the agent now knows your preference

## API Reference

### `POST /webhook/personalize`
ElevenLabs calls this automatically when a Twilio call arrives.

**Request body** (from ElevenLabs):
```json
{
  "caller_id": "+15551234567",
  "agent_id": "agent_abc123",
  "called_number": "+15559876543",
  "call_sid": "CA1234567890abcdef"
}
```

**Response** (to ElevenLabs):
```json
{
  "type": "conversation_initiation_client_data",
  "dynamic_variables": {
    "caller_name": "Unknown",
    "session_id": "a1b2c3d4-...",
    "call_count": "3"
  },
  "conversation_config_override": {
    "agent": {
      "prompt": {
        "prompt": "... soul template + memory + notes ..."
      },
      "first_message": "Hi there! Welcome back."
    }
  }
}
```

### `POST /webhook/post-call`
Optional post-call webhook to log call completion.

### `GET /health`
Returns `{"status": "ok"}`.

### `POST /api/memory/{phone_hash}`
Add a long-term fact about a caller.
```json
{"fact": "Allergic to peanuts"}
```

### `POST /api/notes`
Add a daily context note (global or caller-specific).
```json
{"note": "Office closed today for holiday", "phone_hash": null}
```

## Project Structure

```
elevenlabs-twilio-memory-bridge/
├── app.py                 # FastAPI application & webhook endpoints
├── memory.py              # File-based session, memory, and notes persistence
├── soul_template.md       # Default agent personality template
├── requirements.txt       # Python dependencies
├── manifest.json          # ClawHub skill metadata
├── .env.example           # Environment variable template
├── .gitignore             # Git exclusions
├── README.md              # This file
└── data/                  # Runtime data (git-ignored)
    ├── sessions/          # Per-caller session JSON files
    ├── memories/          # Per-caller long-term facts
    └── notes/             # Daily context notes
```

## Security

- **Never commit `.env`** — it's git-ignored by default
- **Hash all phone numbers** — only SHA-256 hashes are stored/logged
- **Use scoped API keys** — limit ElevenLabs and OpenClaw keys to minimum required permissions
- **HTTPS only** — both OpenClaw and the bridge should be behind TLS in production
- **Webhook verification** — set `WEBHOOK_SECRET` and configure it in ElevenLabs settings
- **No secrets in source** — all configurable values come from environment variables

## Deployment Options

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### systemd
```ini
[Unit]
Description=ElevenLabs Twilio Memory Bridge
After=network.target

[Service]
User=bridge
WorkingDirectory=/opt/elevenlabs-twilio-memory-bridge
EnvironmentFile=/opt/elevenlabs-twilio-memory-bridge/.env
ExecStart=/opt/elevenlabs-twilio-memory-bridge/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## ClawHub Installation

This skill is available on [ClawHub](https://clawhub.com). To install:

1. Search for `elevenlabs-twilio-memory-bridge`
2. Follow the install steps to clone and configure
3. Set the required environment variables
4. Run the service and point ElevenLabs at your webhook URL

## License

MIT
