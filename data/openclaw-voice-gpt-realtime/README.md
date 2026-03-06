# openclaw-voice-gpt-realtime

Ultra-low-latency AI phone calls powered by OpenAI's Realtime API for [OpenClaw](https://github.com/openclaw).

Replaces the traditional multi-step voice pipeline (STT -> LLM -> TTS) with a single speech-to-speech model, cutting response latency from ~500-1000ms+ down to **~200-300ms**.

## Architecture

```
User (via iMessage/CLI) --> OpenClaw Agent --> make_phone_call tool
                                                |
                                       Plugin: initiateCall()
                                                |
                                       Twilio REST API --> PSTN --> Business
                                                | (call answered)
                                       Twilio hits /voice/answer webhook
                                                |
                                       Returns TwiML: <Connect><Stream>
                                                |
                              Twilio WebSocket <--> Plugin WebSocket Server
                                                |
                              OpenAI Realtime API WebSocket (gpt-realtime)
                                   g711_ulaw passthrough, zero transcoding
                                   Function calling (DTMF, end_call, report)
```

**Before (old pipeline):** Twilio audio -> OpenAI STT -> LLM (gpt-4.1-mini) -> ElevenLabs TTS -> Twilio audio (~500-1000ms+)

**After (this plugin):** Twilio audio -> OpenAI Realtime (gpt-realtime) -> Twilio audio (~200-300ms)

## Features

- **~200-300ms response latency** — Single model inference, zero transcoding
- **Natural voice** — OpenAI's `coral` voice (configurable: alloy, ash, ballad, coral, echo, sage, shimmer, verse)
- **"Listen first" outbound behavior** — AI waits for the callee to answer before speaking
- **Agent-driven prompts with safety wrapper** — Custom prompts are sanitized/truncated and wrapped with non-overridable safety rules
- **IVR navigation** — DTMF tone generation for navigating phone menus
- **Voicemail detection** — Leaves a brief message and hangs up
- **Inbound calls** — Optionally receive calls with configurable allowlist policy
- **Barge-in** — Caller can interrupt the AI mid-sentence
- **Structured outcomes** — Calls report success/failure with details (confirmation numbers, prices, etc.)
- **Call transcripts** — Full transcript logging with timestamps
- **Debug mode** — Call recording, verbose WebSocket logging, latency metrics
- **Status checker** — Built-in verification of Twilio, OpenAI, tunnel, and server

## Quick Start

### 1. Install

```bash
npx clawhub@latest install openclaw-voice-gpt-realtime
```

Or install from source for development:

```bash
git clone https://github.com/connorcallison/openclaw-voice-gpt-realtime.git
cd openclaw-voice-gpt-realtime
bun install
openclaw plugins install -l .
```

### 2. Configure

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "openclaw-voice-gpt-realtime": {
        "enabled": true,
        "config": {
          "twilio": {
            "accountSid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "authToken": "your-auth-token"
          },
          "fromNumber": "+17075551234",
          "openai": {
            "apiKey": "sk-proj-...",
            "voice": "coral"
          },
          "publicUrl": "https://your-domain.com"
        }
      }
    }
  }
}
```

`publicUrl` must be an HTTPS origin only (no path/query), and cannot be localhost/private/internal.

### 3. Set Up Tunnel

The plugin needs a public URL so Twilio can reach its webhook server. Any tunneling solution works:

```yaml
# Cloudflare Tunnel example
- hostname: your-domain.com
  path: /voice/realtime-stream
  service: http://localhost:3335
  originRequest:
    noTLSVerify: true
    connectTimeout: 300s
    keepAliveTimeout: 300s
- hostname: your-domain.com
  path: /voice/.*
  service: http://localhost:3335
```

### 4. Verify

```bash
openclaw voicecall-rt status
```

### 5. Make a Call

Tell your agent naturally:

> "Call Tony's Pizza at +14155551234 and make a reservation for 4 people this Friday at 7pm"

Or via CLI:

```bash
openclaw voicecall-rt call -n +14155551234 -t "Reserve a table for 4 on Friday at 7pm"
```

Note: CLI subcommands proxy through the running OpenClaw gateway so webhook/token state stays consistent. If needed, start it with:

```bash
openclaw gateway --force
```

Inspect a past call by Twilio SID (useful for diagnosing machine/voicemail answers):

```bash
openclaw voicecall-rt inspect --sid CAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## CI/CD

This repo includes a GitHub Actions workflow at `.github/workflows/ci-publish.yml` that:

- Runs `bun run typecheck` on pull requests and pushes to `main`
- Verifies version consistency across `package.json`, `openclaw.plugin.json`, and `SKILL.md`
- Publishes to ClawHub on pushes to `main` if that version is not already published

Required GitHub secret:

- `CLAWHUB_TOKEN` — token used for `clawhub login --token ...` during publish

## Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `twilio.accountSid` | string | required | Twilio Account SID |
| `twilio.authToken` | string | required | Twilio Auth Token |
| `fromNumber` | string | required | Twilio phone number (E.164) |
| `openai.apiKey` | string | required | OpenAI API key |
| `openai.model` | string | `gpt-realtime` | OpenAI Realtime model |
| `openai.voice` | string | `coral` | AI voice |
| `vad.type` | string | `semantic_vad` | VAD type |
| `vad.eagerness` | string | `medium` | VAD eagerness |
| `publicUrl` | string | required | Public HTTPS origin for webhooks (no path/query, not localhost/private/internal) |
| `server.port` | number | `3335` | Server port |
| `server.bind` | string | `127.0.0.1` | Bind address |
| `calls.maxDurationSeconds` | number | `600` | Max call duration |
| `calls.timeoutSeconds` | number | `30` | Ring timeout |
| `calls.enableAmd` | boolean | `true` | Answering machine detection |
| `calls.maxConcurrent` | number | `5` | Max concurrent active calls |
| `inbound.enabled` | boolean | `false` | Accept inbound calls |
| `inbound.policy` | string | `disabled` | disabled / open / allowlist |
| `inbound.allowFrom` | string[] | `[]` | Allowed caller numbers (E.164) |
| `inbound.greeting` | string | `"Hey! What's up?"` | What the AI says when answering |
| `inbound.systemPrompt` | string | — | Custom prompt for inbound calls |
| `debug` | boolean | `false` | Debug mode |

## Inbound Calls

Enable receiving calls by setting `inbound.enabled: true` and choosing a policy:

- **`disabled`** — No inbound calls (default)
- **`open`** — Accept calls from any number
- **`allowlist`** — Only accept calls from numbers in `inbound.allowFrom`

## Debug Mode

Enable with `"debug": true` in config. This activates:

- **Call recording** — Raw mu-law + WAV files saved to `~/.openclaw/voice-calls-realtime/recordings/`
- **Verbose logging** — Every WebSocket event with timestamps and color coding
- **Latency metrics** — Speech-end to AI-response-start timing
- **Full transcripts** — JSON transcript files alongside recordings

## How It Works

1. **Call initiation** — Plugin calls Twilio REST API to place an outbound call
2. **Twilio connects** — Twilio hits the `/voice/answer` webhook, gets TwiML with `<Connect><Stream>`
3. **WebSocket bridge** — Twilio opens a WebSocket to the plugin, which opens another to OpenAI Realtime
4. **Audio passthrough** — g711_ulaw audio flows directly between Twilio and OpenAI (zero transcoding)
5. **"Listen first"** — No initial `response.create`; semantic VAD detects the callee's greeting naturally
6. **Conversation** — OpenAI handles the full conversation with function calling for DTMF, hangup, and reporting
7. **Outcome** — Model calls `report_outcome` with structured results, then `end_call`
8. **Callback** — Plugin emits results back to the OpenClaw conversation

## Cost Estimate

Per-call pricing (approximate):

| Component | Cost | Notes |
|-----------|------|-------|
| OpenAI Realtime (audio input) | ~$0.06/min | gpt-realtime |
| OpenAI Realtime (audio output) | ~$0.24/min | gpt-realtime |
| Twilio voice | ~$0.014/min | Outbound US |
| **Total** | **~$0.31/min** | ~$1.55 for a 5-minute call |

## Security

- **Strict webhook authentication** — Signed `X-Twilio-Signature` is required for all Twilio POST webhook routes
- **WebSocket authentication** — Per-call secret tokens prevent unauthorized connections
- **Credentials are never logged or exposed** — API keys and auth tokens are marked sensitive and excluded from all output
- **Twilio Account SIDs are masked** in status output (first 4 + last 4 characters only)
- **Input validation** — All config validated with Zod schemas. Phone numbers must match E.164 format. DTMF restricted to valid digits
- **SSRF guardrails on `publicUrl`** — Only HTTPS public origins are accepted; localhost/private/internal hosts are rejected
- **Server binds to localhost by default** (`127.0.0.1`) — not exposed to the network unless explicitly configured
- **Inbound calls disabled by default** — Requires explicit opt-in with configurable allowlist policy
- **Concurrent call limit** — Prevents runaway costs (default 5 concurrent calls, configurable)
- **Call duration limits** — Default 10-minute max per call
- **Prompt injection hardening** — User/agent prompts are bounded and wrapped with non-overridable call safety rules
- **Identity transparency** — The model is instructed to answer truthfully if asked whether it is an AI
- **Private local artifacts** — Call logs/debug recordings are created with restrictive file permissions

## Requirements

- [Bun](https://bun.sh) runtime
- [OpenClaw](https://github.com/openclaw) installed and configured
- Twilio account with a voice-capable phone number
- OpenAI API key with Realtime API access
- Public URL (Cloudflare Tunnel, ngrok, Tailscale Funnel, etc.)

## License

MIT
