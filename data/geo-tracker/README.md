# GEO Tracker 🔍

Track your brand's visibility across AI search engines — ChatGPT, Perplexity, Gemini, and Claude.

GEO (Generative Engine Optimization) is the new SEO. This skill tells you whether AI recommends your brand, how often it's mentioned, and what to fix.

## Quick Start

```bash
# Single query
python3 scripts/geo_query.py --brand "YourBrand" --query "best AI website builder" --engines chatgpt,perplexity

# Full audit (batch prompts)
python3 scripts/geo_audit.py --brand "YourBrand" --prompts references/prompts.txt --engines chatgpt,perplexity,gemini --output report.md

# Competitor comparison
python3 scripts/geo_query.py --brand "YourBrand" --competitors "Wix,Squarespace,Framer" --query "best website builder"
```

## What It Does

1. Sends search prompts to AI engines via their APIs
2. Scans responses for brand mentions, positioning, and recommendation signals
3. Scores visibility 0–100 per engine
4. Identifies optimization opportunities
5. Generates actionable reports

## Visibility Score

| Score | Label | Meaning |
|-------|-------|---------|
| 0–20 | Invisible | AI doesn't know your brand |
| 21–40 | Low | Occasional mentions, not recommended |
| 41–60 | Moderate | Mentioned but not top choice |
| 61–80 | Strong | Frequently cited/recommended |
| 81–100 | Dominant | Top recommendation across engines |

## Engines Supported

| Engine | Method | Env Var |
|--------|--------|---------|
| ChatGPT | OpenAI API | `OPENAI_API_KEY` |
| Perplexity | Perplexity API | `PERPLEXITY_API_KEY` |
| Gemini | Google AI API | `GOOGLE_API_KEY` |
| Claude | Anthropic API | `ANTHROPIC_API_KEY` |

Configure at least one. More engines = better coverage.

## Install

```bash
pip install openai anthropic google-generativeai
```

Set your API keys:

```bash
export OPENAI_API_KEY="sk-..."
export PERPLEXITY_API_KEY="..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Project Structure

```
geo-tracker/
├── SKILL.md                    # OpenClaw skill definition
├── scripts/
│   ├── geo_query.py            # Single query check
│   └── geo_audit.py            # Batch audit
└── references/
    ├── prompts.txt             # Prompt library (editable)
    └── geo-optimization.md     # Content optimization playbook
```

## OpenClaw Skill

This is an [OpenClaw](https://github.com/openclaw/openclaw) agent skill. Install it:

```bash
clawhub install geo-tracker
```

Or clone this repo into your OpenClaw skills directory.

## Customization

Edit `references/prompts.txt` to add your own search queries — one per line. These are the prompts sent to AI engines during audits.

See `references/geo-optimization.md` for strategies to improve your brand's AI visibility.

## License

MIT
