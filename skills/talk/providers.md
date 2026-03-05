# Voice Provider Setup

Reference only — consult when user needs provider-specific help.

## Twilio

1. Create account: https://www.twilio.com/
2. Buy a phone number (Voice-capable)
3. Get Account SID + Auth Token from Console
4. Configure webhook URL for incoming calls

```yaml
twilio:
  accountSid: "AC..."
  authToken: "..."
```

**Webhook setup:**
- Voice calls need a public URL
- Use ngrok: `ngrok http 8013`
- Or Tailscale funnel: `tailscale funnel 8013`

## Telnyx

1. Create account: https://telnyx.com/
2. Buy a number + create Voice API connection
3. Get API Key + Connection ID

```yaml
telnyx:
  apiKey: "KEY..."
  connectionId: "..."
```

Lower cost than Twilio, similar quality.

## ElevenLabs (TTS + Conversational)

1. Create account: https://elevenlabs.io/
2. Get API key from Profile
3. For agents: use Conversational AI dashboard

```yaml
elevenlabs:
  apiKey: "..."
  voiceId: "21m00Tcm4TlvDq8ikWAM"  # Rachel
  modelId: "eleven_turbo_v2"
```

**Voices:**
- Rachel (default): warm, natural
- Use Voice Lab for custom/cloned

## OpenAI (TTS)

1. Get API key from OpenAI
2. Simpler setup, decent quality

```yaml
openai:
  apiKey: "sk-..."
  voice: "nova"  # alloy, echo, fable, onyx, shimmer
  model: "tts-1"  # tts-1-hd for quality
```

## Webhook Tunnels

Voice calls need public URLs for webhooks.

**ngrok (temporary):**
```bash
ngrok http 8013
# Use the https URL
```

**Tailscale funnel (permanent, requires Tailscale):**
```bash
tailscale funnel 8013
```

**Cloudflare tunnel (permanent, free):**
```bash
cloudflared tunnel --url http://localhost:8013
```
