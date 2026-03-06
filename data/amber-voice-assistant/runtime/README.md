# Amber Voice Assistant Runtime

A production-ready Twilio + OpenAI Realtime SIP bridge that enables voice conversations with an AI assistant. This bridge connects inbound/outbound phone calls to OpenAI's Realtime API and optionally integrates with OpenClaw for brain-in-loop capabilities.

## Features

- **Bidirectional calling**: Handle both inbound call screening and outbound calls with custom objectives
- **OpenAI Realtime API**: Low-latency voice conversations using GPT-4o Realtime
- **OpenClaw integration**: Optional brain-in-loop support for complex queries (calendar, contacts, preferences)
- **Call transcription**: Automatic transcription of both caller and assistant speech
- **Configurable personality**: Customize assistant name, operator info, and greeting styles
- **Call screening modes**: "Friendly" and "GenZ" styles based on caller number
- **Restaurant reservations**: Built-in support for making reservations with structured call plans

## Quick Start

### 1. Prerequisites

- Node.js 18+ (24+ recommended)
- Twilio account with a phone number
- OpenAI account with Realtime API access
- (Optional) OpenClaw gateway running locally
- (Optional) ngrok for easy public URL setup

### 2. Interactive Setup (Recommended) ✨

![Setup Wizard Demo](../demo/demo.gif)

Run the setup wizard for guided installation:

```bash
cd skills/amber-voice-assistant/runtime
npm run setup
```

The wizard will:
- ✅ Validate your Twilio and OpenAI credentials in real-time
- 🌐 Auto-detect and configure ngrok if available
- 📝 Generate a working `.env` file
- 🔧 Optionally install dependencies and build the project
- 📋 Show you exactly where to configure Twilio webhooks

Then just start the server and call your number!

### 3. Manual Configuration (Alternative)

If you prefer to configure manually:

```bash
npm install
cp ../references/env.example .env
```

Edit `.env` with your credentials:

```bash
# Required: Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_CALLER_ID=+15555551234

# Required: OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_PROJECT_ID=proj_xxxxxxxxxxxxxx
OPENAI_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxx
OPENAI_VOICE=alloy

# Required: Server
PORT=8000
PUBLIC_BASE_URL=https://your-domain.com

# Optional: OpenClaw (for brain-in-loop)
OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
OPENCLAW_GATEWAY_TOKEN=your_token

# Optional: Personalization
ASSISTANT_NAME=Amber
OPERATOR_NAME=John Smith
OPERATOR_PHONE=+15555551234
OPERATOR_EMAIL=john@example.com
ORG_NAME=ACME Corp
DEFAULT_CALENDAR=Work
```

### 4. Build

```bash
npm run build
```

### 5. Start

```bash
npm start
```

The bridge will listen on `http://127.0.0.1:8000` (or your configured PORT).

### 6. Expose to the Internet

For Twilio and OpenAI webhooks to reach your bridge, you need a public URL. Options:

**Production**: Use a reverse proxy (nginx, Caddy) with SSL

**Development**: Use ngrok:
```bash
ngrok http 8000
```

Then set `PUBLIC_BASE_URL` in your `.env` to the ngrok URL (e.g., `https://abc123.ngrok.io`).

### 7. Configure Twilio

In your Twilio console, set your phone number's webhook to:
```
https://your-domain.com/twilio/inbound
```

### 8. Configure OpenAI

In your OpenAI Realtime settings, set the webhook URL to:
```
https://your-domain.com/openai/webhook
```

And configure the webhook secret in your `.env`.

## Environment Variables Reference

### Required

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_CALLER_ID` | Your Twilio phone number (E.164 format) |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_PROJECT_ID` | Your OpenAI project ID (for Realtime) |
| `OPENAI_WEBHOOK_SECRET` | Webhook secret from OpenAI Realtime settings |
| `PORT` | Port for the bridge server (default: 8000) |
| `PUBLIC_BASE_URL` | Public URL where this bridge is accessible |

### Optional - OpenClaw Integration

| Variable | Description |
|----------|-------------|
| `OPENCLAW_GATEWAY_URL` | URL of OpenClaw gateway (default: http://127.0.0.1:18789) |
| `OPENCLAW_GATEWAY_TOKEN` | Authentication token for OpenClaw gateway |

When configured, the assistant can delegate complex queries (calendar lookups, contact searches, preference checks) to the OpenClaw agent using the `ask_openclaw` tool during calls.

### Optional - Personalization

| Variable | Description | Default |
|----------|-------------|---------|
| `ASSISTANT_NAME` | Name of the voice assistant | `Amber` |
| `OPERATOR_NAME` | Name of the operator/person being assisted | `your operator` |
| `OPERATOR_PHONE` | Operator's phone number (for fallback info) | (empty) |
| `OPERATOR_EMAIL` | Operator's email (for fallback info) | (empty) |
| `ORG_NAME` | Organization name | (empty) |
| `DEFAULT_CALENDAR` | Default calendar for bookings | (empty) |
| `OPENAI_VOICE` | OpenAI TTS voice (alloy, echo, fable, onyx, nova, shimmer) | `alloy` |

### Optional - Call Screening

| Variable | Description |
|----------|-------------|
| `GENZ_CALLER_NUMBERS` | Comma-separated E.164 numbers for GenZ screening style |

### Optional - Data Persistence

| Variable | Description | Default |
|----------|-------------|---------|
| `OUTBOUND_MAP_PATH` | Path for outbound call metadata | `./data/bridge-outbound-map.json` |

## API Endpoints

### Inbound Calls

- **POST /twilio/inbound** - Twilio webhook for incoming calls
- **POST /twilio/status** - Twilio status callbacks (for debugging)

### Outbound Calls

- **POST /call/outbound** - Initiate an outbound call
  - Body: `{ "to": "+15555551234", "objective": "...", "callPlan": {...} }`

### OpenAI Webhook

- **POST /openai/webhook** - Receives realtime.call.incoming events from OpenAI

### Testing

- **POST /openclaw/ask** - Test the OpenClaw integration
  - Body: `{ "question": "What's on my calendar today?" }`
- **GET /healthz** - Health check endpoint

## How It Connects to OpenClaw

When `OPENCLAW_GATEWAY_URL` and `OPENCLAW_GATEWAY_TOKEN` are configured, the bridge registers an `ask_openclaw` function tool with the OpenAI Realtime session.

During a call, if the AI assistant encounters a question it can't answer from its instructions alone (e.g., "What's my schedule today?"), it will:

1. Call the `ask_openclaw` function with the question
2. The bridge sends the question to OpenClaw's `/v1/chat/completions` endpoint (OpenAI-compatible)
3. OpenClaw (your main agent) processes the question using all its tools (calendar, contacts, memory, etc.)
4. The answer is returned to the bridge
5. The bridge sends the answer back to OpenAI Realtime
6. The assistant speaks the answer to the caller

This enables your voice assistant to access the full context and capabilities of your OpenClaw agent during live phone calls.

If OpenClaw is unavailable or times out, the bridge falls back to a lightweight OpenAI Chat Completions call with basic operator info from environment variables.

## Logs & Transcripts

Call data is stored in the `logs/` directory:

- `{call_id}.jsonl` - Full event stream (JSON Lines format)
- `{call_id}.txt` - Human-readable transcript (CALLER: / ASSISTANT: format)
- `{call_id}.summary.json` - Extracted message summary (if message-taking occurred)

## Development

```bash
# Watch mode (auto-rebuild on changes)
npm run dev

# Type checking
npm run build

# Linting
npm run lint
```

## License

See the main ClawHub repository for license information.

## Support

For issues, questions, or contributions, see the main [ClawHub repository](https://github.com/yourusername/clawhub).
