# OpenClaw Voice Configuration

Reference only — consult when helping user set up real-time voice.

## Which Option?

```
Phone calls? → voice-call plugin (Twilio/Telnyx)
Web voice chat? → talk config (ElevenLabs)
Advanced (memory, cost tracking)? → phone-voice skill
```

## Option 1: ElevenLabs Conversational (`talk`)

Basic voice agent via ElevenLabs:

```yaml
talk:
  voiceId: "21m00Tcm4TlvDq8ikWAM"  # Rachel
  modelId: "eleven_turbo_v2"
  apiKey: "..."
  interruptOnSpeech: true  # stop when user talks
```

Works with ElevenLabs Conversational AI widgets.

## Option 2: Phone Calls (`voice-call` plugin)

Real phone calls via Twilio or Telnyx:

```yaml
plugins:
  entries:
    voice-call:
      enabled: true
      config:
        provider: "twilio"  # or telnyx
        fromNumber: "+15551234567"
        twilio:
          accountSid: "AC..."
          authToken: "..."
        tts:
          provider: "elevenlabs"  # or openai
        inboundPolicy: "allowlist"  # or pairing, open
        allowFrom:
          - "+15559876543"
```

Requires public webhook URL (ngrok or Tailscale funnel).

## Option 3: Advanced Integration

Install the `phone-voice` skill for:
- Caller ID authentication
- Voice PIN security
- Memory injection (MEMORY.md loaded into calls)
- Cost tracking per call
- Cloudflare tunnel (permanent URL)

```bash
clawhub install phone-voice
```

## Provider Comparison

| Feature | ElevenLabs | Twilio | Telnyx |
|---------|------------|--------|--------|
| Phone calls | ❌ | ✅ | ✅ |
| Web voice | ✅ | ❌ | ❌ |
| Cost | ~$0.05/min | ~$0.02/min | ~$0.01/min |
| Voice quality | Best | Good | Good |
| Latency | Low | Medium | Medium |

## Costs (Rough)

**Per-minute voice call:**
- Twilio/Telnyx: ~$0.02
- ElevenLabs TTS: ~$0.05
- Anthropic: ~$0.01
- **Total: ~$0.08/min**

Use inbound allowlist to control costs.
