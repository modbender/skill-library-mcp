---
name: firm-agent-orchestration-pack
version: 1.0.0
description: >
  Multi-agent task orchestration pack.
  DAG-based parallel task execution and team status monitoring. 2 orchestration tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - orchestration
  - agents
  - dag
  - parallel
  - team
---

# firm-agent-orchestration-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Orchestrates multi-agent teams via directed acyclic graph (DAG) task execution.
Supports dependency resolution, parallel execution, and real-time team status monitoring.

## Tools (2)

| Tool | Description |
|------|-------------|
| `openclaw_agent_team_orchestrate` | DAG-based parallel task execution |
| `openclaw_agent_team_status` | Team execution status and progress |

## Usage

```yaml
skills:
  - firm-agent-orchestration-pack

# Orchestrate a multi-agent task:
openclaw_agent_team_orchestrate tasks='[{"id":"1","agent":"cto","task":"review"}]'
openclaw_agent_team_status
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
