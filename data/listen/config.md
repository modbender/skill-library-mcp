# OpenClaw STT Configuration

Reference only — consult when helping user set up STT.

## Quick Setup

```yaml
tools:
  media:
    audio:
      provider: "groq"  # groq | openai | local
      groq:
        apiKey: "gsk_..."
        model: "whisper-large-v3-turbo"
```

## Provider Selection

```
Fast + cheap? → groq (free tier available)
Already have OpenAI? → openai
Privacy/offline? → local whisper
```

| Provider | Cost | Speed | Accuracy |
|----------|------|-------|----------|
| groq | Free tier / cheap | Very fast | Good |
| openai | ~$0.006/min | Medium | Very good |
| local | Free | Slow (depends on hardware) | Varies by model |

## Provider Configs

**Groq (recommended):**
```yaml
groq:
  apiKey: "gsk_..."
  model: "whisper-large-v3-turbo"
```

**OpenAI:**
```yaml
openai:
  apiKey: "sk-..."
  model: "whisper-1"
```

**Local (requires whisper installed):**
```yaml
local:
  model: "turbo"  # tiny, base, small, medium, turbo
  language: "auto"
```

## Applying Changes

Use gateway config.patch to update STT settings.
