# Prompt Performance Tester

**Model-agnostic prompt benchmarking across 9 providers.**

Pass any model ID — provider auto-detected. Compare latency, cost, quality, and consistency across Claude, GPT, Gemini, DeepSeek, Grok, MiniMax, Qwen, Llama, and Mistral.

---

## 🚀 Why This Skill?

### Problem Statement
Comparing LLM models across providers requires manual testing:
- No systematic way to measure performance across models
- Cost differences are significant but not easily comparable
- Quality varies by use case and provider
- Manual API testing is time-consuming and error-prone

### The Solution
Test prompts across any model from any supported provider simultaneously. Get performance metrics and recommendations based on latency, cost, and quality.

### Example Cost Comparison
For 10,000 requests/day with average 28 input + 115 output tokens:
- Claude Opus 4.6: ~$30.15/day ($903/month)
- Gemini 2.5 Flash-Lite: ~$0.05/day ($1.50/month)
- DeepSeek Chat: ~$0.14/day ($4.20/month)
- Monthly cost difference (Opus vs Flash-Lite): $901.50

---

## ✨ What You Get

### Model-Agnostic Multi-Provider Testing
Pass any model ID — provider is auto-detected from the model name prefix.
No hardcoded list; new models work without code changes.

| Provider | Example Models | Prefix | Required Key |
|----------|---------------|--------|--------------|
| **Anthropic** | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001 | `claude-` | ANTHROPIC_API_KEY |
| **OpenAI** | gpt-5.2-pro, gpt-5.2, gpt-5.1 | `gpt-`, `o1`, `o3` | OPENAI_API_KEY |
| **Google** | gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite | `gemini-` | GOOGLE_API_KEY |
| **Mistral** | mistral-large-latest, mistral-small-latest | `mistral-`, `mixtral-` | MISTRAL_API_KEY |
| **DeepSeek** | deepseek-chat, deepseek-reasoner | `deepseek-` | DEEPSEEK_API_KEY |
| **xAI** | grok-4-1-fast, grok-3-beta | `grok-` | XAI_API_KEY |
| **MiniMax** | MiniMax-M2.1 | `MiniMax`, `minimax` | MINIMAX_API_KEY |
| **Qwen** | qwen3.5-plus, qwen3-max-instruct | `qwen` | DASHSCOPE_API_KEY |
| **Meta Llama** | meta-llama/llama-4-maverick, meta-llama/llama-3.3-70b-instruct | `meta-llama/`, `llama-` | OPENROUTER_API_KEY |

### Known Pricing (per 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| claude-opus-4-6 | $15.00 | $75.00 |
| claude-sonnet-4-6 | $3.00 | $15.00 |
| claude-haiku-4-5-20251001 | $1.00 | $5.00 |
| gpt-5.2-pro | $21.00 | $168.00 |
| gpt-5.2 | $1.75 | $14.00 |
| gpt-5.1 | $2.00 | $8.00 |
| gemini-2.5-pro | $1.25 | $10.00 |
| gemini-2.5-flash | $0.30 | $2.50 |
| gemini-2.5-flash-lite | $0.10 | $0.40 |
| mistral-large-latest | $2.00 | $6.00 |
| mistral-small-latest | $0.10 | $0.30 |
| deepseek-chat | $0.27 | $1.10 |
| deepseek-reasoner | $0.55 | $2.19 |
| grok-4-1-fast | $5.00 | $25.00 |
| grok-3-beta | $3.00 | $15.00 |
| MiniMax-M2.1 | $0.40 | $1.60 |
| qwen3.5-plus | $0.57 | $2.29 |
| qwen3-max-instruct | $1.60 | $6.40 |
| meta-llama/llama-4-maverick | $0.20 | $0.60 |
| meta-llama/llama-3.3-70b-instruct | $0.59 | $0.79 |

> **Note:** Unlisted models still work — cost calculation returns $0.00 with a warning. Pricing table is for reference only, not a validation gate.

### Performance Metrics

Every test measures:
- ⚡ **Latency** — Response time in milliseconds
- 💰 **Cost** — Exact API cost per request (input + output tokens)
- 🎯 **Quality** — Response quality score (0–100)
- 📊 **Token Usage** — Input and output token counts
- 🔄 **Consistency** — Variance across multiple test runs
- ❌ **Error Tracking** — API failures, timeouts, rate limits

### Smart Recommendations

Get instant answers to:
- Which model is **fastest** for your prompt?
- Which is most **cost-effective**?
- Which produces **best quality** responses?
- How much can you **save** by switching providers?

---

## 📊 Real-World Example

```
PROMPT: "Write a professional customer service response about a delayed shipment"

┌─────────────────────────────────────────────────────────────────┐
│ GEMINI 2.5 FLASH-LITE (Google) 💰 MOST AFFORDABLE              │
├─────────────────────────────────────────────────────────────────┤
│ Latency:  523ms                                                 │
│ Cost:     $0.000025                                             │
│ Quality:  65/100                                                │
│ Tokens:   28 in / 87 out                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DEEPSEEK CHAT (DeepSeek) 💡 BUDGET PICK                        │
├─────────────────────────────────────────────────────────────────┤
│ Latency:  710ms                                                 │
│ Cost:     $0.000048                                             │
│ Quality:  70/100                                                │
│ Tokens:   28 in / 92 out                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CLAUDE HAIKU 4.5 (Anthropic) 🚀 BALANCED PERFORMER             │
├─────────────────────────────────────────────────────────────────┤
│ Latency:  891ms                                                 │
│ Cost:     $0.000145                                             │
│ Quality:  78/100                                                │
│ Tokens:   28 in / 102 out                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ GPT-5.2 (OpenAI) 💡 EXCELLENT QUALITY                          │
├─────────────────────────────────────────────────────────────────┤
│ Latency:  645ms                                                 │
│ Cost:     $0.000402                                             │
│ Quality:  88/100                                                │
│ Tokens:   28 in / 98 out                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CLAUDE OPUS 4.6 (Anthropic) 🏆 HIGHEST QUALITY                 │
├─────────────────────────────────────────────────────────────────┤
│ Latency:  1,234ms                                               │
│ Cost:     $0.001875                                             │
│ Quality:  94/100                                                │
│ Tokens:   28 in / 125 out                                       │
└─────────────────────────────────────────────────────────────────┘

🎯 RECOMMENDATIONS:
1. Most cost-effective: Gemini 2.5 Flash-Lite ($0.000025/request) — 99.98% cheaper than Opus
2. Budget pick: DeepSeek Chat ($0.000048/request) — strong quality at low cost
3. Best quality: Claude Opus 4.6 (94/100) — state-of-the-art reasoning & analysis
4. Smart pick: Claude Haiku 4.5 ($0.000145/request) — 81% cheaper, 83% quality match
5. Speed + Quality: GPT-5.2 ($0.000402/request) — excellent quality at mid-range cost

💡 Potential monthly savings (10,000 requests/day, 28 input + 115 output tokens avg):
   - Using Gemini 2.5 Flash-Lite vs Opus: $903/month saved ($1.44 vs $904.50)
   - Using DeepSeek Chat vs Opus: $899/month saved ($4.50 vs $904.50)
   - Using Claude Haiku vs Opus: $731/month saved ($173.40 vs $904.50)
```

---

## Use Cases

### Production Deployment
- Evaluate models before production selection
- Compare cost vs quality tradeoffs
- Benchmark API latency across providers

### Prompt Development
- Test prompt variations across models
- Measure quality scores consistently
- Compare performance metrics

### Cost Analysis
- Analyze LLM API spending by model
- Compare provider pricing structures
- Identify cost-efficient alternatives

### Performance Testing
- Measure latency and response times
- Test consistency across multiple runs
- Evaluate quality scores

---

## 🚀 Quick Start

### 1. Subscribe to Skill
Click "Subscribe" on ClawhHub to get access.

### 2. Set API Keys
Add keys for the providers you want to test:

```bash
# Anthropic (Claude models)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI (GPT models)
export OPENAI_API_KEY="sk-..."

# Google (Gemini models)
export GOOGLE_API_KEY="AI..."

# DeepSeek
export DEEPSEEK_API_KEY="..."

# xAI (Grok models)
export XAI_API_KEY="..."

# MiniMax
export MINIMAX_API_KEY="..."

# Alibaba (Qwen models)
export DASHSCOPE_API_KEY="..."

# OpenRouter (Meta Llama models)
export OPENROUTER_API_KEY="..."

# Mistral
export MISTRAL_API_KEY="..."
```

You only need keys for the providers you plan to test.

### 3. Install Dependencies

```bash
# Install only what you need
pip install anthropic          # Claude
pip install openai             # GPT, DeepSeek, xAI, MiniMax, Qwen, Llama
pip install google-generativeai  # Gemini
pip install mistralai          # Mistral

# Or install everything
pip install anthropic openai google-generativeai mistralai
```

### 4. Run Your First Test

**Option A: Python**
```python
import os
from prompt_performance_tester import PromptPerformanceTester

tester = PromptPerformanceTester()  # reads API keys from environment

results = tester.test_prompt(
    prompt_text="Write a professional email apologizing for a delayed shipment",
    models=[
        "claude-haiku-4-5-20251001",
        "gpt-5.2",
        "gemini-2.5-flash",
        "deepseek-chat",
    ],
    num_runs=3,
    max_tokens=500
)

print(tester.format_results(results))
print(f"🏆 Best quality:  {results.best_model}")
print(f"💰 Cheapest:      {results.cheapest_model}")
print(f"⚡ Fastest:       {results.fastest_model}")
```

**Option B: CLI**
```bash
# Test across multiple models
prompt-tester test "Your prompt here" \
  --models claude-haiku-4-5-20251001 gpt-5.2 gemini-2.5-flash deepseek-chat \
  --runs 3

# Export results
prompt-tester test "Your prompt here" --export results.json
```

---

## 🔒 Security & Privacy

### API Key Safety
- Keys stored in environment variables only — never hardcoded or logged
- Never transmitted to UnisAI servers
- HTTPS encryption for all provider API calls

### Data Privacy
- Your prompts are sent only to the AI providers you select for testing
- Each provider has their own data retention policy (see their privacy pages)
- No data stored on UnisAI infrastructure

---

## 📚 Technical Details

### System Requirements
- **Python**: 3.9+
- **Dependencies**: `anthropic`, `openai`, `google-generativeai`, `mistralai` (install only what you need)
- **Platform**: macOS, Linux, Windows

### Architecture
- **Lazy client initialization** — SDK clients only loaded for providers actually tested
- **Prefix-based routing** — `PROVIDER_MAP` detects provider from model name; no hardcoded whitelist
- **OpenAI-compat path** — DeepSeek, xAI, MiniMax, Qwen, and OpenRouter all use the `openai` SDK with a custom `base_url`
- **Pricing table** — used for cost calculation only; unknown models get `cost=0` with a warning

### Metrics Collected
Every test captures:
- **Latency**: Total response time (ms)
- **Cost**: Input + output cost based on known pricing (USD)
- **Quality**: Heuristic response score based on length, completeness (0–100)
- **Tokens**: Exact input/output token counts per provider
- **Consistency**: Standard deviation across multiple runs
- **Errors**: Timeouts, rate limits, API failures

---

## ❓ Frequently Asked Questions

**Q: Do I need API keys for all 9 providers?**
A: No. You only need keys for the providers you want to test. If you only test Claude models, you only need `ANTHROPIC_API_KEY`.

**Q: Who pays for the API costs?**
A: You do. You provide your own API keys and pay each provider directly. This skill has no per-request fees.

**Q: How accurate are the cost calculations?**
A: Costs are calculated from the known pricing table using actual token counts. Models not in the pricing table return `$0.00` — the model still runs, the cost just won't be shown.

**Q: Can I test models not in the pricing table?**
A: Yes. Any model whose name starts with a supported prefix will run. Cost will show as $0.00 for unlisted models.

**Q: Can I test prompts in non-English languages?**
A: Yes. All supported providers handle multiple languages.

**Q: Can I use this in production/CI/CD?**
A: Yes. Import `PromptPerformanceTester` directly from Python or call via CLI.

**Q: What if my prompt is very long?**
A: Set `max_tokens` appropriately. The skill passes your prompt as-is to each provider's API.

---

## 🗺️ Roadmap

### ✅ Current Release (v1.1.8)
- Model-agnostic architecture — any model ID works via prefix detection
- 9 providers, 20 known models with pricing
- DeepSeek, xAI Grok, MiniMax, Qwen, Meta Llama as first-class providers
- Claude 4.6 series (opus-4-6, sonnet-4-6)
- Lazy client initialization — only loads SDKs for providers actually used
- Fixed UnisAI branding throughout

### 🚧 Coming Soon (v1.3)
- **Batch testing**: Test 100+ prompts simultaneously
- **Historical tracking**: Track model performance over time
- **Webhook integrations**: Slack, Discord, email notifications

### 🔮 Future (v1.3+)
- **A/B testing framework**: Scientific prompt experimentation
- **Fine-tuning insights**: Which models to fine-tune for your use case
- **Custom benchmarks**: Create your own evaluation criteria
- **Auto-optimization**: AI-powered prompt improvement suggestions

---

## 📞 Support

- **Email**: support@unisai.vercel.app
- **Website**: https://unisai.vercel.app
- **Bug Reports**: support@unisai.vercel.app

---

## 📄 License & Terms

This skill is distributed via ClawhHub under the following terms.

### ✅ You CAN:
- Use for your own business and projects
- Test prompts for internal applications
- Modify source code for personal use

### ❌ You CANNOT:
- Redistribute outside ClawhHub registry
- Resell or sublicense
- Use UnisAI trademark without permission

**Full Terms**: See [LICENSE.md](LICENSE.md)

---

## 📝 Changelog

### [1.1.8] - 2026-02-27

#### Fixes & Polish
- Bumped version to 1.1.8
- SKILL.md fully rewritten — cleaned up formatting, removed stale content
- Removed old IP watermark reference (`PROPRIETARY_SKILL_VEDANT_2024`) from docs
- Corrected watermark to `PROPRIETARY_SKILL_UNISAI_2026_MULTI_PROVIDER` throughout
- Fixed all UnisAI branding (was UniAI in v1.1.0 changelog)
- Updated pricing table to include all 20 known models
- Cleaned up FAQ, Quick Start, and Use Cases sections

### [1.1.6] - 2026-02-27

#### 🏗️ Model-Agnostic Architecture
- Provider auto-detected from model name prefix — no hardcoded whitelist
- Any new model works automatically without code changes
- Added DeepSeek, xAI Grok, MiniMax, Qwen, Meta Llama as first-class providers (9 total)
- Updated Claude to 4.6 series (claude-opus-4-6, claude-sonnet-4-6)
- Lazy client initialization — only loads SDKs for providers actually tested
- Unified OpenAI-compat path for DeepSeek, xAI, MiniMax, Qwen, OpenRouter

### [1.1.5] - 2026-02-01

#### 🚀 Latest Models Update
- GPT-5.2 Series — Added Instant, Thinking, and Pro variants
- Gemini 2.5 Series — Updated to 2.5 Pro, Flash, and Flash-Lite
- Claude 4.5 pricing updates
- 10 total models across 3 providers

### [1.1.0] - 2026-01-15

#### ✨ Major Features
- Multi-provider support — Claude, GPT, Gemini
- Cross-provider cost comparison
- Enhanced recommendations engine
- Rebranded to UnisAI

### [1.0.0] - 2024-02-02

#### Initial Release
- Claude-only prompt testing (Haiku, Sonnet, Opus)
- Performance metrics: latency, cost, quality, consistency
- Basic recommendations engine

---

**Last Updated**: February 27, 2026
**Current Version**: 1.1.8
**Status**: Active & Maintained

© 2026 UnisAI. All rights reserved.
