---
name: firm-vs-bridge-pack
version: 1.0.0
description: >
  VS Code bridge pack.
  Context push/pull and session linking between VS Code and OpenClaw Gateway. 4 bridge tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - vscode
  - bridge
  - context
  - session
  - ide
---

# firm-vs-bridge-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Bridges VS Code editor context with OpenClaw Gateway. Pushes/pulls context
(selections, files, diagnostics) and links/monitors editor sessions.

## Tools (4)

| Tool | Description |
|------|-------------|
| `vs_context_push` | Push VS Code context to Gateway |
| `vs_context_pull` | Pull context from Gateway to VS Code |
| `vs_session_link` | Link VS Code session to Gateway agent |
| `vs_session_status` | Check VS Code session link status |

## Usage

```yaml
skills:
  - firm-vs-bridge-pack

# Sync context with VS Code:
vs_context_push selection="current file content"
vs_context_pull
vs_session_status
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
- VS Code with OpenClaw extension
