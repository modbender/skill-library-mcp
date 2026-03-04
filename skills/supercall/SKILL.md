---
name: supercall
description: Make AI-powered phone calls with custom personas and goals. Uses OpenAI Realtime API + Twilio for ultra-low latency voice conversations. Supports DTMF/IVR navigation — the AI can navigate automated phone menus by sending touch-tone digits. Use when you need to call someone, confirm appointments, deliver messages, navigate phone trees, or have the AI handle phone conversations autonomously. Unlike the standard voice_call plugin, the person on the call doesn't have access to gateway agent, reducing attack surfaces.
homepage: https://github.com/xonder/supercall
metadata:
  {
    "openclaw":
      {
        "emoji": "📞",
        "requires": { 
          "plugins": ["supercall"],
          "env": ["OPENAI_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"],
          "anyBins": ["ngrok", "tailscale"]
        },
        "primaryEnv": "OPENAI_API_KEY",
        "install":
          [
            {
              "id": "npm",
              "kind": "node",
              "package": "@xonder/supercall",
              "label": "Install supercall plugin (npm)",
            },
          ],
      },
  }
---

# SuperCall

Make AI-powered phone calls with custom personas and goals using OpenAI Realtime API + Twilio.

## Features

- **Persona Calls**: Define a persona, goal, and opening line for autonomous calls
- **Full Realtime Mode**: GPT-4o powered voice conversations with <~1s latency
- **DTMF / IVR Navigation**: AI automatically navigates automated phone menus (press 1 for X, enter your account number, etc.) by generating and injecting touch-tone digits into the audio stream
- **Provider**: Supports Twilio (full realtime) and mock provider for testing
- **Streaming Audio**: Bidirectional audio via WebSocket for real-time conversations
- **Limited Access**: Unlike the standard voice_call plugin, the person on the call doesn't have access to gateway agent, reducing attack surfaces.

## Credentials

### Required

| Credential | Source | Purpose |
|------------|--------|---------|
| `OPENAI_API_KEY` | [OpenAI](https://platform.openai.com/api-keys) | Powers the realtime voice AI (GPT-4o) |
| `TWILIO_ACCOUNT_SID` | [Twilio Console](https://console.twilio.com) | Twilio account identifier |
| `TWILIO_AUTH_TOKEN` | [Twilio Console](https://console.twilio.com) | Twilio API authentication |

### Optional

| Credential | Source | Purpose |
|------------|--------|---------|
| `NGROK_AUTHTOKEN` | [ngrok](https://dashboard.ngrok.com) | ngrok tunnel auth (only needed if using ngrok as tunnel provider) |

Credentials can be set via environment variables or in the plugin config (config takes precedence).

## Installation

1. Install the plugin via npm or copy to your OpenClaw extensions directory

2. **Enable hooks** for call completion callbacks (required):

```json
{
  "hooks": {
    "enabled": true,
    "token": "your-secret-token"
  }
}
```

Generate a secure token with: `openssl rand -hex 24`

> ⚠️ **Security**: The `hooks.token` is sensitive — it authenticates internal callbacks. Keep it secret and rotate if compromised.

3. Configure the plugin in your openclaw config:

```json
{
  "plugins": {
    "entries": {
      "supercall": {
        "enabled": true,
        "config": {
          "provider": "twilio",
          "fromNumber": "+15551234567",
          "twilio": {
            "accountSid": "your-account-sid",
            "authToken": "your-auth-token"
          },
          "streaming": {
            "openaiApiKey": "your-openai-key"
          },
          "tunnel": {
            "provider": "ngrok",
            "ngrokDomain": "your-domain.ngrok.app"
          }
        }
      }
    }
  }
}
```

**Important**: The `hooks.token` is required for call completion callbacks. Without it, the agent won't be notified when calls finish.

## Tool: supercall

Make phone calls with custom personas:

```
supercall(
  action: "persona_call",
  to: "+1234567890",
  persona: "Personal assistant to the king",
  goal: "Confirm the callee's availabilities for dinner next week",
  openingLine: "Hey, this is Michael, Alex's Assistant..."
)
```

### Actions

- `persona_call` - Start a new call with a persona
- `get_status` - Check call status and transcript
- `end_call` - End an active call
- `list_calls` - List active persona calls

### DTMF / IVR Navigation

The AI automatically handles automated phone menus (IVR systems) during calls. When it hears prompts like "press 1 for sales", it uses an internal `send_dtmf` tool to send touch-tone digits through the audio stream. This is fully automatic — no extra configuration or agent intervention is needed.

- **Supported characters**: `0-9`, `*`, `#`, `A-D`, `w` (500ms pause)
- **Example sequences**: `1` (press 1), `1234567890#` (enter account number + pound), `1w123#` (press 1, wait, then enter 123#)
- **How it works**: DTMF tones are generated as ITU-standard dual-frequency pairs, encoded to µ-law (8kHz mono), and injected directly into the Twilio media stream. No external dependencies.

This means persona calls can navigate phone trees end-to-end — e.g., "call the pharmacy, navigate through their menu, and check on my prescription status."

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `provider` | Voice provider (twilio/mock) | Required |
| `fromNumber` | Caller ID (E.164 format) | Required for real providers |
| `toNumber` | Default recipient number | - |
| `twilio.accountSid` | Twilio Account SID | TWILIO_ACCOUNT_SID env |
| `twilio.authToken` | Twilio Auth Token | TWILIO_AUTH_TOKEN env |
| `streaming.openaiApiKey` | OpenAI API key for realtime | OPENAI_API_KEY env |
| `streaming.silenceDurationMs` | VAD silence duration in ms | 800 |
| `streaming.vadThreshold` | VAD threshold 0-1 (higher = less sensitive) | 0.5 |
| `streaming.streamPath` | WebSocket path for media stream | /voice/stream |
| `tunnel.provider` | Tunnel for webhooks (ngrok/tailscale-serve/tailscale-funnel) | none |
| `tunnel.ngrokDomain` | Fixed ngrok domain (recommended for production) | - |
| `tunnel.ngrokAuthToken` | ngrok auth token | NGROK_AUTHTOKEN env |
Full realtime requires an OpenAI API key.

## Requirements

- Node.js 20+
- Twilio account for full realtime calls (media streams)
- ngrok or Tailscale for webhook tunneling (production)
- OpenAI API key for real-time features

## Architecture

This is a fully standalone skill - it does not depend on the built-in voice-call plugin. All voice calling logic is self-contained.

## Runtime Behavior and Security

This plugin is **not** instruction-only. It runs code, spawns processes, opens network listeners, and writes to disk. The following describes exactly what happens at runtime.

### Process spawning

When `tunnel.provider` is set to `ngrok`, the plugin spawns the `ngrok` CLI binary via `child_process.spawn`. When set to `tailscale-serve` or `tailscale-funnel`, it spawns the `tailscale` CLI instead. These processes run for the lifetime of the plugin and are terminated on shutdown. If `tunnel.provider` is `none` (or a `publicUrl` is provided directly), no external processes are spawned.

### Network activity

- **Local webhook server**: The plugin opens an HTTP server (default `0.0.0.0:3335`) to receive Twilio webhook callbacks and WebSocket media streams.
- **Startup self-test**: On startup, the plugin sends an HTTP POST to its own public webhook URL with an `x-supercall-self-test` header to verify connectivity. If `publicUrl` is misconfigured to point at an unintended endpoint, this self-test token could be sent there. Always verify your `publicUrl` or tunnel configuration before starting.
- **Outbound API calls**: The plugin makes outbound requests to the OpenAI Realtime API (WebSocket) and Twilio REST API during calls.

### Webhook verification

- **Twilio calls**: Verified using Twilio's X-Twilio-Signature header (HMAC-SHA1).
- **Self-test requests**: Authenticated using an internal token (`x-supercall-self-test`) generated at startup.
- **ngrok free-tier relaxation**: On free-tier ngrok domains (`.ngrok-free.app`, `.ngrok.io`), URL reconstruction may vary due to ngrok's request rewriting; Twilio signature mismatches are logged but allowed through. Paid/custom ngrok domains (`.ngrok.app`) are verified strictly. This relaxation is limited to free-tier domains only and does not affect Tailscale or direct `publicUrl` configurations.

### Data at rest

Call transcripts are persisted to `~/clawd/supercall-logs`. These logs may contain sensitive conversation content. Review and rotate logs periodically.

### Best practices

- **Protect your credentials** — Twilio and OpenAI keys grant access to paid services
- **Verify your public URL** — ensure `publicUrl` or tunnel config points where you expect before starting
- **Rotate `hooks.token`** periodically and if you suspect compromise
- **Review call logs** — transcripts stored on disk may contain sensitive content
