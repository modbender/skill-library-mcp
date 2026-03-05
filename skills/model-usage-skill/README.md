# Model Usage Skill for OpenClaw

Track AI model costs from CodexBar CLI — per-model breakdowns for Codex or Claude.

## Features

- 📊 **Per-model cost tracking** — See exactly which models cost you the most
- 💰 **30-day summaries** — Track spend over time
- 🔍 **Current vs All** — Check latest session or full history
- 📈 **JSON/Text output** — Scriptable or human-readable

## Quick Start

```bash
# Current model (most recent day)
python scripts/model_usage.py --provider codex --mode current

# All models (full breakdown)
python scripts/model_usage.py --provider claude --mode all

# JSON output for scripting
python scripts/model_usage.py --provider claude --mode all --format json --pretty
```

## Requirements

- CodexBar CLI installed (`brew install steipete/tap/codexbar`)
- Python 3.8+

## Configuration

No config needed — reads from CodexBar's local cost logs automatically.

## Output Example

```
Provider: codex
Models:
- gpt-5.2: $13.08

Provider: claude
Models:
- claude-opus-4-5: $53.47
- claude-sonnet-4-5: $2.81
- claude-haiku-4-5: $0.20
```

## Use Cases

- Track which AI models are burning through your budget
- Generate usage reports
- Identify cost spikes
- Optimize model selection

## License

MIT
