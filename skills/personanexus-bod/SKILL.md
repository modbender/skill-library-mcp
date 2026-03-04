---
name: personanexus-board
description: "Add a Historical Figures Advisory Board to AI agent personalities. 10 pre-configured personas inspired by public-domain historical figures for strategic advice."
version: 1.0.0
metadata:
  openclaw:
    emoji: "crown"
    homepage: https://github.com/PersonaNexus/personanexus
    requires:
      bins:
        - python3
      anyBins:
        - pip
        - uv
---

# PersonaNexus Board of Directors Skill

Extend AI agent identities with a structured Board of Directors advisory panel
composed of historical figures. Builds on the PersonaNexus YAML schema to add
board members, engagement rules, and strategic advisory capabilities.

## What This Skill Does

- **Define** agent advisory board configuration via YAML
- **Compile** board context into system prompts alongside personality traits
- **Validate** board configuration with semantic warnings
- **Export** to OpenClaw personality.json, SOUL.md, Anthropic XML, and more
- **Pre-configured** 10 historical figures ready to use

## Setup

Install dependencies:

```bash
pip install pydantic pyyaml typer rich
```

## Usage

### 1. Create an Agent with a Board

Start from a template:

- `templates/board-minimal.yaml` -- Simple: enabled + 2 members + basic engagement
- `templates/board-full.yaml` -- All fields: 10 historical figures, full engagement rules, disclaimer

### 2. Validate

```python
from board_skill import IdentityValidator

validator = IdentityValidator()
result = validator.validate_file("my-agent.yaml")
print(result.valid, result.errors, result.warnings)
```

### 3. Compile to a System Prompt

```python
from board_skill import parse_identity_file, compile_identity

identity = parse_identity_file("my-agent.yaml")
prompt = compile_identity(identity, target="text")
print(prompt)
```

### 4. Quick build_persona Helper

```python
from board_skill.board import build_persona

prompt = build_persona("my-agent.yaml")
# Includes board members in the prompt when enabled
```

## CLI

```bash
python -m board_skill --help
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `validate FILE` | Parse and validate a YAML identity file |
| `compile FILE --target TARGET` | Compile identity to a system prompt |
| `init NAME --type TYPE` | Scaffold a new agent identity YAML |
| `board show FILE` | Display the board config from a YAML file |
| `board list-members FILE` | List all board members with personality details |
| `personality ocean-to-traits` | Map OCEAN scores to personality traits |
| `personality disc-to-traits` | Map DISC scores to personality traits |
| `personality jungian-to-traits` | Map Jungian scores to personality traits |
| `personality list-disc-presets` | Show available DISC presets |
| `personality list-jungian-presets` | Show available Jungian 16-type presets |

### CLI Examples

```bash
# Validate an identity with board
python -m board_skill validate templates/board-full.yaml --verbose

# Compile to text prompt (board section visible)
python -m board_skill compile templates/board-full.yaml --target text

# Compile to OpenClaw personality.json (board key in output)
python -m board_skill compile templates/board-full.yaml --target openclaw --output personality.json

# Show board configuration
python -m board_skill board show templates/board-full.yaml

# List board members with details
python -m board_skill board list-members templates/board-full.yaml

# Scaffold a new agent
python -m board_skill init "My Agent"
```

## Board YAML Schema

```yaml
board:
  enabled: true                          # Enable board (default: false)
  disclaimer: "These are fictional..."   # Required disclaimer text

  board_members:
    - id: "sun_tzu"
      name: "Sun Tzu"
      historical_figure: "Sun Tzu"
      died: "~496 BC"
      board_role: "Chief Strategist"
      core_mindset: "Win without fighting"
      modern_relevance: "Competitive strategy"
      personality:
        ocean:
          openness: 0.9
          conscientiousness: 0.95
          extraversion: 0.4
          agreeableness: 0.3
          neuroticism: 0.2
        disc_style: "dominance"          # dominance | influence | steadiness | compliance
        jungian_type: "INTJ"
      key_quote: "The supreme art of war is to subdue the enemy without fighting"

  engagement_rules:
    - "Each member responds from their historical lens"
    - "Synthesize consensus or majority vote"
```

## Compile Targets

| Target | Output Format |
|--------|---------------|
| `text` | Plain text system prompt with board section |
| `anthropic` | Claude-optimized with XML sections |
| `openai` | GPT-optimized plain text |
| `openclaw` | personality.json dict with board key |
| `soul` | SOUL.md + STYLE.md with advisory section |
| `json` | Full identity + metadata |
| `markdown` | Formatted Markdown document |

## External Endpoints

This skill does not make any network requests. All processing is local.

## Security & Privacy

No data leaves your machine. PersonaNexus operates entirely on local YAML files.
Identity files should not contain secrets or API keys.

## Learn More

Full documentation and the main PersonaNexus framework:

https://github.com/PersonaNexus/personanexus
