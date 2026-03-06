---
name: q-kdb-code-review
description: AI-powered code review for Q/kdb+ — catch bugs in the most terse language in finance
version: 1.0.0
homepage: https://github.com/beee003/astrai-openclaw
metadata:
  clawdbot:
    emoji: "⚡"
    requires:
      env: ["ASTRAI_API_KEY"]
    primaryEnv: "ASTRAI_API_KEY"
    files: ["plugin.py", "config.example.toml"]
tags: [q, kdb, kdb-plus, quant, finance, code-review, hft, trading, timeseries]
---

# q-kdb-code-review

AI-powered code review for Q/kdb+ — catch bugs, performance issues, and security vulnerabilities in the most terse language in quantitative finance.

## What it does

Reviews Q/kdb+ code with deep understanding of Q idioms, performance patterns, and common pitfalls. Built for quant developers, kdb+ DBAs, and trading infrastructure teams.

**Catches:**

- Type errors in implicit casts (e.g., mixing longs and floats in comparisons)
- Rank errors from wrong argument counts in function calls
- Unescaped signals in protected evaluation
- Memory-inefficient queries (selecting all columns when only some are needed)
- Missing `peach` parallelism opportunities for embarrassingly parallel operations
- Unsafe `eval`/`value` usage on user-supplied strings (Q injection)
- Unlocked tables during concurrent inserts
- Missing `` `g# `` grouped attributes on high-cardinality join columns
- N-squared joins that should be `aj` (asof joins) or `wj` (window joins)
- Race conditions in timer callbacks (.z.ts)
- Unprotected IPC handlers (.z.pg, .z.ps) and exposed .z.pw

**Strictness modes:**

| Mode | What it checks |
|------|---------------|
| `standard` | Bugs, correctness, type errors, join semantics, null handling |
| `strict` | Everything in standard + performance (attributes, peach, vector ops) + style |
| `security` | Everything in standard + injection via string eval, unprotected IPC handlers, exposed .z.pw, port exposure |

**Intelligent routing via Astrai:** Complex algorithmic Q (custom signal generation, real-time CEP) routes to powerful models. Simple table operations (selects, inserts, schema definitions) route to cheaper, faster models. You get the best result at the lowest cost.

**BYOK (Bring Your Own Keys):** Your provider API keys, your billing. Astrai routes to the best model among your configured providers.

## Setup

1. **Get a free API key** at [as-trai.com](https://as-trai.com)
2. **Set your API key:**
   ```bash
   export ASTRAI_API_KEY="your_key_here"
   ```
3. **Optionally add provider keys** for BYOK routing:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export OPENAI_API_KEY="sk-..."
   ```
4. **Run `/review-q`** on any `.q` file

## Usage

```
/review-q                          Review current Q file
/review-q --strict                 Strict mode: bugs + performance + style
/review-q --focus security         Security mode: eval injection, IPC, .z.pw
/review-q --file tick.q            Review a specific file
```

### Example output

```
Reviewing tick.q (strict mode)...
Model: claude-opus-4-6 via Astrai

Found 3 issues:

[CRITICAL] Line 12: Missing `s# attribute on time column
  `trade` table uses `aj` but `time` column lacks sorted attribute.
  Without `s#`, asof join scans linearly — O(n) instead of O(log n).
  Fix: trade: `trade upsert update `s#time from trade

[WARNING] Line 34: Using `each` where vector operation suffices
  {x*y} each' (price;qty) can be replaced with price*qty
  Vector multiply is ~100x faster than each-both.

[INFO] Line 45: Consider `peach` for independent symbol processing
  Processing each symbol sequentially. Since operations are independent,
  `peach` would utilize all cores.
  Fix: results: func peach syms

Summary: 1 critical, 1 warning, 1 info. Focus on the missing sorted
attribute — it will cause aj performance to degrade from microseconds
to milliseconds at scale.
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ASTRAI_API_KEY` | Yes | API key from [as-trai.com](https://as-trai.com) |
| `ANTHROPIC_API_KEY` | No | BYOK: Anthropic provider key |
| `OPENAI_API_KEY` | No | BYOK: OpenAI provider key |
| `GOOGLE_API_KEY` | No | BYOK: Google AI provider key |
| `DEEPSEEK_API_KEY` | No | BYOK: DeepSeek provider key |
| `MISTRAL_API_KEY` | No | BYOK: Mistral provider key |
| `GROQ_API_KEY` | No | BYOK: Groq provider key |
| `TOGETHER_API_KEY` | No | BYOK: Together AI provider key |
| `FIREWORKS_API_KEY` | No | BYOK: Fireworks AI provider key |
| `COHERE_API_KEY` | No | BYOK: Cohere provider key |
| `PERPLEXITY_API_KEY` | No | BYOK: Perplexity provider key |
| `REVIEW_STRICTNESS` | No | Default strictness: `standard`, `strict`, or `security` |

## External Endpoints

| Endpoint | Purpose |
|----------|---------|
| `as-trai.com/v1/chat/completions` | Astrai inference router — routes Q review requests to the optimal model |

## Security & Privacy

- **No code storage:** Your Q code is sent to the selected AI provider for inference and is not stored by Astrai.
- **BYOK:** When you provide your own provider keys, requests go directly through Astrai's router to your provider account. Astrai does not store or log your provider keys beyond the request lifecycle.
- **Transport:** All communication uses HTTPS/TLS.
- **No telemetry:** The skill does not send analytics or telemetry data. Only the review request goes to Astrai.
- **Local processing:** File reading and result formatting happen entirely on your machine.

## Why Q needs specialized review

Q is unlike any mainstream programming language:

- **Extreme terseness:** A single line of Q can express what takes 20 lines in Python. This density makes bugs nearly invisible during manual review.
- **Implicit type coercion:** Q silently coerces types in many operations. Comparing a long to a float, or joining on mismatched key types, can produce silently wrong results.
- **1000x performance gaps:** The difference between idiomatic and naive Q is not 2x or 10x — it is often 1000x. Missing a sorted attribute on a time column turns an O(log n) asof join into O(n). Using `each` instead of vector operations adds interpreter overhead per element.
- **Adverb complexity:** Q's adverbs (`/`, `\`, `'`, `/:`, `\:`, `':`) modify function behavior in powerful but subtle ways. `+/` is reduce-add, `+\` is scan-add, `+'` is each-both-add. Confusing these causes wrong results, not errors.
- **Most AI models struggle:** Without Q-specific prompting, general-purpose AI models treat Q code as line noise. This skill provides detailed system prompts that teach the model Q semantics, kdb+ internals, and finance-domain patterns.

## Pricing

Uses Astrai's inference routing. Your costs depend on the models selected:

| Plan | Rate | Includes |
|------|------|----------|
| Free | $0 | 1,000 requests/day |
| Pro | $49/mo | 50,000 requests/day, priority routing |
| Business | $199/mo | Unlimited requests, dedicated support |

With BYOK, you pay your provider directly at their rates. Astrai's routing is included in the plan price.
