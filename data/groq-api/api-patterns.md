# Groq API Patterns

## Base URL and Headers

Base URL:
`https://api.groq.com/openai/v1`

Required headers:
- `Authorization: Bearer $GROQ_API_KEY`
- `Content-Type: application/json`

## Health Check

```bash
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" | jq '.data | length'
```

## Chat Completion (minimal)

```bash
curl -s https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MODEL_ID",
    "messages": [
      {"role":"system","content":"Be concise."},
      {"role":"user","content":"Summarize this in 3 bullets: ..."}
    ],
    "temperature": 0.2
  }' | jq -r '.choices[0].message.content'
```

## Structured JSON Response

Use explicit format instructions and validate parse:

```bash
curl -s https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MODEL_ID",
    "messages": [
      {"role":"system","content":"Return strict JSON with keys: label, confidence."},
      {"role":"user","content":"Classify: payment failed after update"}
    ],
    "temperature": 0
  }' | jq -r '.choices[0].message.content' | jq
```

## Audio Transcription

```bash
curl -s https://api.groq.com/openai/v1/audio/transcriptions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -F "model=MODEL_ID" \
  -F "file=@sample.wav" | jq
```

## Retry Pattern

Retry on `429` and `5xx` with exponential backoff:
1. Sleep 1s
2. Sleep 2s
3. Sleep 4s
4. Stop and report full context if still failing
