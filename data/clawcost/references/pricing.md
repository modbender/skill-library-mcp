# Model Pricing Reference

Updated: February 2026

## Anthropic Claude Models

All prices in USD per 1 million tokens.

### Claude Opus 4.6 / 4.5
| Token Type | Price |
|------------|-------|
| Input | $15.00 |
| Output | $75.00 |
| Cache Read | $1.50 (90% discount) |
| Cache Write | $18.75 (25% premium) |

### Claude Sonnet 4.5
| Token Type | Price |
|------------|-------|
| Input | $3.00 |
| Output | $15.00 |
| Cache Read | $0.30 (90% discount) |
| Cache Write | $3.75 (25% premium) |

### Claude Haiku 4.5
| Token Type | Price |
|------------|-------|
| Input | $0.80 |
| Output | $4.00 |
| Cache Read | $0.08 (90% discount) |
| Cache Write | $1.00 (25% premium) |

## Cost Comparison

For a typical task with 10K input + 2K output tokens:

| Model | Estimated Cost |
|-------|----------------|
| Opus 4.6 | $0.30 |
| Sonnet 4.5 | $0.06 |
| Haiku 4.5 | $0.016 |

**Savings:**
- Sonnet vs Opus: ~80% cheaper
- Haiku vs Opus: ~95% cheaper
- Haiku vs Sonnet: ~73% cheaper

## Tips

1. Use **Haiku** for simple tasks (summarization, formatting)
2. Use **Sonnet** for coding and complex reasoning
3. Reserve **Opus** for tasks requiring maximum capability
4. Leverage **prompt caching** for repeated contexts (90% savings on cached reads)
