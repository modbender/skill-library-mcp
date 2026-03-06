# 🦞🚀 Venice.ai Router for OpenClaw

A cost-optimized model routing skill for [OpenClaw](https://github.com/PlusOne/openclaw) that automatically selects the cheapest [Venice.ai](https://venice.ai) model capable of handling your query.

Instead of always hitting expensive models, the router classifies each prompt's complexity and routes it to an appropriate tier — saving up to **99%** on simple queries compared to always using premium models.

## Why Venice.ai?

Venice AI is the AI platform for people who don't want Big Tech watching over their shoulder. Unlike OpenAI, Anthropic, and Google — where every prompt is logged, analyzed, and potentially used to train future models — Venice offers **true privacy** with zero data retention on private models. Your conversations stay yours.

Venice is also **uncensored**: no content filters, no refusals, no "I can't help with that." The AI answers what you actually ask, whether that's creative fiction, security research, controversial topics, or anything else mainstream AI platforms won't touch.

**Why agents should care:**

- **🔒 Private inference** — Models marked "Private" have zero data retention. Process sensitive data without it leaking into training sets.
- **🔓 Uncensored responses** — No guardrails blocking legitimate use cases. Generate any content your workflow needs.
- **🔌 OpenAI-compatible API** — Drop-in replacement. Same API format, just change the base URL.
- **📦 30+ models** — From tiny efficient models to Claude Opus 4.6, GPT-5.2, and Venice's own uncensored models.
- **🌐 Built-in web search** — LLMs can search the web and cite sources in a single API call ($10/1K calls).
- **🎨 Image & video generation** — Flux, Sora, Runway, WAN models for visual content *(see [venice-ai-media](https://github.com/PlusOne/venice-ai-media) skill)*.

> ⚠️ **API changes**: If something doesn't work as expected, check [docs.venice.ai](https://docs.venice.ai) — the API specs may have been updated since this skill was written.

## How It Works

```
User prompt → Complexity Classifier → Tier Selection → Venice.ai API
                                          │
              ┌───────────┬───────────┬───┴───────┬───────────┐
            CHEAP      BUDGET       MID        HIGH      PREMIUM
           $0.05/M    $0.15/M    $0.25/M    $0.50/M     $2.19/M
```

The classifier uses heuristic analysis:

- **Length** — longer prompts suggest more complex tasks
- **Keywords** — domain-specific terms signal complexity (e.g., "architecture", "prove", "optimize")
- **Code markers** — code blocks, function names, technical syntax
- **Instruction depth** — multi-step instructions, comparisons
- **Conversational simplicity** — greetings and small talk stay cheap
- **Conversation context** — when given chat history, analyzes the full conversation to maintain appropriate tier
- **Function calling** — tool use auto-bumps to at least mid tier
- **Budget constraints** — progressive tier downgrade as spending approaches daily/session limits

## Model Tiers

| Tier | Models | Input Cost | Best For |
|------|--------|-----------|----------|
| **💚 Cheap** | Venice Small, GPT OSS 120B, GLM 4.7 Flash, Llama 3.2 3B | $0.05–$0.15/M | Simple Q&A, greetings, math |
| **💙 Budget** | Qwen 3 235B, Venice Uncensored, GLM 4.7 Flash Heretic | $0.14–$0.25/M | Summaries, translations |
| **💛 Mid** | DeepSeek V3.2, MiniMax M2.1/M2.5, Llama 3.3 70B | $0.25–$0.70/M | Code generation, analysis |
| **🧡 High** | GLM 5, Kimi K2 Thinking, Grok 4.1 Fast, Gemini 3 Flash | $0.50–$1.00/M | Complex reasoning, code review |
| **💎 Premium** | GPT-5.2, Gemini 3 Pro, Claude Opus/Sonnet 4.5/4.6 | $2.19–$6.00/M | Expert analysis, architecture |

Full model pricing in [references/models.md](references/models.md).

## Requirements

- **Python 3.8+** (no external dependencies — stdlib only)
- **Venice.ai API key** — get one at [venice.ai/settings/api](https://venice.ai/settings/api)
- **OpenClaw** (optional — works standalone too)

## Installation

### Quick Install (OpenClaw)

```bash
git clone git@github.com:PlusOne/venice.ai-router-openclaw.git
cd venice.ai-router-openclaw
chmod +x install.sh
./install.sh
```

The installer auto-detects your OpenClaw workspace and copies the skill files.

Then enable in `~/.openclaw/openclaw.json`:

```json
{
  "env": {
    "VENICE_API_KEY": "your-api-key-here"
  },
  "skills": {
    "entries": {
      "venice-router": {
        "enabled": true
      }
    }
  }
}
```

Restart the gateway or wait for auto-reload (if `skills.load.watch` is enabled).

### Manual Install

Copy the files to your OpenClaw skills directory:

```bash
mkdir -p ~/.openclaw/workspace/skills/venice-router
cp -r SKILL.md scripts/ references/ ~/.openclaw/workspace/skills/venice-router/
```

### Standalone (without OpenClaw)

```bash
export VENICE_API_KEY="your-api-key-here"
python3 scripts/venice-router.py --prompt "Hello world"
```

## Usage

### Via OpenClaw WebChat / Telegram

Type `/venice_router` followed by your prompt:

```
/venice_router What is the capital of France?
```

### CLI — Auto-Routed Prompt

```bash
python3 scripts/venice-router.py --prompt "What is 2+2?"
# → 💚 CHEAP → Venice Small

python3 scripts/venice-router.py --prompt "Write a Python async web scraper with error handling"
# → 💛 MID → DeepSeek V3.2

python3 scripts/venice-router.py --prompt "Design a distributed event-driven microservices architecture"
# → 💎 PREMIUM → Gemini 3 Pro
```

### CLI — Force a Tier

```bash
python3 scripts/venice-router.py --tier mid --prompt "Tell me a joke"
```

### CLI — Stream Output

```bash
python3 scripts/venice-router.py --stream --prompt "Write a poem about lobsters"
```

### CLI — Web Search (LLM searches the web, cites sources)

```bash
python3 scripts/venice-router.py --web-search --prompt "Latest news on AI regulation"
```

### CLI — Uncensored Mode (no content filters, no refusals)

```bash
python3 scripts/venice-router.py --uncensored --prompt "Write edgy creative fiction"
# Auto-bumps to nearest tier with uncensored models (e.g., budget → GLM 4.7 Flash Heretic)
```

### CLI — Private-Only Mode (zero data retention)

```bash
python3 scripts/venice-router.py --private-only --prompt "Analyze this confidential contract"
# Only uses Venice-hosted models — never proxies to OpenAI/Anthropic/Google
```

### CLI — Conversation-Aware Routing (multi-turn)

```bash
# Save conversation as JSON: [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
python3 scripts/venice-router.py --conversation history.json --prompt "Can you add error handling too?"
# Router analyzes full conversation context — trivial follow-ups go cheap, complex code convos stay at mid/high
```

### CLI — Function Calling (tool use)

```bash
# Define tools in OpenAI format: [{"type":"function","function":{"name":"...","parameters":{...}}}]
python3 scripts/venice-router.py --tools tools.json --prompt "What's the weather in NYC?"
python3 scripts/venice-router.py --tools tools.json --tool-choice required --prompt "Look up the stock price"
# Auto-bumps to mid tier minimum — function calling needs capable models
```

### CLI — Thinking / Reasoning Mode

```bash
# Prefer chain-of-thought reasoning models (Qwen3 235B Thinking, Kimi K2 Thinking, Kimi K2.5)
python3 scripts/venice-router.py --thinking --prompt "Prove that the square root of 2 is irrational"
python3 scripts/venice-router.py --thinking --prompt "What is the halting problem and why is it undecidable?"
python3 scripts/venice-router.py --thinking --tier high --prompt "Find the bug in this recursive algorithm"
# Auto-bumps to mid tier minimum — thinking models live in mid/high
# All thinking models are private (zero data retention)
```

Or set persistently:

```bash
export VENICE_THINKING=true   # Always use thinking/reasoning models
```

### CLI — Cost Budget Management

```bash
# Set daily and/or session spending limits
export VENICE_DAILY_BUDGET=2.00    # $2/day max
export VENICE_SESSION_BUDGET=0.50  # $0.50/session max

# View spending breakdown
python3 scripts/venice-router.py --budget-status
python3 scripts/venice-router.py --budget-status --session-id my-project

# Router auto-downgrades tiers as budget is consumed:
# 95% spent → cheap only | 80% → budget max | 60% → mid max | 40% → high max
```

### CLI — Classify Only (No API Call)

```bash
python3 scripts/venice-router.py --classify "Explain quantum entanglement"
# → 💛 MID → DeepSeek V3.2
```

### CLI — List All Models

```bash
python3 scripts/venice-router.py --list-models
```

### CLI — Override Model Directly

```bash
python3 scripts/venice-router.py --model deepseek-v3.2 --prompt "Hello"
```

### CLI — JSON Output

```bash
python3 scripts/venice-router.py --classify "Design a system" --json
```

```json
{
  "classified_tier": "premium",
  "effective_tier": "premium",
  "model_id": "gemini-3-pro-preview",
  "model_name": "Gemini 3 Pro",
  "input_cost_per_1m": 2.5,
  "output_cost_per_1m": 15.0,
  "context_window": 198000,
  "private": false,
  "uncensored": false,
  "prompt_length": 15
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VENICE_API_KEY` | Venice.ai API key **(required)** | — |
| `VENICE_DEFAULT_TIER` | Default tier when classification is ambiguous | `budget` |
| `VENICE_MAX_TIER` | Maximum tier to use (cost cap) | `premium` |
| `VENICE_TEMPERATURE` | Default temperature | `0.7` |
| `VENICE_MAX_TOKENS` | Default max tokens | `4096` |
| `VENICE_STREAM` | Enable streaming by default | `false` |
| `VENICE_UNCENSORED` | Always prefer uncensored models | `false` |
| `VENICE_PRIVATE_ONLY` | Only use private models (zero data retention) | `false` |
| `VENICE_WEB_SEARCH` | Enable web search by default ($10/1K calls) | `false` |
| `VENICE_THINKING` | Always prefer thinking/reasoning models | `false` |
| `VENICE_DAILY_BUDGET` | Max daily spend in USD (0 = unlimited) | `0` |
| `VENICE_SESSION_BUDGET` | Max per-session spend in USD (0 = unlimited) | `0` |

### Cost Control

Cap your spending by setting `VENICE_MAX_TIER`:

```bash
export VENICE_MAX_TIER=mid  # Never use high or premium models
```

Or use budget tracking for progressive tier downgrading:

```bash
export VENICE_DAILY_BUDGET=2.00    # $2/day soft cap
export VENICE_SESSION_BUDGET=0.50  # $0.50/session soft cap
```

Budget tracking stores cost data in `~/.venice-router/costs/` and auto-downgrades tiers as spending approaches limits. Use `--budget-status` to see a breakdown with progress bars.

### Privacy

The router prefers **private** (self-hosted) Venice models over anonymized ones when available at the same tier:

- **🔒 Private** — Venice hosts the model directly, data stays within Venice infrastructure
- **🔀 Anonymized** — request proxied to external provider (OpenAI, Anthropic, Google, xAI) with identity stripped

Use `--prefer-anon` to override this behavior.

## CLI Reference

```
usage: venice-router.py [-h] [--prompt PROMPT]
                        [--tier {cheap,budget,budget-medium,mid,high,premium}]
                        [--model MODEL] [--classify CLASSIFY] [--list-models]
                        [--stream] [--web-search] [--uncensored] [--private-only]
                        [--thinking] [--temperature TEMP] [--max-tokens N]
                        [--system SYSTEM] [--character SLUG] [--prefer-anon] [--json]
                        [--conversation FILE] [--tools FILE] [--tool-choice CHOICE]
                        [--budget-status] [--session-id ID]

Options:
  --prompt, -p         Prompt to send to Venice.ai
  --tier, -t           Force a specific tier (cheap|budget|budget-medium|mid|high|premium)
  --model, -m          Force a specific model ID
  --classify, -c       Classify complexity without calling the API
  --list-models, -l    List all model tiers and pricing
  --stream, -s         Enable streaming output
  --web-search, -w     Enable Venice web search ($10/1K calls)
  --uncensored, -u     Prefer uncensored models (no content filters)
  --private-only       Only use private models (zero data retention)
  --thinking           Prefer thinking/reasoning models (Qwen3 235B Thinking, Kimi K2/K2.5);
                       auto-bumps to mid tier minimum; all thinking models are private
  --temperature        Temperature (0.0–2.0)
  --max-tokens         Max output tokens
  --system             System prompt
  --character          Venice character slug for persona responses
  --prefer-anon        Prefer anonymized over private models
  --json, -j           Output routing info as JSON
  --conversation       JSON file with conversation history for context-aware routing
  --tools              JSON file with tool/function definitions (OpenAI format)
  --tool-choice        Tool choice: "auto", "none", "required", or JSON object
  --budget-status      Show current cost budget usage and exit
  --session-id         Session ID for per-session cost tracking
```

## Project Structure

```
venice.ai-router-openclaw/
├── README.md              ← You are here
├── SKILL.md               ← OpenClaw skill definition (AgentSkills format)
├── install.sh             ← Auto-installer for OpenClaw
├── scripts/
│   ├── venice-router.py   ← Core router engine (Python 3, stdlib only)
│   └── venice-router.sh   ← Bash wrapper
└── references/
    └── models.md          ← Full Venice.ai model pricing reference
```

## License

MIT License — see [LICENSE](LICENSE).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## Links

- [Venice.ai](https://venice.ai) — AI inference platform
- [Venice.ai API Docs](https://docs.venice.ai) — API reference
- [OpenClaw](https://github.com/PlusOne/openclaw) — Personal AI assistant
