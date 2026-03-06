---
name: emotionwise
description: Analyze text for emotions and sarcasm using the EmotionWise API (28 labels, EN/ES).
metadata: {"openclaw":{"emoji":"🧠","homepage":"https://emotionwise.ai","requires":{"env":["EMOTIONWISE_API_KEY"]},"primaryEnv":"EMOTIONWISE_API_KEY"}}
user-invocable: true
---

# EmotionWise Skill

Use this skill when the user asks to:
- detect emotions in text
- detect sarcasm in text
- summarize emotional trends across multiple messages

## API

Endpoint:
`POST https://api.emotionwise.ai/api/v1/tools/emotion-detector`

Headers:
- `X-API-Key: $EMOTIONWISE_API_KEY`
- `Content-Type: application/json`

Body:
```json
{ "message": "<text>" }
```

## Response (expected fields)

```json
{
  "detected_emotions": ["joy", "admiration"],
  "confidence_scores": { "joy": 0.87, "admiration": 0.72 },
  "sarcasm_detected": false,
  "sarcasm_score": 0.04
}
```

## Output format

Return:
- top emotions with confidence
- sarcasm flag + score
- short practical interpretation for developer use

## Error handling

- `401/403`: Tell the user API key is missing/invalid and suggest reconfiguration.
- `429`: Tell the user quota/rate limit was hit and suggest retry later.
- `5xx`: Tell the user the API is temporarily unavailable and suggest retry.
