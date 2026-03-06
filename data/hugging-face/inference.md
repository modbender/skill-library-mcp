# Inference Playbook - Hugging Face

## Authentication

Set token once per shell session:

```bash
export HF_TOKEN="<token>"
```

Never print full tokens in logs or transcripts.

## Generic Inference Request

```bash
MODEL_ID="google/flan-t5-large"

curl -s "https://api-inference.huggingface.co/models/${MODEL_ID}" \
  -H "Authorization: Bearer ${HF_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": "Summarize this article in five bullets.",
    "parameters": {
      "max_new_tokens": 220,
      "temperature": 0.2
    }
  }' | jq
```

## Parameter Defaults

Use conservative defaults for predictable outputs:
- `temperature`: `0.1` to `0.3`
- `max_new_tokens`: task-specific but bounded
- Deterministic prompt framing for benchmarks

## Response Handling

Always normalize outputs before comparison:
- Strip boilerplate prefixes
- Extract core answer payload
- Preserve raw response in `evaluations.md` summary

## Fallback Ladder

If request fails:
1. Retry once with shorter input
2. Retry with lower `max_new_tokens`
3. Switch to backup model with same task family
4. Return a local-only alternative when external inference remains unavailable

## Guardrails

- Do not send unrelated user context.
- Do not upload local files unless explicitly requested.
- Do not assume all models support the same payload schema.
