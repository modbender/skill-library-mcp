# Model Pricing & Routing Reference

## Current Pricing (per 1M tokens, early 2026)

| Model | Input | Output | Best For |
|-------|-------|--------|----------|
| claude-haiku-3-5 | $0.80 | $4.00 | Simple tasks: classify, summarize, format, route |
| claude-sonnet-4-5/4-6 | $3.00 | $15.00 | Default: research, drafting, analysis, tool use |
| claude-opus-4 | $15.00 | $75.00 | Never use unless explicitly requested |

## Model Routing Rules

**Use Haiku for:**
- Single-question lookups
- Text formatting/cleanup
- Yes/no decisions
- Simple summarization
- Status checks with no tool use

**Use Sonnet (default) for:**
- Multi-step research
- Email/content drafting
- Tool-heavy workflows
- Analysis with context
- LinkedIn/prospect research

**Never use Opus** unless Nick explicitly requests it.

## Cost Math (Sonnet at 50:1 ratio)

| Input Tokens | Output Tokens | Cost |
|-------------|---------------|------|
| 50,000 | 1,000 | ~$0.165 |
| 100,000 | 2,000 | ~$0.33 |
| 500,000 | 10,000 | ~$1.65 |
| 1,000,000 | 20,000 | ~$3.30 |

## Context Size Benchmarks

| Context Load | Approx Tokens | Notes |
|-------------|---------------|-------|
| Lean workspace | 1,500–2,500 | Target after trimming |
| Normal session | 5,000–15,000 | Briefing + a few tasks |
| Bloated session | 50,000+ | End of long day, needs compaction |
| Today's peak (pre-fix) | ~120,000+ | 9.8M/day ÷ ~82 calls |

## $5/Day Budget Math

At Sonnet rates, $5/day = ~1.67M input tokens/day.
With aggressive compaction targeting 20:1 ratio, that's ~83,500 output tokens.
Equivalent to ~15–20 substantive tasks per day.
