---
name: personanexus
description: "Build structured AI agent personalities using OCEAN, DISC, and Jungian frameworks. Define traits, communication styles, guardrails, and compile to system prompts."
version: 1.0.0
metadata:
  openclaw:
    emoji: "🧬"
    homepage: https://github.com/PersonaNexus/personanexus
    requires:
      bins:
        - python3
      anyBins:
        - pip
        - uv
---

# PersonaNexus -- AI Agent Identity Skill

PersonaNexus lets you define structured AI agent identities using YAML and
business-grade personality frameworks (OCEAN Big Five, DISC, Jungian 16-type).

## What This Skill Does

- **Define** agent personalities using 10 canonical traits (warmth, directness, rigor, etc.)
- **Map** between OCEAN, DISC, and Jungian frameworks automatically
- **Compile** identity specs into system prompts for any LLM platform
- **Validate** identity files against a strict Pydantic schema

## Setup

Install the skill's Python dependencies:

```bash
pip install pydantic pyyaml typer rich
```

Or if using uv:

```bash
uv pip install pydantic pyyaml typer rich
```

## Usage

### 1. Create an Agent Identity

Copy a template from `templates/` and customize it:

- `templates/minimal.yaml` -- Start here (simplest possible agent)
- `templates/full.yaml` -- All sections filled out
- `templates/ocean-example.yaml` -- Using OCEAN Big Five framework
- `templates/disc-example.yaml` -- Using DISC personality framework
- `templates/jungian-example.yaml` -- Using Jungian 16-type framework

### 2. Validate the Identity

```python
from personanexus_skill import IdentityValidator

validator = IdentityValidator()
result = validator.validate_file("my-agent.yaml")
print(result.valid, result.errors, result.warnings)
```

### 3. Compile to a System Prompt

```python
from personanexus_skill import parse_identity_file, compile_identity

identity = parse_identity_file("my-agent.yaml")
prompt = compile_identity(identity, target="text")
# Targets: "text", "anthropic", "openai", "openclaw", "soul", "json", "markdown"
print(prompt)
```

### 4. Use Personality Frameworks

```python
from personanexus_skill import (
    ocean_to_traits, disc_to_traits, jungian_to_traits,
    get_disc_preset, get_jungian_preset,
)

# Get a DISC preset and convert to PersonaNexus traits
disc = get_disc_preset("the_analyst")
traits = disc_to_traits(disc)

# Get a Jungian preset
jungian = get_jungian_preset("intj")
traits = jungian_to_traits(jungian)
```

## CLI

The skill includes a CLI for common operations:

```bash
python -m personanexus_skill --help
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `validate FILE` | Parse and validate a YAML identity file |
| `compile FILE --target TARGET` | Compile identity to a system prompt |
| `init NAME --type TYPE` | Scaffold a new agent identity YAML |
| `personality ocean-to-traits` | Map OCEAN scores to personality traits |
| `personality disc-to-traits` | Map DISC scores to personality traits |
| `personality jungian-to-traits` | Map Jungian scores to personality traits |
| `personality list-disc-presets` | Show available DISC presets |
| `personality list-jungian-presets` | Show available Jungian 16-type presets |

### CLI Examples

```bash
# Validate an identity file
python -m personanexus_skill validate my-agent.yaml --verbose

# Compile to Anthropic system prompt
python -m personanexus_skill compile my-agent.yaml --target anthropic --output prompt.md

# Compile to OpenClaw personality.json
python -m personanexus_skill compile my-agent.yaml --target openclaw --output personality.json

# Scaffold a new minimal agent
python -m personanexus_skill init "My Agent"
python -m personanexus_skill init "My Agent" --type full --output-dir ./agents

# Personality framework tools
python -m personanexus_skill personality disc-to-traits --preset the_analyst
python -m personanexus_skill personality jungian-to-traits --preset intj
python -m personanexus_skill personality ocean-to-traits \
  --openness 0.8 --conscientiousness 0.7 --extraversion 0.4 \
  --agreeableness 0.6 --neuroticism 0.3
python -m personanexus_skill personality list-disc-presets
python -m personanexus_skill personality list-jungian-presets
```

## The 10 Canonical Traits

| Trait | Range | Description |
|-------|-------|-------------|
| warmth | 0-1 | Social warmth vs reserved |
| verbosity | 0-1 | Detailed vs concise |
| assertiveness | 0-1 | Proactive vs reactive |
| humor | 0-1 | Playful vs serious |
| empathy | 0-1 | Emotionally attuned vs task-focused |
| directness | 0-1 | Blunt vs diplomatic |
| rigor | 0-1 | Meticulous vs flexible |
| creativity | 0-1 | Innovative vs conventional |
| epistemic_humility | 0-1 | Aware of uncertainty vs confident |
| patience | 0-1 | Patient vs efficient |

## Compile Targets

| Target | Output Format |
|--------|---------------|
| `text` | Plain text system prompt (default) |
| `anthropic` | Claude-optimized with XML sections |
| `openai` | GPT-optimized plain text |
| `openclaw` | personality.json dict |
| `soul` | SOUL.md + STYLE.md dict |
| `json` | Full identity + metadata |
| `markdown` | Formatted Markdown document |

## Minimal YAML Example

```yaml
schema_version: "1.0"

metadata:
  id: "agt_my_agent_001"
  name: "My Agent"
  version: "1.0.0"
  description: "A helpful assistant"
  created_at: "2026-01-01T00:00:00Z"
  updated_at: "2026-01-01T00:00:00Z"
  status: "active"

role:
  title: "Assistant"
  purpose: "Help users with their tasks"
  scope:
    primary: ["general assistance"]

personality:
  traits:
    warmth: 0.7
    directness: 0.6
    rigor: 0.5

communication:
  tone:
    default: "professional and friendly"

principles:
  - id: "be_helpful"
    priority: 1
    statement: "Always prioritize being genuinely helpful"

guardrails:
  hard:
    - id: "no_harmful_content"
      rule: "Never generate harmful content"
      enforcement: "output_filter"
      severity: "critical"
```

## External Endpoints

This skill does not make any network requests. All processing is local.

## Security & Privacy

No data leaves your machine. PersonaNexus operates entirely on local YAML files.
Identity files should not contain secrets or API keys.

## Learn More

Full documentation, advanced features (inheritance, mixins, teams, drift detection),
and the web UI are available in the main PersonaNexus repository:

https://github.com/PersonaNexus/personanexus
