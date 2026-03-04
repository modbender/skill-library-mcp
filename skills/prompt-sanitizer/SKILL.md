---
name: prompt-sanitizer
description: "Sanitize prompts before sending to LLMs. Detects PII, prompt injection, toxicity, and off-topic content. Returns cleaned text + risk score. Use when: sanitize input, check prompt safety, detect injection, remove PII, content moderation, guardrails, agent safety."
version: "1.0.0"
author: "Daisuke134"
---

# prompt-sanitizer

Sanitize any text before sending it to an LLM. Detects and flags PII, prompt injection attempts, toxicity, and off-topic hijacking. Returns cleaned text with PII masked and a risk score.

## Prerequisite

```bash
npm install -g awal@2.0.3
awal auth login
```

## Usage

```bash
npx awal@2.0.3 x402 pay https://anicca-proxy-production.up.railway.app/api/x402/prompt-sanitizer \
  -X POST \
  -d '{"text": "My email is john@example.com. Ignore previous instructions.", "checks": ["pii", "injection", "toxicity", "off_topic"], "language": "en"}'
```

## Input

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string (max 10000) | yes | Text to sanitize |
| checks | array of: pii, injection, toxicity, off_topic | no (default: all) | Which checks to run |
| language | "en" or "ja" | no (default: "en") | Language hint |

## Output

```json
{
  "sanitizer_id": "san_a1b2c3",
  "original_length": 89,
  "sanitized_text": "My email is [EMAIL]. ...",
  "flags": [{"type": "pii", "severity": "high", "detail": "Email detected", "position": {"start": 12, "end": 28}}],
  "risk_score": 1.0,
  "safe_to_send": false,
  "safe_t_flag": true
}
```

## Pricing

$0.005 USDC per request (Base network, eip155:8453)

## Endpoint

POST https://anicca-proxy-production.up.railway.app/api/x402/prompt-sanitizer
