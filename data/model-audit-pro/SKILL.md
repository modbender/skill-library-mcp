---
name: model-audit
description: Monthly LLM stack audit — compare your current models against latest benchmarks and pricing from OpenRouter. Identifies potential savings, upgrades, and better alternatives by category (reasoning, code, fast, cheap, vision). Use for optimizing AI costs and staying on the frontier.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+, OpenRouter API key
metadata: {"openclaw": {"emoji": "\ud83d\udd2c", "requires": {"env": ["OPENROUTER_API_KEY"]}, "primaryEnv": "OPENROUTER_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# Model Audit 📊

**Audit your LLM stack against current pricing and alternatives.**

Fetches live pricing from OpenRouter, analyzes your configured models, and recommends potential savings or upgrades by category.

## Quick Start

```bash
# Full audit with recommendations
python3 {baseDir}/scripts/model_audit.py

# JSON output
python3 {baseDir}/scripts/model_audit.py --json

# Audit specific models
python3 {baseDir}/scripts/model_audit.py --models "anthropic/claude-opus-4-6,openai/gpt-4o"

# Show top models by category
python3 {baseDir}/scripts/model_audit.py --top

# Compare two models
python3 {baseDir}/scripts/model_audit.py --compare "anthropic/claude-sonnet-4" "openai/gpt-4o"
```

## What It Does

1. **Fetches** live pricing from OpenRouter API
2. **Reads** your configured models from openclaw.json
3. **Categorizes** models (reasoning, code, fast, cheap, vision)
4. **Compares** against top alternatives in each category
5. **Calculates** potential monthly savings
6. **Recommends** upgrades or cost optimizations

## Output Example

```
═══ LLM Stack Audit ═══

Your Models:
  anthropic/claude-opus-4-6    $5.00/$25.00 per 1M tokens (in/out)
  openai/gpt-4o              $2.50/$10.00 per 1M tokens
  google/gemini-2.0-flash     $0.10/$0.40 per 1M tokens

Recommendations:
  💡 For fast tasks: gemini-2.0-flash is 50x cheaper than opus
  💡 Consider: deepseek/deepseek-r1 for reasoning at $0.55/$2.19
  💡 Your stack covers: reasoning ✓, code ✓, fast ✓, vision ✓
```

## Environment

Requires `OPENROUTER_API_KEY` environment variable.

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
