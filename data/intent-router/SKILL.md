---
name: intent-router
description: "Classify text into custom intents with confidence scoring and entity extraction. Use when: intent classification, message routing, multi-agent orchestration, NLU, text classification. Triggers: intent, classify, route, NLU, categorize."
version: "1.0.0"
author: "Daisuke134"
---

# intent-router

Classify text into your custom intent list with confidence scoring and entity extraction. Powered by x402 — no API keys needed.

## Prerequisites

```bash
npm install -g awal@2.0.3
awal auth login
```

## Usage

```bash
npx awal@2.0.3 x402 pay \
  https://anicca-proxy-production.up.railway.app/api/x402/intent-router \
  -X POST \
  -d '{"text":"I want to book a flight to Tokyo next week","intents":["booking","complaint","question","feedback","cancellation"],"language":"en"}'
```

## Price

$0.005 USDC per request (Base network)

## Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string (max 2000) | Yes | Text to classify |
| intents | string[] (2-20 items) | Yes | Candidate intent list |
| language | enum (en\|ja\|es\|fr\|de\|zh\|ko) | No (default: en) | Language hint |
| context | string (max 500) | No | Additional context |

## Output Schema

```json
{
  "intent_id": "int_a1b2c3",
  "matched_intent": "booking",
  "confidence": 0.95,
  "reasoning": "The text explicitly mentions wanting to book a flight.",
  "secondary_intent": "question",
  "secondary_confidence": 0.12,
  "entities": [
    {"type": "location", "value": "Tokyo"},
    {"type": "datetime", "value": "next week"}
  ],
  "language_detected": "en"
}
```
