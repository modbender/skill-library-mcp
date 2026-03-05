# OpenRouter API Patterns

OpenRouter is a universal AI gateway — one account, one key, access to every major model. The Second Brain uses it for two things: embeddings and metadata extraction.

Base URL: `https://openrouter.ai/api/v1`

Auth header: `Authorization: Bearer $OPENROUTER_API_KEY`

## Embeddings

Generate vector representations of text for semantic search.

**Model:** `openai/text-embedding-3-small`
**Dimensions:** 1536

### Single text

```bash
curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/text-embedding-3-small",
    "input": "Text to embed"
  }'
```

Response:

```json
{
  "data": [
    {
      "embedding": [0.0023, -0.0094, ...],
      "index": 0
    }
  ],
  "usage": {"prompt_tokens": 4, "total_tokens": 4}
}
```

Extract: `data[0].embedding`

### Batch (multiple texts)

```bash
curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/text-embedding-3-small",
    "input": ["First text", "Second text", "Third text"]
  }'
```

Each text gets its own entry in `data[]`, matched by `index`.

### Cost

~$0.02 per million tokens. For typical thoughts (20-50 words each), that's roughly 50,000 thoughts per dollar.

### Limits

- Max input: 8191 tokens per text
- For long content, summarize first, then embed the summary

## Chat Completions (Classification + Routing)

Use an LLM to classify thoughts, assess confidence, and extract structured fields for routing into the appropriate table.

**Model:** `openai/gpt-4o-mini`
**Mode:** JSON mode via `response_format`

```bash
curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o-mini",
    "response_format": { "type": "json_object" },
    "messages": [
      {"role": "system", "content": "YOUR_CLASSIFICATION_PROMPT"},
      {"role": "user", "content": "THE_THOUGHT_TEXT"}
    ]
  }'
```

### Classification prompt

The system prompt should instruct the LLM to return:

```
Extract metadata from the user's captured thought. Return JSON with:
- "type": one of "observation", "task", "idea", "reference", "person_note"
- "topics": array of 1-3 short topic tags (always at least one)
- "people": array of people mentioned (empty if none)
- "action_items": array of implied to-dos (empty if none)
- "dates_mentioned": array of dates YYYY-MM-DD (empty if none)
- "confidence": float 0-1 indicating how confident you are in the classification
- "suggested_route": one of "people", "projects", "ideas", "admin", or null if observation/reference
- "extracted_fields": object with structured data for the destination table (see below)

For person_note: extracted_fields = {"person_name": "...", "context_update": "...", "follow_up": "..." (optional)}
For task: extracted_fields = {"task_name": "...", "due_date": "YYYY-MM-DD" (optional), "notes": "..." (optional)}
For idea: extracted_fields = {"title": "...", "summary": "...", "topics": [...]}
For observation/reference: extracted_fields = null

Only extract what's explicitly there. When unsure of the type, use "observation" with a lower confidence score.
```

### Example response

```json
{
  "choices": [
    {
      "message": {
        "content": "{\"type\": \"person_note\", \"topics\": [\"career\", \"consulting\"], \"people\": [\"Sarah\"], \"action_items\": [\"Follow up about consulting plans\"], \"dates_mentioned\": [], \"confidence\": 0.92, \"suggested_route\": \"people\", \"extracted_fields\": {\"person_name\": \"Sarah\", \"context_update\": \"Thinking about leaving her job to start consulting\", \"follow_up\": \"Ask about consulting plans\"}}"
      }
    }
  ]
}
```

Extract: `JSON.parse(choices[0].message.content)`

### Fallback on parse failure

```json
{"type": "observation", "topics": ["uncategorized"], "confidence": 0.3, "suggested_route": null, "extracted_fields": null}
```

### Cost

~$0.15 per million input tokens, ~$0.60 per million output tokens. For classification of typical thoughts, roughly $0.10-0.30/month at 20 thoughts/day.

## Swapping Models

Because everything goes through OpenRouter, you can swap models by changing the model string:

- **Embeddings:** Change `openai/text-embedding-3-small` to any compatible embedding model. Keep dimensions consistent — if you switch to a model with different dimensions, you need to recreate the table column and re-embed existing thoughts.
- **Metadata extraction:** Change `openai/gpt-4o-mini` to any chat model. `anthropic/claude-3.5-haiku`, `google/gemini-2.0-flash`, etc. Any model that supports JSON mode works.

Browse available models at **openrouter.ai/models**.

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Bad API key | Check `OPENROUTER_API_KEY` |
| 402 Payment Required | No credits | Add credits at openrouter.ai/credits |
| 429 Rate Limited | Too many requests | Back off and retry |
| Model not found | Typo in model string | Check exact model ID at openrouter.ai/models |

---

Built by Limited Edition Jonathan • natebjones.com
