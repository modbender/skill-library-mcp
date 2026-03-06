---
name: firm-memory-audit-pack
version: 1.0.0
description: >
  Memory infrastructure audit pack.
  pgvector configuration validation and knowledge graph integrity check. 2 memory tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - memory
  - pgvector
  - knowledge-graph
  - audit
  - infrastructure
---

# firm-memory-audit-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Audits memory infrastructure: validates pgvector extension configuration
(dimensions, index type, distance metric) and knowledge graph integrity
(node connectivity, orphan detection, cycle detection).

## Tools (2)

| Tool | Description |
|------|-------------|
| `openclaw_pgvector_memory_check` | pgvector config validation (dimensions, index, distance) |
| `openclaw_knowledge_graph_check` | Knowledge graph integrity audit |

## Usage

```yaml
skills:
  - firm-memory-audit-pack

# Audit memory infrastructure:
openclaw_pgvector_memory_check config_path=/path/to/config.json
openclaw_knowledge_graph_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
