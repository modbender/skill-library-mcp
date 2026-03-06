# TokenWatch

> Track, optimize, and control your AI API spending. Free and open-source (MIT).

[![Version](https://img.shields.io/badge/version-1.2.3-blue)](https://github.com/vedantsingh60/tokenwatch/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE.md)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-0%2F77-brightgreen)](https://github.com/vedantsingh60/tokenwatch)
[![ClawhHub](https://img.shields.io/badge/ClawhHub-Token%20Budget%20Monitor-orange)](https://clawhub.ai/unisai/tokenwatch)

Know exactly what you're spending on AI APIs. Set budgets, get alerts before you overspend, compare model costs, and get actionable optimization suggestions — all running locally with zero dependencies.

---

## What It Does

- **Cost Tracking** — Record every API call with automatic cost calculation
- **Budget Alerts** — Set daily/weekly/monthly limits with threshold warnings
- **Model Comparison** — Compare costs across 41 models before making a call
- **Optimization Suggestions** — Get ranked tips to reduce spend with estimated savings
- **Dashboard** — Visual spending overview with budget status bars
- **Provider Hooks** — Auto-record from Anthropic and OpenAI response objects

---

## Supported Models & Pricing (Feb 2026)

**41 models across 10 providers** — the most comprehensive AI pricing table available.

| Provider | Model | Input ($/1M) | Output ($/1M) |
|----------|-------|-------------|--------------|
| **Anthropic** | `claude-opus-4-6` | $5.00 | $25.00 |
| **Anthropic** | `claude-opus-4-5` | $5.00 | $25.00 |
| **Anthropic** | `claude-sonnet-4-5-20250929` | $3.00 | $15.00 |
| **Anthropic** | `claude-haiku-4-5-20251001` | $1.00 | $5.00 |
| **OpenAI** | `gpt-5.2-pro` | $21.00 | $168.00 |
| **OpenAI** | `gpt-5.2` | $1.75 | $14.00 |
| **OpenAI** | `gpt-5` | $1.25 | $10.00 |
| **OpenAI** | `gpt-4.1` | $2.00 | $8.00 |
| **OpenAI** | `gpt-4.1-mini` | $0.40 | $1.60 |
| **OpenAI** | `gpt-4.1-nano` | $0.10 | $0.40 |
| **OpenAI** | `o3` | $10.00 | $40.00 |
| **OpenAI** | `o4-mini` | $1.10 | $4.40 |
| **Google** | `gemini-3-pro` | $2.00 | $12.00 |
| **Google** | `gemini-3-flash` | $0.50 | $3.00 |
| **Google** | `gemini-2.5-pro` | $1.25 | $10.00 |
| **Google** | `gemini-2.5-flash` | $0.30 | $2.50 |
| **Google** | `gemini-2.5-flash-lite` | $0.10 | $0.40 |
| **Google** | `gemini-2.0-flash` | $0.10 | $0.40 |
| **Mistral** | `mistral-large-2411` | $2.00 | $6.00 |
| **Mistral** | `mistral-medium-3` | $0.40 | $2.00 |
| **Mistral** | `mistral-small` | $0.10 | $0.30 |
| **Mistral** | `mistral-nemo` | $0.02 | $0.10 |
| **Mistral** | `devstral-2` | $0.40 | $2.00 |
| **xAI** | `grok-4` | $3.00 | $15.00 |
| **xAI** | `grok-3` | $3.00 | $15.00 |
| **xAI** | `grok-4.1-fast` | $0.20 | $0.50 |
| **Kimi** | `kimi-k2.5` | $0.60 | $3.00 |
| **Kimi** | `kimi-k2` | $0.60 | $2.50 |
| **Kimi** | `kimi-k2-turbo` | $1.15 | $8.00 |
| **Qwen** | `qwen3.5-plus` | $0.11 | $0.44 |
| **Qwen** | `qwen3-max` | $0.40 | $1.60 |
| **Qwen** | `qwen3-vl-32b` | $0.91 | $3.64 |
| **DeepSeek** | `deepseek-v3.2` | $0.14 | $0.28 |
| **DeepSeek** | `deepseek-r1` | $0.55 | $2.19 |
| **DeepSeek** | `deepseek-v3` | $0.27 | $1.10 |
| **Meta** | `llama-4-maverick` | $0.27 | $0.85 |
| **Meta** | `llama-4-scout` | $0.18 | $0.59 |
| **Meta** | `llama-3.3-70b` | $0.23 | $0.40 |
| **MiniMax** | `minimax-m2.5` | $0.30 | $1.20 |
| **MiniMax** | `minimax-m1` | $0.43 | $1.93 |
| **MiniMax** | `minimax-text-01` | $0.20 | $1.10 |

> Add any custom model to `PROVIDER_PRICING` in `tokenwatch.py` with `{"input": ..., "output": ..., "provider": "..."}` to track it.

---

## Quick Start

No installation needed — pure Python, zero dependencies.

```python
from tokenwatch import TokenWatch

monitor = TokenWatch()

# Set a monthly budget
monitor.set_budget(daily_usd=1.00, weekly_usd=5.00, monthly_usd=15.00)

# Record usage after each API call
monitor.record_usage(
    model="claude-haiku-4-5-20251001",
    input_tokens=1200,
    output_tokens=400,
    task_label="summarize article"
)

# View spending dashboard
print(monitor.format_dashboard())
```

**Auto-record from API responses:**

```python
from tokenwatch import TokenWatch, record_from_anthropic_response
import anthropic

client = anthropic.Anthropic()
monitor = TokenWatch()

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)

# Auto-extracts model, input_tokens, output_tokens from response
record_from_anthropic_response(monitor, response, task_label="greeting")
```

**Compare models before choosing:**

```python
# See cost for 2000 input + 500 output tokens across all models
for m in monitor.compare_models(2000, 500)[:5]:
    print(f"{m['model']:<40} ${m['cost_usd']:.6f}")
```

---

## Example Output

```
╔═══════════════════════════════════════════════════════════════╗
║              TOKEN BUDGET MONITOR — DASHBOARD                 ║
╚═══════════════════════════════════════════════════════════════╝

💰 SPENDING SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Today:   $0.0042  (4 calls, 13,600 tokens)
  Week:    $0.0231  (18 calls, 67,200 tokens)
  Month:   $0.1847  (92 calls, 438,000 tokens)

📋 BUDGET STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Daily:   [████░░░░░░░░░░░░░░░░] 42% $0.0042 / $1.00 ✅
  Monthly: [███████░░░░░░░░░░░░░] 37% $0.1847 / $0.50 ✅

💡 OPTIMIZATION TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔴 Swap Opus → Sonnet for non-reasoning tasks (save ~$8.20/mo)
  🟡 High avg cost/call on gpt-4o — consider reducing prompt length
  🟢 ✅ Spending looks efficient overall
```

---

## Privacy & Security

- **Local-only** — all data stored in `.tokenwatch/` on your machine
- **No external calls** — works completely offline
- **No API keys required** — the monitor itself needs no credentials
- **Full transparency** — MIT licensed, source code included

---

## Available on ClawhHub

Install directly via [ClawhHub](https://clawhub.ai/unisai/tokenwatch) for integration with Claude Code and OpenClaw.

---

## License

MIT License — see [LICENSE.md](LICENSE.md) for details.

© 2026 UnisAI Community
