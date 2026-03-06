# Providers

This skill uses HTTP calls via `urllib.request` only (no SDKs).

## OpenAI

### Config

```json
{
  "summary": {
    "provider": "openai",
    "model": "gpt-5-mini",
    "api_key_env": "OPENAI_API_KEY"
  }
}
```

### Suggested models
- `gpt-5-mini` (default; low cost)
- `gpt-5.2` (higher quality)

### Cost estimate (rough)
- Typical transcript summary: around **$0.001–$0.01 per video** depending on length.

---

## Gemini

### Config

```json
{
  "tagging": {
    "provider": "gemini",
    "model": "gemini-3-flash",
    "api_key_env": "GEMINI_API_KEY"
  }
}
```

### Suggested models
- `gemini-3-flash` (fast, low cost)
- `gemini-2.5-flash` (widely available)

### Cost estimate (rough)
- Often within free tier for light usage.
- Paid usage is usually low for short tagging prompts.

---

## Anthropic

### Config

```json
{
  "summary": {
    "provider": "anthropic",
    "model": "claude-haiku-4-5",
    "api_key_env": "ANTHROPIC_API_KEY"
  }
}
```

### Suggested models
- `claude-haiku-4-5` (cost-efficient)
- `claude-sonnet-4-6` (higher quality)

### Cost estimate (rough)
- Usually **$0.002–$0.02 per video** depending on transcript length/model.

---

## OpenRouter

### Config

```json
{
  "summary": {
    "provider": "openrouter",
    "model": "openai/gpt-5-mini",
    "api_key_env": "OPENROUTER_API_KEY"
  }
}
```

### Suggested models
- `openai/gpt-5-mini`
- `anthropic/claude-haiku-4-5`
- `google/gemini-3-flash`

### Cost estimate (rough)
- Varies by routed model; check OpenRouter pricing for exact rates.

---

## Ollama (local)

### Config (native API)

```json
{
  "summary": {
    "provider": "ollama",
    "model": "qwen3:8b",
    "api_mode": "native"
  }
}
```

### Config (OpenAI-compatible API)

```json
{
  "summary": {
    "provider": "ollama",
    "model": "llama4-scout:latest",
    "api_mode": "openai",
    "base_url": "http://localhost:11434/v1/chat/completions"
  }
}
```

### Suggested models
- `qwen3:8b`
- `llama4-scout:latest`
- `qwen3:14b`

### Cost estimate (rough)
- API cost: **$0** (local inference)
- Hardware/electricity cost depends on machine and runtime.

---

## Disable AI features

If no API keys are available:

```json
{
  "summary": {"provider": "none"},
  "tagging": {"provider": "none"}
}
```

Behavior:
- Import still works (metadata).
- Enrichment can still add transcript when subtitles are available.
- Tagging falls back to keyword matching.
