# personanexus-religion-skill

**PersonaNexus Religion Skill**: Extend AI agent personalities with
religion, faith, and spiritual framework configurations.

This skill builds on the [PersonaNexus](https://github.com/PersonaNexus/personanexus)
framework, adding a `religion` section to agent identity YAML files that lets you
define principles, sacred texts, moral frameworks, traditions, dietary rules,
holy days, and prayer schedules.

## Install

```bash
pip install pydantic pyyaml typer rich
```

## Quick Start

### Python API

```python
from religion_skill import parse_identity_file, compile_identity, build_persona

# Full compilation pipeline
identity = parse_identity_file("templates/religion-full.yaml")
prompt = compile_identity(identity, target="text")
print(prompt)

# Quick build_persona helper
prompt = build_persona("templates/religion-minimal.yaml")
print(prompt)
```

### CLI

```bash
python -m religion_skill validate templates/religion-full.yaml
python -m religion_skill compile templates/religion-full.yaml --target text
python -m religion_skill compile templates/religion-full.yaml --target openclaw --output personality.json
python -m religion_skill religion show templates/religion-full.yaml
python -m religion_skill personality disc-to-traits --preset the_analyst
```

Run `python -m religion_skill --help` for all available commands.

## Full Framework

For advanced features (inheritance, mixins, teams, drift detection,
linting, web UI, and more), see the full PersonaNexus repository:

https://github.com/PersonaNexus/personanexus
