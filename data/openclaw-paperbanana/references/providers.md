# Provider Reference — PaperBanana

## Supported Providers

| Component | Provider | Default Model | Cost | Env Var |
|-----------|----------|---------------|------|---------|
| VLM | Google Gemini | gemini-2.0-flash | Free | `GOOGLE_API_KEY` |
| Image Gen | Google Gemini | gemini-2.0-flash-preview-image-generation | Free | `GOOGLE_API_KEY` |
| VLM | OpenAI | gpt-5.2 | Paid | `OPENAI_API_KEY` |
| Image Gen | OpenAI | gpt-image-1.5 | Paid | `OPENAI_API_KEY` |
| VLM | OpenRouter | google/gemini-2.0-flash-001 | Paid | `OPENROUTER_API_KEY` |
| Image Gen | OpenRouter | google/gemini-2.0-flash-001 | Paid | `OPENROUTER_API_KEY` |

## Auto-Detection Priority

The scripts check environment variables in this order:
1. `GOOGLE_API_KEY` → Gemini (free tier, recommended to start)
2. `OPENAI_API_KEY` → OpenAI (best quality, paid)
3. `OPENROUTER_API_KEY` → OpenRouter (flexible, paid)
4. None → error with setup instructions

## Provider Comparison

| Aspect | Gemini (Free) | OpenAI | OpenRouter |
|--------|---------------|--------|------------|
| **Quality** | Good | Best | Varies |
| **Cost** | Free | ~$0.10-0.50/diagram | Pay-per-use |
| **Speed** | ~45s/iteration | ~40s/iteration | Model-dependent |
| **Rate Limits** | 15 RPM (free) | Tier-dependent | Tier-dependent |
| **Best For** | Drafts, iteration | Final figures | Specific models |

## Configuration Examples

### Gemini Only (Free — Recommended to Start)
```json5
// ~/.openclaw/openclaw.json
{
  skills: {
    entries: {
      "paperbanana": {
        env: {
          GOOGLE_API_KEY: "AIzaSy..."
        }
      }
    }
  }
}
```

### OpenAI Only (Best Quality)
```json5
{
  skills: {
    entries: {
      "paperbanana": {
        env: {
          OPENAI_API_KEY: "sk-..."
        }
      }
    }
  }
}
```

### OpenRouter (Access to Any Model)
```json5
{
  skills: {
    entries: {
      "paperbanana": {
        env: {
          OPENROUTER_API_KEY: "sk-or-..."
        }
      }
    }
  }
}
```

### All Providers (Gemini Default, Others Available)
```json5
{
  skills: {
    entries: {
      "paperbanana": {
        env: {
          GOOGLE_API_KEY: "AIzaSy...",
          OPENAI_API_KEY: "sk-...",
          OPENROUTER_API_KEY: "sk-or-..."
        }
      }
    }
  }
}
```

## Model Overrides

Override default models via environment variables in your skill config:

```json5
{
  skills: {
    entries: {
      "paperbanana": {
        env: {
          OPENAI_API_KEY: "sk-...",
          OPENAI_VLM_MODEL: "gpt-5.2",
          OPENAI_IMAGE_MODEL: "gpt-image-1.5",
        }
      }
    }
  }
}
```

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_VLM_MODEL` | gpt-5.2 | OpenAI vision-language model |
| `OPENAI_IMAGE_MODEL` | gpt-image-1.5 | OpenAI image generation model |
| `GEMINI_VLM_MODEL` | gemini-2.0-flash | Gemini VLM |
| `GEMINI_IMAGE_MODEL` | gemini-2.0-flash-preview-image-generation | Gemini image gen |
| `OPENROUTER_VLM_MODEL` | google/gemini-2.0-flash-001 | OpenRouter VLM |
| `OPENROUTER_IMAGE_MODEL` | google/gemini-2.0-flash-001 | OpenRouter image gen |

## Getting API Keys

### Google Gemini (Free)
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Copy the key (starts with `AIzaSy...`)

### OpenAI
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Ensure you have access to `gpt-5.2` and `gpt-image-1.5`

### OpenRouter
1. Go to [OpenRouter](https://openrouter.ai/keys)
2. Create a new API key
3. Add credits to your account

## Aspect Ratios

| Ratio | Best For |
|-------|---------|
| `4:3` | Paper figures (default) |
| `16:9` | Slides, presentations |
| `1:1` | Square figures |
| `3:2` | Wide paper figures |
| `2:3` | Tall/portrait figures |
| `3:4` | Portrait paper figures |
| `9:16` | Vertical posters |
| `21:9` | Ultra-wide banners |
