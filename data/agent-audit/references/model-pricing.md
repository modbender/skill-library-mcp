# Model Pricing Reference

Updated: February 2026. Prices per 1M tokens.

## Anthropic (Claude)

| Model | Input | Output | Tier |
|-------|-------|--------|------|
| claude-opus-4 | $15.00 | $75.00 | Complex |
| claude-sonnet-4 | $3.00 | $15.00 | Medium |
| claude-haiku-3.5 | $0.80 | $4.00 | Simple |
| claude-haiku-3 | $0.25 | $1.25 | Simple |

## OpenAI

| Model | Input | Output | Tier |
|-------|-------|--------|------|
| gpt-4.5 | $75.00 | $150.00 | Complex |
| gpt-4o | $2.50 | $10.00 | Medium |
| gpt-4o-mini | $0.15 | $0.60 | Simple |
| o1 | $15.00 | $60.00 | Complex |
| o3-mini | $1.10 | $4.40 | Medium |

## Google (Gemini)

| Model | Input | Output | Tier |
|-------|-------|--------|------|
| gemini-2.5-pro | $1.25 | $10.00 | Complex |
| gemini-2.0-flash | $0.10 | $0.40 | Simple |
| gemini-2.0-flash-lite | $0.025 | $0.10 | Simple |

## xAI (Grok)

| Model | Input | Output | Tier |
|-------|-------|--------|------|
| grok-3 | $3.00 | $15.00 | Complex |
| grok-3-mini | $0.30 | $0.50 | Simple |
| grok-4-1-fast | $5.00 | $25.00 | Medium |

## How to Calculate Monthly Cost

```
monthly_cost = (input_tokens / 1M × input_price) + (output_tokens / 1M × output_price)
```

For cron jobs, multiply by runs per month:
```
cron_monthly_cost = cost_per_run × runs_per_day × 30
```

## Tier Recommendations by Provider

| Task Type | Anthropic | OpenAI | Google | xAI |
|-----------|-----------|--------|--------|-----|
| Simple | haiku-3 | gpt-4o-mini | flash-lite | grok-3-mini |
| Medium | sonnet-4 | gpt-4o | flash | grok-4-1-fast |
| Complex | opus-4 | gpt-4.5/o1 | 2.5-pro | grok-3 |
