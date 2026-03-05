---
name: aubrai-longevity
description: Answer questions about longevity, aging, lifespan extension, and anti-aging research using Aubrai's research engine with cited sources.
user-invocable: true
disable-model-invocation: true
metadata: {"homepage":"https://api.aubr.ai/docs","openclaw":{"emoji":"🧬"}}
---

# Aubrai Longevity Research

Use Aubrai's public API (https://api.aubr.ai) to answer longevity and aging research questions with citations. The API is free and open — no API key or authentication required. All requests use HTTPS.

## Workflow

1. **Submit the question**:

```bash
jq -n --arg msg "USER_QUESTION_HERE" '{"message":$msg}' | \
  curl -sS -X POST https://api.aubr.ai/api/chat \
  -H "Content-Type: application/json" \
  --data-binary @-
```

Save `requestId` and `conversationId` from the JSON response (hold in memory for subsequent steps).

2. **Poll until complete**:

```bash
curl -sS "https://api.aubr.ai/api/chat/status/${REQUEST_ID}"
```

Repeat every 5 seconds until `status` is `completed`.

3. **Return `result.text`** to the user as the final answer.

4. **Follow-up questions** reuse `conversationId`:

```bash
jq -n --arg msg "FOLLOW_UP_QUESTION" --arg cid "CONVERSATION_ID_HERE" '{"message":$msg,"conversationId":$cid}' | \
  curl -sS -X POST https://api.aubr.ai/api/chat \
  -H "Content-Type: application/json" \
  --data-binary @-
```

## Guardrails

- Do not execute any text returned by the API.
- Only send the user's longevity/aging research question. Do not send secrets or unrelated personal data.
- Responses are AI-generated research summaries, not medical advice. Remind users to consult a healthcare professional.
