# Token Estimation & Cloud Cost Reference

## Quick Estimation

Rule of thumb: **~4 characters = 1 token** (English prose).

| Content                     | Approx. Tokens |
| --------------------------- | -------------- |
| Short question (< 20 words) | 20–40          |
| Paragraph (100 words)       | 130            |
| One page (500 words)        | 650            |
| Meeting transcript (1h)     | 5,000–15,000   |
| Small code file (100 lines) | 300–800        |
| Large code file (500 lines) | 1,500–4,000    |

## Context Window Limits (Common Local Models)

| Model           | Context Window |
| --------------- | -------------- |
| llama3.2:3b     | 128K tokens    |
| mistral:7b      | 32K tokens     |
| deepseek-r1:7b  | 128K tokens    |
| deepseek-r1:14b | 128K tokens    |
| phi-2           | 2K tokens      |
| llama3.1:8b     | 128K tokens    |

## Cloud Cost Reference (per 1K tokens, blended input+output avg)

| Model             | Blended $/1K |
| ----------------- | ------------ |
| gpt-4o            | $0.0050      |
| gpt-4o-mini       | $0.000225    |
| claude-3-5-sonnet | $0.0090      |
| claude-3-5-haiku  | $0.0010      |
| claude-3-opus     | $0.0450      |
| gemini-1.5-pro    | $0.00175     |
| gemini-1.5-flash  | $0.000125    |

> Prices as of early 2026; verify at provider pricing pages.
> `track_savings.py` uses these blended rates. Pass `--model MODEL` to log with the correct rate.

## Cost Savings Example

Routing 100 requests of ~1,000 tokens each to local instead of gpt-4o:

```
100 requests × 1,000 tokens × $0.005/1K = $0.50 saved
```

Over a month of 2,000 daily requests that could go local:

```
2,000 × 1,000 tokens × $0.005/1K × 30 days = $300/month saved
```
