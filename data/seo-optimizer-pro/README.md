# SEO Optimizer Pro

> AI-powered SEO + AEO content optimization. Free to use.

[![Version](https://img.shields.io/badge/version-1.0.6-blue)](https://github.com/vedantsingh60/seo-optimizer-pro/releases)
[![License](https://img.shields.io/badge/license-free--to--use-green)](LICENSE.md)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-0%2F77-brightgreen)](https://github.com/vedantsingh60/seo-optimizer-pro)
[![ClawhHub](https://img.shields.io/badge/ClawhHub-SEO%20Optimizer%20Pro-orange)](https://clawhub.ai/unisai/seo-optimizer-pro)

Analyze and optimize content for both **Google ranking** and **AI search (AEO)** using your choice of AI model. Supports 12 models across 5 providers.

---

## What It Does

- **Readability Analysis** — Flesch-Kincaid grade level and readability scores
- **Keyword Density** — Track and optimize target keyword coverage
- **Technical SEO** — Heading structure, meta tags, link analysis
- **Content Structure** — Word count, paragraph length, content organization
- **AI Optimization (AEO)** — Recommendations to appear in ChatGPT, Google AI Overviews, Claude

---

## Supported Models

| Provider | Models |
|----------|--------|
| **Anthropic** | `claude-opus-4-5-20251101`, `claude-sonnet-4-5-20250929`, `claude-haiku-4-5-20251001` |
| **OpenAI** | `gpt-5.2-pro`, `gpt-5.2-thinking`, `gpt-5.2-instant` |
| **Google** | `gemini-3-pro`, `gemini-2.5-pro`, `gemini-2.5-flash` |
| **OpenRouter** | `llama-3.3-70b`, `llama-3.2-90b` |
| **Mistral** | `mistral-large-2501` |

---

## Quick Start

### 1. Install the SDK for your chosen provider

```bash
# Claude (recommended)
pip install anthropic>=0.40.0

# GPT or Llama
pip install openai>=1.60.0

# Gemini
pip install google-generativeai>=0.8.0

# Mistral
pip install mistralai>=1.3.0
```

> **Only install the SDK for the provider you plan to use.**

### 2. Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # For Claude
export OPENAI_API_KEY=sk-...          # For GPT
export GOOGLE_API_KEY=AI...           # For Gemini
export OPENROUTER_API_KEY=sk-or-...   # For Llama
export MISTRAL_API_KEY=...            # For Mistral
```

### 3. Run an analysis

```python
from seo_optimizer import SEOOptimizer

optimizer = SEOOptimizer()  # defaults to claude-haiku-4-5-20251001

results = optimizer.analyze_content(
    content="<h1>Cloud Storage</h1><p>Your content here...</p>",
    url="https://example.com/cloud-storage",
    target_keywords=["cloud storage", "data security"]
)

print(optimizer.format_results(results))
```

**Or use a different model:**

```python
optimizer = SEOOptimizer(model="gemini-2.5-flash")
optimizer = SEOOptimizer(model="gpt-5.2-instant")
optimizer = SEOOptimizer(model="mistral-large-2501")
```

---

## Example Output

```
📊 METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Word Count: 847 words
• Readability Score: 68/100 (Good)
• Flesch-Kincaid Grade: 8.2
• Avg Paragraph: 32 words (Optimal)

🔑 KEYWORD DENSITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• cloud storage: 1.8% ✅ (Optimal)
• data security: 0.8% (Increase to 1-2%)

💡 TOP SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 [KEYWORDS] "data security" too low at 0.8%
🟢 [TECHNICAL] Heading structure well organized
🟡 [CONTENT] Expand "encryption" section

🤖 AI SEARCH (AEO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Add FAQ section → gets cited in ChatGPT
2. Include comparison tables → AI cites as authoritative
3. Add "Quick Summary" box → AI pulls for responses
```

---

## Privacy & Security

- **Local execution** — runs on your machine, no UnisAI backend
- **Your content goes to your chosen AI provider only** — not to UnisAI
- **No data stored** — all analysis runs in-memory
- **API keys via env vars only** — never hardcoded or logged

Provider privacy policies:
- [Anthropic](https://www.anthropic.com/legal/privacy) · [OpenAI](https://openai.com/policies/privacy-policy) · [Google](https://ai.google.dev/gemini-api/terms) · [OpenRouter](https://openrouter.ai/privacy) · [Mistral](https://mistral.ai/terms/)

---

## Available on ClawhHub

Install directly via [ClawhHub](https://clawhub.ai/unisai/seo-optimizer-pro) for integration with Claude Code and OpenClaw.

---

## License

Free to use — see [LICENSE.md](LICENSE.md) for details.

© 2026 UnisAI
