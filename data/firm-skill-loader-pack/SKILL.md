---
name: firm-skill-loader-pack
version: 1.0.0
description: >
  Skill lazy loading and search pack.
  On-demand SKILL.md loading and keyword-based skill search. 2 loader tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - skills
  - loader
  - search
  - lazy-loading
  - registry
---

# firm-skill-loader-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Provides lazy loading of SKILL.md files and keyword-based skill search
across the local skills directory. Enables on-demand skill discovery
without pre-loading all skills into memory.

## Tools (2)

| Tool | Description |
|------|-------------|
| `openclaw_skill_lazy_loader` | Lazy-load SKILL.md on demand |
| `openclaw_skill_search` | Keyword-based skill search |

## Usage

```yaml
skills:
  - firm-skill-loader-pack

# Search and load skills:
openclaw_skill_search query="security audit"
openclaw_skill_lazy_loader skill_name=firm-security-audit
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
