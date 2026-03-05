---
name: skills-compat
displayName: Skills Compatibility Layer
description: Ensures OpenClaw skills.md format works with both nanobot and overstory. Loads skills, registers tools, maps between systems.
version: 1.0.0
---

# Skills Compatibility Layer

## Description

Ensures the OpenClaw SKILL.md format works seamlessly across nanobot, overstory, and Ollama. Discovers and loads skills, parses frontmatter, builds a unified tool registry, and exports tool definitions in each system's native format.

## Architecture

```
┌─────────────────┐      ┌───────────────┐
│  skill_loader.py │─────▶│ SkillLoader   │──▶ Parses SKILL.md + _meta.json
└─────────────────┘      └───────────────┘
         │
         ▼
┌─────────────────┐      ┌───────────────┐
│ tool_registry.py │─────▶│ ToolRegistry  │──▶ Unified tool catalog
└─────────────────┘      └───────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
               nanobot      overstory     Ollama
               format       format       format
```

- **skill_loader.py** — Discovers skills directories, parses YAML frontmatter from SKILL.md files, extracts tool definitions from `_meta.json`, returns structured `SkillDefinition` objects.
- **tool_registry.py** — Singleton tool registry. Registers tools from skills, MCP servers, or manual definitions. Exports the full catalog in nanobot, overstory, or Ollama JSON-schema format.

## Requirements

- Python 3.9+
- No external dependencies (stdlib only — uses `json`, `sqlite3`, `pathlib`, `re` for YAML-subset parsing)

## Commands

### Discover skills

```bash
python3 scripts/skill_loader.py discover --dir /path/to/skills --json
```

### Load a single skill

```bash
python3 scripts/skill_loader.py load --skill /path/to/skills/agent-swarm --json
```

### List registered tools

```bash
python3 scripts/tool_registry.py list --json
python3 scripts/tool_registry.py list --capability code --json
```

### Export tool definitions

```bash
python3 scripts/tool_registry.py export --format nanobot
python3 scripts/tool_registry.py export --format overstory
python3 scripts/tool_registry.py export --format ollama
```

### Register tools from a skill

```bash
python3 scripts/tool_registry.py register --skill agent-swarm --dir /path/to/skills
```

## Usage as Python Module

```python
from skill_loader import SkillLoader
from tool_registry import ToolRegistry

loader = SkillLoader()
loader.load_all("/path/to/skills")

skill = loader.get_skill("agent-swarm")
print(skill.name, skill.version, skill.tools)

registry = ToolRegistry.instance()
registry.register_skill_tools("agent-swarm", "/path/to/skills")

for tool in registry.list_tools():
    print(tool["name"], tool["skill"])

nanobot_tools = registry.export_for_nanobot()
overstory_tools = registry.export_for_overstory()
ollama_tools = registry.export_for_ollama()
```

## Skill Definition Format

Skills are discovered by looking for directories containing a `SKILL.md` file. The frontmatter block (between `---` delimiters) is parsed as key-value pairs:

```yaml
---
name: my-skill
displayName: My Skill
description: What this skill does
version: 1.0.0
---
```

If a `_meta.json` file exists alongside `SKILL.md`, tool names and additional metadata are extracted from it.

## Export Formats

### nanobot

```json
[{"name": "tool_name", "skill": "skill-name", "description": "...", "parameters": {...}}]
```

### overstory

```json
[{"tool": "tool_name", "source_skill": "skill-name", "description": "...", "input_schema": {...}}]
```

### Ollama

```json
[{"type": "function", "function": {"name": "tool_name", "description": "...", "parameters": {...}}}]
```
