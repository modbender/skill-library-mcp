# personanexus-board-skill

**PersonaNexus Board Skill**: Extend AI agent personalities with a Board of
Directors advisory panel featuring 10 pre-configured historical figures.

This skill builds on the [PersonaNexus](https://github.com/PersonaNexus/personanexus)
framework, adding a `board` section to agent identity YAML files that lets you
define board members, engagement rules, disclaimers, and advisory capabilities.

## Install

```bash
pip install pydantic pyyaml typer rich
```

## Quick Start

### Python API

```python
from board_skill import parse_identity_file, compile_identity, build_persona

# Full compilation pipeline
identity = parse_identity_file("templates/board-full.yaml")
prompt = compile_identity(identity, target="text")
print(prompt)

# Quick build_persona helper
prompt = build_persona("templates/board-minimal.yaml")
print(prompt)
```

### CLI

```bash
python -m board_skill validate templates/board-full.yaml
python -m board_skill compile templates/board-full.yaml --target text
python -m board_skill compile templates/board-full.yaml --target openclaw --output personality.json
python -m board_skill board show templates/board-full.yaml
python -m board_skill board list-members templates/board-full.yaml
```

Run `python -m board_skill --help` for all available commands.

## Full Framework

For advanced features (inheritance, mixins, teams, drift detection,
linting, web UI, and more), see the full PersonaNexus repository:

https://github.com/PersonaNexus/personanexus
