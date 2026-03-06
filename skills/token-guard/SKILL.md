---
name: TokenGuard — LLM API 429 Prevention Engine
description: "<!-- 🌌 Aoineco-Verified | S-DNA: AOI-2026-0213-SDNA-TG01 -->"
---

# TokenGuard — LLM API 429 Prevention Engine

<!-- 🌌 Aoineco-Verified | S-DNA: AOI-2026-0213-SDNA-TG01 -->

**Version:** 1.5.0  
**Author:** Aoineco & Co.  
**License:** MIT  
**Tags:** rate-limit, 429, token-management, cost-optimization, llm-guard, high-performance

## Description

Prevents LLM API 429 (Rate Limit / Resource Exhausted) errors by intercepting requests before they're sent. Designed for users on free/low-cost API plans who need maximum intelligence per dollar.

**Core philosophy:** *"Intelligence is measured not by how much you spend, but by how little you need."*

## Problem

When using LLM APIs (especially Google Gemini Flash with 1M TPM limit):
- Large documents (docx, PDFs) can consume the entire minute quota in one request
- Failed requests still count toward token usage
- Retry loops after 429 errors waste more tokens → death spiral
- No built-in way to detect runaway/duplicate requests

## Features

| Feature | Description |
|---------|-------------|
| **Pre-flight Token Estimation** | Estimates token count before API call (CJK-aware, no tiktoken dependency) |
| **Real-time Quota Tracking** | Tracks per-model per-minute token usage with sliding window |
| **Smart Throttle** | Auto-waits when quota > 80%, blocks at > 95% |
| **Duplicate Detection** | Blocks identical requests within 60s window (3+ = runaway) |
| **Response Caching** | Caches successful responses for duplicate requests |
| **Auto Model Fallback** | Switches to cheaper/available model when primary is exhausted |
| **429 Error Parser** | Extracts exact retry delay from Google/Anthropic error responses |
| **Batch vs Mistake Detection** | Distinguishes intentional bulk processing from error loops |

## Supported Models

Pre-configured quotas for:
- `gemini-3-flash` (1M TPM)
- `gemini-3-pro` (2M TPM)
- `claude-haiku` (50K TPM)
- `claude-sonnet` (200K TPM)
- `claude-opus` (200K TPM)
- `gpt-4o` (800K TPM)
- `deepseek` (1M TPM)

Custom quotas can be added for any model.

## Usage

```python
from token_guard import TokenGuard

guard = TokenGuard()

# Before every API call:
decision = guard.check(prompt_text, model="gemini-3-flash")

if decision.action == "proceed":
    response = call_your_api(prompt_text)
    guard.record_usage(decision.estimated_tokens, model="gemini-3-flash")
    guard.cache_response(prompt_text, response)

elif decision.action == "wait":
    time.sleep(decision.wait_seconds)
    # retry

elif decision.action == "fallback":
    response = call_your_api(prompt_text, model=decision.fallback_model)

elif decision.action == "block":
    print(f"Blocked: {decision.reason}")

# If you get a 429 error:
guard.record_429("gemini-3-flash", retry_delay=53.0)
```

## Integration with OpenClaw

Add to your agent's config or use as a middleware:

```yaml
skills:
  - token-guard
```

The agent can invoke TokenGuard before any LLM API call to prevent quota exhaustion.

## File Structure

```
token-guard/
├── SKILL.md          # This file
└── scripts/
    └── token_guard.py  # Main engine (zero external dependencies)
```

## Status Output Example

```json
{
  "models": {
    "gemini-3-flash": {
      "tpm_limit": 1000000,
      "used_this_minute": 750000,
      "remaining": 250000,
      "usage_pct": "75.0%",
      "status": "🟢 OK"
    }
  },
  "stats": {
    "total_checks": 42,
    "tokens_saved": 128000,
    "blocks": 3,
    "fallbacks": 2
  }
}
```

## Zero Dependencies

Pure Python 3.10+. No pip install needed. No tiktoken, no external API calls.
Designed for the $7 Bootstrap Protocol — every byte counts.
