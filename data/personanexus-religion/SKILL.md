---
name: personanexus-religion
description: "Extend AI agent personalities with religion, faith, and spiritual frameworks. Define principles, sacred texts, moral frameworks, traditions, and more."
version: 1.0.0
metadata:
  openclaw:
    emoji: "🕊️"
    homepage: https://github.com/PersonaNexus/personanexus
    requires:
      bins:
        - python3
      anyBins:
        - pip
        - uv
---

# PersonaNexus Religion Skill

Extend AI agent identities with structured religion and spiritual framework
configuration. Builds on the PersonaNexus YAML schema to add faith-based
principles, sacred texts, moral frameworks, traditions, and more.

## What This Skill Does

- **Define** agent religion/faith configuration via YAML
- **Compile** religion context into system prompts alongside personality traits
- **Validate** religion configuration with semantic warnings
- **Export** to OpenClaw personality.json, SOUL.md, Anthropic XML, and more

## Setup

Install dependencies:

```bash
pip install pydantic pyyaml typer rich
```

## Usage

### 1. Create an Agent with Religion

Start from a template:

- `templates/religion-minimal.yaml` -- Simple: enabled + influence + principles
- `templates/religion-full.yaml` -- All fields: tradition, denomination, sacred texts, moral framework, traditions, dietary rules, holy days, prayer schedule

### 2. Validate

```python
from religion_skill import IdentityValidator

validator = IdentityValidator()
result = validator.validate_file("my-agent.yaml")
print(result.valid, result.errors, result.warnings)
```

### 3. Compile to a System Prompt

```python
from religion_skill import parse_identity_file, compile_identity

identity = parse_identity_file("my-agent.yaml")
prompt = compile_identity(identity, target="text")
print(prompt)
```

### 4. Quick build_persona Helper

```python
from religion_skill.religion import build_persona

prompt = build_persona("my-agent.yaml")
# Includes religion principles in the prompt when enabled
```

## CLI

```bash
python -m religion_skill --help
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `validate FILE` | Parse and validate a YAML identity file |
| `compile FILE --target TARGET` | Compile identity to a system prompt |
| `init NAME --type TYPE` | Scaffold a new agent identity YAML |
| `religion show FILE` | Display the religion config from a YAML file |
| `personality ocean-to-traits` | Map OCEAN scores to personality traits |
| `personality disc-to-traits` | Map DISC scores to personality traits |
| `personality jungian-to-traits` | Map Jungian scores to personality traits |
| `personality list-disc-presets` | Show available DISC presets |
| `personality list-jungian-presets` | Show available Jungian 16-type presets |

### CLI Examples

```bash
# Validate an identity with religion
python -m religion_skill validate templates/religion-full.yaml --verbose

# Compile to text prompt (religion section visible)
python -m religion_skill compile templates/religion-full.yaml --target text

# Compile to OpenClaw personality.json (religion key in output)
python -m religion_skill compile templates/religion-full.yaml --target openclaw --output personality.json

# Show religion configuration
python -m religion_skill religion show templates/religion-full.yaml

# Scaffold a new agent
python -m religion_skill init "My Agent"
```

## Religion YAML Schema

```yaml
religion:
  enabled: true                          # Enable religion (default: false)
  tradition_name: "Christianity"         # Faith tradition
  denomination: "Benedictine"            # Specific denomination or sect
  influence: "strong"                    # subtle | moderate | strong | central

  principles:                            # Core guiding principles
    - "Love your neighbor"
    - "Seek justice, love mercy"

  sacred_texts:
    - name: "The Bible"
      description: "Primary scripture"
      authority_level: "canonical"        # canonical | authoritative | inspirational

  moral_framework:
    name: "Virtue ethics"
    description: "Rooted in classical virtues"
    principles:
      - "Humility as foundation"
      - "Moderation in all things"
    decision_weight: 0.8                  # 0-1, how heavily to weigh in decisions

  traditions:
    - name: "Lectio Divina"
      description: "Contemplative reading"
      behavioral_impact: "Encourages slow, reflective analysis"

  dietary_rules:
    - rule: "Simple, moderate meals"
      strictness: "moderate"              # strict | moderate | flexible
      exceptions: ["health needs"]

  holy_days:
    - name: "Easter"
      description: "Celebration of the Resurrection"
      observance: "prayer and celebration"
      period: "annual"                    # annual | weekly | monthly

  prayer_schedule:
    enabled: true
    frequency: "3x daily"
    description: "Morning, midday, and evening prayer"

  notes: "Additional context about the agent's faith"
```

## Compile Targets

| Target | Output Format |
|--------|---------------|
| `text` | Plain text system prompt with religion section |
| `anthropic` | Claude-optimized with XML sections |
| `openai` | GPT-optimized plain text |
| `openclaw` | personality.json dict with religion key |
| `soul` | SOUL.md + STYLE.md with faith section |
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
