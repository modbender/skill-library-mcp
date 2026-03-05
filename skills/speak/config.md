# OpenClaw TTS Configuration

Reference only — consult when helping user set up TTS.

## Quick Setup

```yaml
messages:
  tts:
    auto: "inbound"      # off | always | inbound | tagged
    provider: "edge"     # edge | openai | elevenlabs
```

**auto modes:**
- `off` — No TTS
- `always` — Every reply becomes audio
- `inbound` — Reply with audio when user sends audio
- `tagged` — Only when user requests voice

## Provider Selection

```
Free? → edge
Natural voices? → elevenlabs
Already have OpenAI key? → openai
```

| Provider | Cost | Quality | Speed |
|----------|------|---------|-------|
| edge | Free | 6/10 | Fast |
| openai | ~$15/1M chars | 8/10 | Medium |
| elevenlabs | ~$30/1M chars | 9/10 | Medium |

## Provider Configs

**Edge (free, no API key):**
```yaml
edge:
  voice: "en-US-AriaNeural"  # see voices at edge TTS docs
  rate: "+0%"
  pitch: "+0Hz"
```

**OpenAI:**
```yaml
openai:
  apiKey: "sk-..."
  voice: "nova"  # alloy, echo, fable, onyx, nova, shimmer
  model: "tts-1"  # tts-1-hd for quality
```

**ElevenLabs:**
```yaml
elevenlabs:
  apiKey: "..."
  voiceId: "21m00Tcm4TlvDq8ikWAM"  # Rachel
  model: "eleven_multilingual_v2"
```

## Applying Changes

Use gateway config.patch to update TTS settings without full restart.
