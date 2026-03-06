---
name: volcengine-ai-text-ark-chat
description: Text generation and chat completion on Volcengine ARK. Use when users need long-form writing, summarization, extraction, rewriting, Q&A, or prompt optimization with ARK text models.
---

# volcengine-ai-text-ark-chat

Execute text/chat tasks on Volcengine ARK with stable parameter defaults and reproducible request templates.

## Execution Checklist

1. Verify `ARK_API_KEY`, endpoint ID, and region.
2. Clarify task type (chat, summarize, rewrite, extract).
3. Set safe defaults (`temperature`, `max_tokens`, `top_p`).
4. Return output plus key parameters used.

## Minimal Request Template

```bash
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ep-xxxx",
    "messages": [{"role":"user","content":"请总结这段文本"}],
    "temperature": 0.2
  }'
```

## References

- `references/sources.md`
