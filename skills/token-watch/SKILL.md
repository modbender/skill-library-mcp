---
name: TokenWatch
description: Free and open-source (MIT License) • Zero dependencies • Works
  locally • No API keys required
---

# TokenWatch

**Track, analyze, and optimize token usage and costs across AI providers. Set budgets, get alerts, compare models, and reduce your spend.**

Free and open-source (MIT License) • Zero dependencies • Works locally • No API keys required

---

## Why This Skill?

After OpenAI's acquisition of OpenClaw, token costs are the #1 concern for power users. This skill gives you full visibility into what you're spending, where it's going, and exactly how to reduce it.

### Problems it solves:
- You don't know how much you're spending until the bill arrives
- No way to compare costs across providers before choosing a model
- No alerts when you're approaching your budget
- No actionable suggestions for reducing spend

---

## Features

### 1. Record Usage & Auto-Calculate Costs

```python
from tokenwatch import TokenWatch

monitor = TokenWatch()

monitor.record_usage(
    model="claude-haiku-4-5-20251001",
    input_tokens=1200,
    output_tokens=400,
    task_label="summarize article"
)
# ✅ Recorded: $0.00192
```

### 2. Auto-Record from API Responses

```python
from tokenwatch import record_from_anthropic_response, record_from_openai_response

# Anthropic
response = client.messages.create(model="claude-haiku-4-5-20251001", ...)
record_from_anthropic_response(monitor, response, task_label="my task")

# OpenAI
response = client.chat.completions.create(model="gpt-4o-mini", ...)
record_from_openai_response(monitor, response, task_label="my task")
```

### 3. Set Budgets with Alerts

```python
monitor.set_budget(
    daily_usd=1.00,
    weekly_usd=5.00,
    monthly_usd=15.00,
    per_call_usd=0.10,
    alert_at_percent=80.0   # Alert at 80% of budget
)
# ✅ Budget set: daily=$1.0, weekly=$5.0, monthly=$15.0
# 🚨 BUDGET ALERT fires automatically when threshold is crossed
```

### 4. Dashboard

```python
print(monitor.format_dashboard())
```

```
💰 SPENDING SUMMARY
  Today:   $0.0042  (4 calls, 13,600 tokens)
  Week:    $0.0231  (18 calls, 67,200 tokens)
  Month:   $0.1847  (92 calls, 438,000 tokens)

📋 BUDGET STATUS
  Daily:   [████░░░░░░░░░░░░░░░░] 42% $0.0042 / $1.00 ✅
  Monthly: [███████░░░░░░░░░░░░░] 37% $0.1847 / $0.50 ⚠️

💡 OPTIMIZATION TIPS
  🔴 Swap Opus → Sonnet for non-reasoning tasks (save ~$8.20/mo)
  🟡 High avg cost/call on gpt-4o — reduce prompt length
```

### 5. Compare Models Before Calling

```python
# For 2000 input + 500 output tokens:
for m in monitor.compare_models(2000, 500)[:6]:
    print(f"{m['model']:<42} ${m['cost_usd']:.6f}")
```

```
gemini-2.5-flash                           $0.000300
gpt-4o-mini                                $0.000600
mistral-small-2501                         $0.000350
claude-haiku-4-5-20251001                  $0.003600
mistral-large-2501                         $0.007000
gemini-2.5-pro                             $0.007500
```

### 6. Estimate Before You Call

```python
estimate = monitor.estimate_cost("claude-sonnet-4-5-20250929", input_tokens=5000, output_tokens=1000)
print(f"Estimated cost: ${estimate['estimated_cost_usd']:.6f}")
```

### 7. Optimization Suggestions

```python
suggestions = monitor.get_optimization_suggestions()
for s in suggestions:
    savings = s.get("estimated_monthly_savings_usd", 0)
    print(f"[{s['priority'].upper()}] {s['message']}")
    if savings:
        print(f"  → Save ~${savings:.2f}/month")
```

### 8. Export Reports

```python
monitor.export_report("monthly_report.json", period="month")
```

---

## Supported Models (Feb 2026)

**41 models across 10 providers** — updated Feb 16, 2026.

| Provider | Model | Input/1M | Output/1M |
|----------|-------|----------|-----------|
| Anthropic | claude-opus-4-6 | $5.00 | $25.00 |
| Anthropic | claude-opus-4-5 | $5.00 | $25.00 |
| Anthropic | claude-sonnet-4-5-20250929 | $3.00 | $15.00 |
| Anthropic | claude-haiku-4-5-20251001 | $1.00 | $5.00 |
| OpenAI | gpt-5.2-pro | $21.00 | $168.00 |
| OpenAI | gpt-5.2 | $1.75 | $14.00 |
| OpenAI | gpt-5 | $1.25 | $10.00 |
| OpenAI | gpt-4.1 | $2.00 | $8.00 |
| OpenAI | gpt-4.1-mini | $0.40 | $1.60 |
| OpenAI | gpt-4.1-nano | $0.10 | $0.40 |
| OpenAI | o3 | $10.00 | $40.00 |
| OpenAI | o4-mini | $1.10 | $4.40 |
| Google | gemini-3-pro | $2.00 | $12.00 |
| Google | gemini-3-flash | $0.50 | $3.00 |
| Google | gemini-2.5-pro | $1.25 | $10.00 |
| Google | gemini-2.5-flash | $0.30 | $2.50 |
| Google | gemini-2.5-flash-lite | $0.10 | $0.40 |
| Google | gemini-2.0-flash | $0.10 | $0.40 |
| Mistral | mistral-large-2411 | $2.00 | $6.00 |
| Mistral | mistral-medium-3 | $0.40 | $2.00 |
| Mistral | mistral-small | $0.10 | $0.30 |
| Mistral | mistral-nemo | $0.02 | $0.10 |
| Mistral | devstral-2 | $0.40 | $2.00 |
| xAI | grok-4 | $3.00 | $15.00 |
| xAI | grok-3 | $3.00 | $15.00 |
| xAI | grok-4.1-fast | $0.20 | $0.50 |
| Kimi | kimi-k2.5 | $0.60 | $3.00 |
| Kimi | kimi-k2 | $0.60 | $2.50 |
| Kimi | kimi-k2-turbo | $1.15 | $8.00 |
| Qwen | qwen3.5-plus | $0.11 | $0.44 |
| Qwen | qwen3-max | $0.40 | $1.60 |
| Qwen | qwen3-vl-32b | $0.91 | $3.64 |
| DeepSeek | deepseek-v3.2 | $0.14 | $0.28 |
| DeepSeek | deepseek-r1 | $0.55 | $2.19 |
| DeepSeek | deepseek-v3 | $0.27 | $1.10 |
| Meta | llama-4-maverick | $0.27 | $0.85 |
| Meta | llama-4-scout | $0.18 | $0.59 |
| Meta | llama-3.3-70b | $0.23 | $0.40 |
| MiniMax | minimax-m2.5 | $0.30 | $1.20 |
| MiniMax | minimax-m1 | $0.43 | $1.93 |
| MiniMax | minimax-text-01 | $0.20 | $1.10 |

> To add a custom model: add it to `PROVIDER_PRICING` dict at the top of `tokenwatch.py`.

---

## API Reference

### `TokenWatch(storage_path)`
Initialize monitor. Data stored in `.tokenwatch/` by default.

### `record_usage(model, input_tokens, output_tokens, task_label, session_id)`
Record a single API call. Returns `TokenUsageRecord` with calculated cost.

### `set_budget(daily_usd, weekly_usd, monthly_usd, per_call_usd, alert_at_percent)`
Configure spending limits. Alerts fire automatically when thresholds are crossed.

### `get_spend(period)`
Get aggregated spend. Period: `"today"`, `"week"`, `"month"`, `"all"`, or `"YYYY-MM-DD"`.

### `get_spend_by_model(period)`
Spending breakdown by model, sorted by cost descending.

### `get_spend_by_provider(period)`
Spending breakdown by provider.

### `compare_models(input_tokens, output_tokens)`
Compare costs across all known models. Returns list sorted cheapest first.

### `estimate_cost(model, input_tokens, output_tokens)`
Estimate cost before making a call.

### `get_optimization_suggestions()`
Analyze usage and return ranked suggestions with estimated monthly savings.

### `format_dashboard()`
Human-readable spending dashboard with budget bars and tips.

### `export_report(output_file, period)`
Export full report to JSON.

### `record_from_anthropic_response(monitor, response, task_label)`
Helper to auto-record from Anthropic SDK response object.

### `record_from_openai_response(monitor, response, task_label)`
Helper to auto-record from OpenAI SDK response object.

---

## Privacy & Security

- ✅ **Zero telemetry** — No data sent anywhere
- ✅ **Local-only storage** — Everything in `.tokenwatch/` on your machine
- ✅ **No API keys required** — The monitor itself needs no credentials
- ✅ **No authentication** — No accounts or logins needed
- ✅ **Full transparency** — MIT licensed, source code included

---

## Changelog

### [1.2.3] - 2026-02-16

- 📋 Updated SKILL.md model table to match code: 41 models across 10 providers

### [1.2.0] - 2026-02-16

- ✨ Added DeepSeek, Meta Llama, MiniMax providers
- ✨ Expanded to 41 models across 10 providers
- ✨ Updated all Anthropic/OpenAI/Google/Mistral pricing to Feb 2026 rates

### [1.1.0] - 2026-02-16

- ✨ Added xAI Grok, Kimi (Moonshot), Qwen (Alibaba)
- ✨ Expanded to 32 models across 7 providers

### [1.0.0] - 2026-02-16

- ✨ Initial release — TokenWatch
- ✨ Pricing table for 11 models across 5 providers
- ✨ Budget alerts: daily, weekly, monthly, per-call thresholds
- ✨ Model cost comparison, cost estimation, optimization suggestions
- ✨ Auto-hooks for Anthropic and OpenAI response objects
- ✨ Dashboard, JSON export, local-only storage, MIT licensed

---

**Last Updated**: February 16, 2026
**Current Version**: 1.2.3
**Status**: Active & Community-Maintained

© 2026 UnisAI Community
