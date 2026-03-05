---
name: model-council
description: Multi-model consensus system — send a query to 3+ different LLMs via OpenRouter simultaneously, then a judge model evaluates all responses and produces a winner, reasoning, and synthesized best answer. Like having a board of AI advisors. Use for important decisions, code review, research verification.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+, OpenRouter API key
metadata: {"openclaw": {"emoji": "\ud83c\udfdb\ufe0f", "requires": {"env": ["OPENROUTER_API_KEY"]}, "primaryEnv": "OPENROUTER_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# Model Council 🏛️

**Get consensus from multiple AI models on any question.**

Send your query to 3+ different LLMs simultaneously via OpenRouter. A judge model evaluates all responses and produces a winner, reasoning, and synthesized best answer.

## When to Use

- **Important decisions** — Don't trust one model's opinion
- **Code review** — Get multiple perspectives on architecture choices
- **Research verification** — Cross-check facts across models
- **Creative work** — Compare writing styles and pick the best
- **Debugging** — When one model is stuck, others might see the issue

## How It Works

```
Your Question
    ├──→ Claude Sonnet 4    ──→ Response A
    ├──→ GPT-4o             ──→ Response B
    └──→ Gemini 2.0 Flash   ──→ Response C
                                    │
                              Judge (Opus) evaluates all
                                    │
                              ├── Winner + Reasoning
                              ├── Synthesized Best Answer
                              └── Cost Breakdown
```

## Quick Start

```bash
# Basic usage
python3 {baseDir}/scripts/model_council.py "What's the best database for a real-time analytics dashboard?"

# Custom models
python3 {baseDir}/scripts/model_council.py --models "anthropic/claude-sonnet-4,openai/gpt-4o,google/gemini-2.5-pro" "Your question"

# Custom judge
python3 {baseDir}/scripts/model_council.py --judge "openai/gpt-4o" "Your question"

# JSON output
python3 {baseDir}/scripts/model_council.py --json "Your question"

# Set max tokens per response
python3 {baseDir}/scripts/model_council.py --max-tokens 2000 "Your question"
```

## Configuration

| Flag | Default | Description |
|------|---------|-------------|
| `--models` | claude-sonnet-4, gpt-4o, gemini-2.0-flash | Comma-separated model list |
| `--judge` | anthropic/claude-opus-4-6 | Judge model |
| `--max-tokens` | 1024 | Max tokens per council member |
| `--json` | false | Output as JSON |
| `--timeout` | 60 | Timeout per model (seconds) |

## Environment

Requires `OPENROUTER_API_KEY` environment variable.

## Output Example

```
═══ MODEL COUNCIL RESULTS ═══

Question: What's the best way to handle auth in a microservices architecture?

── Council Member Responses ──

🤖 anthropic/claude-sonnet-4 ($0.0043)
Use a centralized auth service with JWT tokens...

🤖 openai/gpt-4o ($0.0038)
Implement OAuth 2.0 with an API gateway...

🤖 google/gemini-2.0-flash-001 ($0.0012)
Consider using service mesh with mTLS...

── Judge Verdict (anthropic/claude-opus-4-6, $0.0125) ──

🏆 Winner: anthropic/claude-sonnet-4
Reasoning: Most comprehensive and practical approach...

📝 Synthesized Answer:
The best approach combines elements from all three...

💰 Total Cost: $0.0218
```

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
