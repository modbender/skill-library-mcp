# Personas Skill - Overview

**Status:** Production-ready  
**Version:** 2.2.6

## What this skill contains

- 20 bundled personas in `data/*.md`
- Skill instructions in `SKILL.md`
- User docs in `README.md` and `FAQ.md`
- CLI helper script in `scripts/persona.py`

## What `scripts/persona.py` does

- `--list`: list bundled personas by category
- `--show <name>`: print persona markdown content
- `--activate <name>`: set active persona and print its prompt
- `--current`: show active persona
- `--reset`: clear active persona

State is stored at `~/.openclaw/persona-state.json`.

## Scope clarification

This package provides a fixed bundled persona set and persona switching. It does **not** include a guided custom persona creation feature.

## Persona categories

- Core: 5
- Creative: 2
- Curator: 1
- Learning: 3
- Lifestyle: 3
- Professional: 6
- **Total: 20**